#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Not found: {path.relative_to(ROOT)}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid YAML mapping: {path.relative_to(ROOT)}")
    return data


def missing(value: object) -> bool:
    return value is None or value == "" or value == []


def releases_for_artist(artist_id: str) -> list[dict]:
    items: list[dict] = []
    for path in sorted((ROOT / "releases").glob("*.yaml")):
        data = load_yaml(path)
        if data.get("artist_id") == artist_id:
            items.append(data)
    return items


def print_section(title: str, required_missing: list[str], pending: list[str] | None = None) -> None:
    print(title)
    if required_missing:
        print("  status: BLOCKED")
        print("  missing:")
        for item in required_missing:
            print(f"    - {item}")
    else:
        print("  status: READY")
    if pending:
        print("  pending / non-blocking:")
        for item in pending:
            print(f"    - {item}")
    print()


def check_release(release_id: str) -> None:
    release = load_yaml(ROOT / "releases" / f"{release_id}.yaml")
    artist_id = release.get("artist_id")
    artist = load_yaml(ROOT / "artists" / f"{artist_id}.yaml") if artist_id else {}

    capture_missing: list[str] = []
    for label, value in (
        ("title", release.get("title")),
        ("artist_id", artist_id),
        ("release_type", release.get("release_type")),
        ("tracks", release.get("tracks")),
    ):
        if missing(value):
            capture_missing.append(label)

    pending: list[str] = []
    if missing(release.get("release_date")):
        pending.append("release_date")
    if missing((release.get("identifiers") or {}).get("upc_ean")):
        pending.append("UPC/EAN (usually assigned later)")

    print_section("CAPTURE", capture_missing, pending)

    pitch = ((release.get("promotion") or {}).get("priority_pitch") or {})
    spotify_artist = pitch.get("spotify_artist") or ((artist.get("platforms") or {}).get("spotify_artist_url"))
    pitch_missing: list[str] = []
    for label, value in (
        ("selected_track", pitch.get("selected_track")),
        ("release_summary", pitch.get("release_summary")),
        ("spotify_artist", spotify_artist),
        ("marketing_elements", pitch.get("marketing_elements")),
        ("past_awards_milestones", pitch.get("past_awards_milestones")),
    ):
        if missing(value):
            pitch_missing.append(label)
    print_section("TOO LOST PRIORITY PITCH", pitch_missing)


def check_artist(artist_id: str) -> None:
    artist = load_yaml(ROOT / "artists" / f"{artist_id}.yaml")
    core_missing: list[str] = []
    if missing(artist.get("name")):
        core_missing.append("name")
    print_section("ARTIST CAPTURE", core_missing)

    platforms = artist.get("platforms") or {}
    spotify_url = platforms.get("spotify_artist_url")
    releases = releases_for_artist(artist_id)
    any_upc = any(not missing((release.get("identifiers") or {}).get("upc_ean")) for release in releases)

    claim_missing: list[str] = []
    if missing(spotify_url):
        claim_missing.append("Spotify Artist URL / URI")
    if not any_upc:
        claim_missing.append("UPC/EAN for at least one related release (needed for some pre-release claim flows)")

    assets = artist.get("assets") or {}
    selected_image = (assets.get("artist_image") or {}).get("github_path") if isinstance(assets.get("artist_image"), dict) else None
    pending: list[str] = []
    if missing(selected_image):
        pending.append("official artist image not selected — profile image update must stay skipped")

    print_section("SPOTIFY FOR ARTISTS CLAIM / PROFILE", claim_missing, pending)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check KAZEX Catalog readiness for downstream tasks.")
    sub = parser.add_subparsers(dest="kind", required=True)

    release = sub.add_parser("release")
    release.add_argument("release_id")

    artist = sub.add_parser("artist")
    artist.add_argument("artist_id")

    args = parser.parse_args()
    if args.kind == "release":
        check_release(args.release_id)
    else:
        check_artist(args.artist_id)


if __name__ == "__main__":
    main()
