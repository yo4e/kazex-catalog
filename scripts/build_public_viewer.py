#!/usr/bin/env python3
"""Export public catalog data and adopted lyrics only. No private input option."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'viewer'))
from server import Catalog, PrivateCandidates

FORBIDDEN = re.compile(r'(?i)https?://(?:[^/\s]+\.)?suno\.(?:com|ai)|/Users/|/Volumes/|file://|source_path|selected_version_id|master_audio_verified')


def export(root: Path, destination: Path):
    if destination.exists():
        raise ValueError('Use a new output directory; existing files are never overwritten')
    catalog = Catalog(root, PrivateCandidates(root, None))
    data, tracks = copy.deepcopy(catalog.catalog), copy.deepcopy(catalog.track_details)
    if data['private_available'] or any(t['candidate_count'] for t in tracks.values()):
        raise ValueError('Private data must never be exported')
    destination.mkdir(parents=True)
    (destination / 'data').mkdir()
    (destination / 'assets/media').mkdir(parents=True)
    copied = set()

    def images(value):
        if isinstance(value, dict):
            if 'url' in value and value['url'].startswith('/api/image/'):
                source = catalog.image_files[value['id']]
                target = Path('assets/media') / (value['id'] + source.suffix.lower())
                if target not in copied:
                    shutil.copyfile(source, destination / target)
                    copied.add(target)
                value['url'] = target.as_posix()
            for child in value.values():
                images(child)
        elif isinstance(value, list):
            for child in value:
                images(child)
    images(data)
    for name, value in [('catalog', data), ('tracks', tracks)]:
        (destination / f'data/{name}.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    web = root / 'viewer/web'
    for name in ['app.js', 'style.css']:
        shutil.copyfile(web / name, destination / name)
    html = (web / 'index.html').read_text().replace('<html lang="ja">', '<html lang="ja" data-mode="public">')
    html = html.replace('<head>', '''<head>
  <meta name="referrer" content="no-referrer">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; frame-src https://open.spotify.com; base-uri 'none'; form-action 'none'">''')
    html = html.replace('KAZEX — カタログ確認', 'KazeX Records — カタログ')
    (destination / 'index.html').write_text(html, encoding='utf-8')
    (destination / '.nojekyll').touch()
    result = validate_export(destination)
    result['image_files'] = len(copied)
    return result


def validate_export(directory: Path):
    catalog = json.loads((directory / 'data/catalog.json').read_text())
    tracks = json.loads((directory / 'data/tracks.json').read_text())
    if catalog['private_available'] is not False:
        raise ValueError('Public export cannot enable private candidates')
    adopted = 0
    for track in tracks.values():
        if set(track) != {'key', 'number', 'title', 'isrc', 'status', 'candidate_count', 'spotify_id', 'adopted'}:
            raise ValueError('Unexpected track fields in public export')
        if track['candidate_count'] != 0:
            raise ValueError('Public export cannot contain private candidate counts')
        body = track['adopted']
        if body is not None:
            if track['status'] != 'adopted' or set(body) != {'id', 'label', 'body', 'sha256'}:
                raise ValueError('Only adopted lyric bodies can be exported')
            if hashlib.sha256(body['body'].encode()).hexdigest() != body['sha256']:
                raise ValueError('Adopted body mismatch')
            adopted += 1
    for file in directory.rglob('*'):
        if file.is_symlink():
            raise ValueError('Symlinks are not allowed in the Pages artifact')
        if file.is_file() and file.suffix in {'.html', '.js', '.css', '.json'}:
            if FORBIDDEN.search(file.read_text()):
                raise ValueError('Private source metadata or local paths found in public output')
    if any(t['candidate_count'] for release in catalog['releases'] for t in release['tracks']):
        raise ValueError('Private candidate counts found in catalog')
    return {'artists': len(catalog['artists']), 'releases': len(catalog['releases']),
            'tracks': len(tracks), 'adopted_lyrics': adopted, 'private_candidates': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(ROOT, args.output.resolve())))
