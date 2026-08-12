#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

errors: list[str] = []


def error(path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def load_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        error(path, f"YAML parse error: {exc}")
        return {}
    if not isinstance(data, dict):
        error(path, "top level must be a mapping")
        return {}
    return data


def validate_id(path: Path, data: dict) -> str | None:
    value = data.get("id")
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        error(path, "id must be lowercase kebab-case")
        return None
    if path.stem != value:
        error(path, f"filename must match id ({value}.yaml)")
    return value


def validate_date(path: Path, value: object, field: str) -> None:
    if value is None:
        return
    if isinstance(value, dt.date):
        return
    if isinstance(value, str) and DATE_RE.fullmatch(value):
        try:
            dt.date.fromisoformat(value)
            return
        except ValueError:
            pass
    error(path, f"{field} must be YYYY-MM-DD or null")


def validate_github_path(path: Path, value: object, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not value.startswith("assets/"):
        error(path, f"{field} must be a repository-relative assets/ path or null")
        return
    target = ROOT / value
    if not target.exists():
        error(path, f"{field} points to missing file: {value}")


def validate_asset_dir(path: Path, value: object, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not value.startswith("assets/") or not value.endswith("/"):
        error(path, f"{field} must be an assets/ directory ending in / or null")


def validate_selected_asset(path: Path, block: object, field: str) -> None:
    if block is None:
        return
    if not isinstance(block, dict):
        error(path, f"{field} must be a mapping")
        return
    validate_github_path(path, block.get("github_path"), f"{field}.github_path")


def validate_candidate_assets(path: Path, items: object, field: str) -> None:
    if items is None:
        return
    if not isinstance(items, list):
        error(path, f"{field} must be a list")
        return
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            error(path, f"{field}[{index}] must be a mapping")
            continue
        validate_github_path(path, item.get("github_path"), f"{field}[{index}].github_path")
        status = item.get("status")
        if status not in {"candidate", "selected", "archived"}:
            error(path, f"{field}[{index}].status must be candidate, selected, or archived")


def validate_pitch(path: Path, data: dict) -> None:
    pitch = data.get("promotion", {}).get("priority_pitch", {})
    if not isinstance(pitch, dict):
        error(path, "promotion.priority_pitch must be a mapping")
        return

    for field in ("release_summary", "past_awards_milestones"):
        value = pitch.get(field)
        if value is not None and not isinstance(value, str):
            error(path, f"promotion.priority_pitch.{field} must be text or null")
        elif isinstance(value, str) and len(value) > 500:
            error(path, f"promotion.priority_pitch.{field} exceeds 500 characters ({len(value)})")

    selected_track = pitch.get("selected_track")
    if selected_track is not None:
        track_titles = {
            track.get("title")
            for track in data.get("tracks", [])
            if isinstance(track, dict) and isinstance(track.get("title"), str)
        }
        if selected_track not in track_titles:
            error(path, "promotion.priority_pitch.selected_track must match a track title")


artist_files = sorted((ROOT / "artists").glob("*.yaml"))
release_files = sorted((ROOT / "releases").glob("*.yaml"))

artist_ids: set[str] = set()
for path in artist_files:
    data = load_yaml(path)
    artist_id = validate_id(path, data)
    if artist_id:
        if artist_id in artist_ids:
            error(path, f"duplicate artist id: {artist_id}")
        artist_ids.add(artist_id)

    assets = data.get("assets", {})
    if not isinstance(assets, dict):
        error(path, "assets must be a mapping")
        continue
    validate_asset_dir(path, assets.get("github_asset_dir"), "assets.github_asset_dir")
    validate_selected_asset(path, assets.get("artist_image"), "assets.artist_image")
    validate_selected_asset(path, assets.get("logo"), "assets.logo")
    validate_selected_asset(path, assets.get("epk"), "assets.epk")
    validate_candidate_assets(path, assets.get("artist_photo_candidates", []), "assets.artist_photo_candidates")
    validate_candidate_assets(path, assets.get("concept_art", []), "assets.concept_art")

release_ids: set[str] = set()
for path in release_files:
    data = load_yaml(path)
    release_id = validate_id(path, data)
    if release_id:
        if release_id in release_ids:
            error(path, f"duplicate release id: {release_id}")
        release_ids.add(release_id)

    artist_id = data.get("artist_id")
    if artist_id not in artist_ids:
        error(path, f"artist_id does not exist: {artist_id!r}")

    validate_date(path, data.get("release_date"), "release_date")

    identifiers = data.get("identifiers", {})
    if isinstance(identifiers, dict):
        upc = identifiers.get("upc_ean")
        if upc is not None and not isinstance(upc, str):
            error(path, "identifiers.upc_ean must be a string or null")

    tracks = data.get("tracks", [])
    if not isinstance(tracks, list):
        error(path, "tracks must be a list")
    else:
        for index, track in enumerate(tracks):
            if not isinstance(track, dict):
                error(path, f"tracks[{index}] must be a mapping")
                continue
            isrc = track.get("isrc")
            if isrc is not None and not isinstance(isrc, str):
                error(path, f"tracks[{index}].isrc must be a string or null")

    cover = data.get("cover", {})
    if not isinstance(cover, dict):
        error(path, "cover must be a mapping")
    else:
        validate_github_path(path, cover.get("github_path"), "cover.github_path")

    assets = data.get("assets", {})
    if not isinstance(assets, dict):
        error(path, "assets must be a mapping")
    else:
        validate_asset_dir(path, assets.get("github_asset_dir"), "assets.github_asset_dir")

    validate_pitch(path, data)

if errors:
    print("Catalog validation failed:")
    for item in errors:
        print(f"- {item}")
    sys.exit(1)

print(f"Catalog validation passed: {len(artist_files)} artists, {len(release_files)} releases")
