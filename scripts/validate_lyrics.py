"""Check the adopted-lyrics export; private source records are kept outside Git."""
from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
import re

import yaml

SOURCE_URL = re.compile(r"(?i)(?:https?://)?(?:[a-z0-9-]+\.)?suno\.(?:com|ai)(?:[/\\?\s\"']|$)")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def validate_lyrics(root: Path, release_files: list[Path]) -> list[str]:
    errors: list[str] = []
    indexes: set[Path] = set()
    bodies: set[Path] = set()
    counts = dict(adopted_tracks=0, pending_selection_tracks=0, not_collected_tracks=0)

    def error(path: Path, message: str) -> None:
        errors.append(f"{path.relative_to(root)}: {message}")

    def load(path: Path) -> dict:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("expected a mapping")
            return data
        except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
            error(path, f"cannot read YAML mapping: {exc}")
            return {}

    def fields(path: Path, data: dict, expected: set[str]) -> None:
        if set(data) != expected:
            error(path, "unexpected or missing fields; source/variant metadata belongs outside the public catalog")

    for release_path in release_files:
        release = load(release_path)
        lyrics = release.get("lyrics", {})
        if not isinstance(lyrics, dict):
            error(release_path, "lyrics must be a mapping")
            continue
        ref = lyrics.get("index_path")
        if ref is None:
            continue
        rid = release_path.stem
        if ref != f"lyrics/{rid}/index.yaml":
            error(release_path, "lyrics.index_path must name this release's index")
            continue
        path = root / ref
        indexes.add(path)
        index = load(path)
        fields(path, index, {'schema_version', 'release_id', 'tracks'})
        if index.get('schema_version') != 2 or index.get('release_id') != rid:
            error(path, 'schema_version or release_id mismatch')
        tracks = index.get('tracks')
        catalog = release.get('tracks')
        if not isinstance(tracks, list) or not isinstance(catalog, list):
            error(path, 'tracks must be a list')
            continue
        actual = [t.get('isrc') for t in tracks if isinstance(t, dict)]
        expected = [t.get('isrc') for t in catalog if isinstance(t, dict)]
        if (actual != expected or len(actual) != len(tracks)
                or any(not isinstance(x, str) for x in actual)
                or len(set(str(x) for x in actual)) != len(actual)):
            error(path, 'track ISRCs must match the release exactly once and in catalog order')
        for track in tracks:
            if not isinstance(track, dict):
                continue
            fields(path, track, {'isrc', 'status', 'text_path', 'sha256', 'adoption'})
            isrc, status = track.get('isrc'), track.get('status')
            if not isinstance(isrc, str):
                continue
            if status not in {'adopted', 'pending_selection', 'not_collected', 'no_lyrics'}:
                error(path, f'{isrc}: invalid status')
                continue
            counts[status + '_tracks'] = counts.get(status + '_tracks', 0) + 1
            if status == 'no_lyrics' and lyrics.get('has_lyrics') is not False:
                error(path, f'{isrc}: no_lyrics requires release lyrics.has_lyrics=false')
            if lyrics.get('has_lyrics') is False and status != 'no_lyrics':
                error(path, f'{isrc}: release declares no lyrics but index status differs')
            if status != 'adopted':
                if any(track.get(k) is not None for k in ('text_path', 'sha256', 'adoption')):
                    error(path, f'{isrc}: unadopted or uncollected tracks must not expose text or adoption metadata')
                continue
            adoption = track.get('adoption')
            if not isinstance(adoption, dict):
                error(path, f'{isrc}: adopted lyrics need an adoption record')
            else:
                fields(path, adoption, {'basis', 'verified_on'})
                if adoption.get('basis') not in {'completed_submission_record', 'owner_confirmation'}:
                    error(path, f'{isrc}: invalid adoption basis')
                try:
                    dt.date.fromisoformat(adoption.get('verified_on'))
                except (TypeError, ValueError):
                    error(path, f'{isrc}: verified_on must be an ISO date string')
            ref = track.get('text_path')
            if ref != f'lyrics/{rid}/{isrc.lower()}.txt':
                error(path, f'{isrc}: text_path must match release and ISRC')
                continue
            target = root / ref
            if not target.resolve().is_relative_to((root / 'lyrics').resolve()):
                error(path, f'{isrc}: body path escapes lyrics directory')
                continue
            bodies.add(target)
            if not isinstance(track.get('sha256'), str) or not SHA256.fullmatch(track['sha256']):
                error(path, f'{isrc}: invalid SHA256')
            try:
                content = target.read_bytes()
                if not content.decode('utf-8').strip():
                    error(path, f'{isrc}: empty lyrics')
                if hashlib.sha256(content).hexdigest() != track.get('sha256'):
                    error(path, f'{isrc}: body SHA256 mismatch')
            except (OSError, UnicodeError) as exc:
                error(path, f'{isrc}: unreadable UTF-8 body: {exc}')

    directory = root / 'lyrics'
    for path in directory.glob('*/index.yaml'):
        if path not in indexes:
            error(path, 'index is not referenced by a release')
    allowed = indexes | bodies | {directory / 'README.md', directory / 'collection.yaml'}
    for path in directory.rglob('*'):
        if path.is_file() and path not in allowed:
            error(path, 'unexpected file: only indexed adopted bodies and public indexes are allowed')
    if indexes:
        path = directory / 'collection.yaml'
        collection = load(path)
        fields(path, collection, {'schema_version', 'publication_scope', 'counts'})
        if collection.get('schema_version') != 2 or collection.get('publication_scope') != 'adopted_lyrics_only':
            error(path, 'collection must use adopted_lyrics_only schema version 2')
        if collection.get('counts') != counts:
            error(path, f'counts do not match indexes: {counts}')

    # Data and documentation are scanned without printing the matched private URL.
    for path in root.rglob('*'):
        if '.git' in path.relative_to(root).parts or not path.is_file():
            continue
        if path.suffix.lower() in {'.yaml', '.yml', '.json', '.md', '.txt'}:
            try:
                text = path.read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                continue
            if SOURCE_URL.search(text):
                error(path, 'source-service URL is not allowed in public data or documentation')
    return errors
