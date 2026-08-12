#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO = "yo4e/kazex-catalog"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Not found: {path.relative_to(ROOT)}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid YAML mapping: {path.relative_to(ROOT)}")
    return data


def clean(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return str(value)


def show(value: object, missing: str = "MISSING") -> str:
    text = clean(value)
    return text if text is not None else missing


def raw_url(path: object) -> str | None:
    value = clean(path)
    if not value:
        return None
    return RAW_BASE + value.replace(" ", "%20")


def block(title: str, value: object) -> str:
    return f"{title}\n{show(value)}"


def find_releases_for_artist(artist_id: str) -> list[dict]:
    releases: list[dict] = []
    for path in sorted((ROOT / "releases").glob("*.yaml")):
        data = load_yaml(path)
        if data.get("artist_id") == artist_id:
            releases.append(data)
    releases.sort(key=lambda item: str(item.get("release_date") or "9999-99-99"))
    return releases


def render_priority_pitch(release_id: str) -> str:
    release = load_yaml(ROOT / "releases" / f"{release_id}.yaml")
    artist_id = show(release.get("artist_id"))
    artist = load_yaml(ROOT / "artists" / f"{artist_id}.yaml")

    promotion = release.get("promotion") or {}
    pitch = promotion.get("priority_pitch") or {}
    social = pitch.get("social") or {}
    attachments = pitch.get("attachments") or {}

    required = {
        "Selected Track": pitch.get("selected_track"),
        "Release Summary": pitch.get("release_summary"),
        "Spotify Artist": pitch.get("spotify_artist") or (artist.get("platforms") or {}).get("spotify_artist_url"),
        "Marketing Elements": pitch.get("marketing_elements"),
        "Past Awards / Milestones": pitch.get("past_awards_milestones"),
    }

    missing: list[str] = []
    for label, value in required.items():
        if value is None or value == "" or value == []:
            missing.append(label)

    marketing = pitch.get("marketing_elements") or []
    marketing_text = "\n".join(f"- {item}" for item in marketing) if marketing else "MISSING"

    cover_path = (release.get("cover") or {}).get("github_path")
    image_hint = attachments.get("image_url") or raw_url(cover_path)
    epk_hint = attachments.get("epk_url") or ((artist.get("assets") or {}).get("epk") or {}).get("web_url")

    readiness = "READY FOR FORM ENTRY" if not missing else "BLOCKED — DO NOT SUBMIT"
    missing_text = ", ".join(missing) if missing else "none"

    lines = [
        "# Browser Task Packet — Too Lost Priority Pitch",
        "",
        "あなたはブラウザ操作担当です。Too Lost の Priority Pitch Portal で、下記のカタログ正本に従って対象リリースのフォーム入力を進めてください。",
        "",
        "## Safety / execution rules",
        "- カタログにない実績・数字・広告・プレス・ツアー・SNS・Spotify情報を推測で補わない。",
        "- REQUIRED が MISSING の場合は、その項目を勝手に作らず、入力可能なところまで進めて停止し、不足項目を報告する。",
        "- REQUIRED がすべて揃うまで最終Submitは押さない。",
        "- 同じリリースを重複Pitchしない。すでに提出済み表示がある場合は何も送信せず報告する。",
        "- 代表曲は1曲だけ。",
        "- 添付がURLから直接扱えずローカルファイル選択が必要なら、必要なrepo pathを報告して停止する。",
        "",
        "## Readiness",
        readiness,
        f"Missing required fields: {missing_text}",
        "",
        "## Target release",
        f"Artist: {show(artist.get('name'))}",
        f"Release: {show(release.get('title'))}",
        f"Release date: {show(release.get('release_date'))}",
        f"UPC/EAN: {show((release.get('identifiers') or {}).get('upc_ean'))}",
        "",
        "## Form values",
        block("Selected Track", pitch.get("selected_track")),
        "",
        block("Release Summary — max 500 characters", pitch.get("release_summary")),
        "",
        block("Spotify Artist", required["Spotify Artist"]),
        "",
        "Marketing Elements",
        marketing_text,
        "",
        block("Past Awards / Milestones — max 500 characters", pitch.get("past_awards_milestones")),
        "",
        "## Optional fields",
        f"Upcoming Tour Dates: {show(pitch.get('upcoming_tour_dates'), 'leave blank')}",
        f"Facebook: {show(social.get('facebook'), 'leave blank')}",
        f"Instagram: {show(social.get('instagram'), 'leave blank')}",
        f"Twitter/X: {show(social.get('x'), 'leave blank')}",
        f"TikTok: {show(social.get('tiktok'), 'leave blank')}",
        f"Image candidate: {show(image_hint, 'none')}",
        f"Image repo path: {show(cover_path, 'none')}",
        f"EPK: {show(epk_hint, 'none')}",
        "",
        "## Completion report",
        "最後に、入力済み項目・未入力項目・Submitしたかどうか・ブラウザ上で新たに判明した必須項目や仕様を箇条書きで報告してください。",
    ]
    return "\n".join(lines)


def render_spotify_profile(artist_id: str) -> str:
    artist = load_yaml(ROOT / "artists" / f"{artist_id}.yaml")
    releases = find_releases_for_artist(artist_id)
    platforms = artist.get("platforms") or {}
    social = artist.get("social") or {}
    assets = artist.get("assets") or {}
    selected_image = assets.get("artist_image") or {}
    candidates = assets.get("artist_photo_candidates") or []

    spotify_url = platforms.get("spotify_artist_url")
    mode = "UPDATE EXISTING PROFILE" if clean(spotify_url) else "CLAIM / SET UP ACCESS"

    release_lines: list[str] = []
    for release in releases:
        release_lines.append(
            f"- {show(release.get('title'))} | date: {show(release.get('release_date'))} | "
            f"UPC/EAN: {show((release.get('identifiers') or {}).get('upc_ean'))}"
        )
    if not release_lines:
        release_lines = ["- none registered"]

    selected_path = selected_image.get("github_path") if isinstance(selected_image, dict) else None
    selected_url = selected_image.get("web_url") if isinstance(selected_image, dict) else None
    selected_asset = selected_url or raw_url(selected_path)

    candidate_lines: list[str] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        path = item.get("github_path")
        candidate_lines.append(
            f"- role={show(item.get('role'), 'unspecified')} | status={show(item.get('status'))} | "
            f"path={show(path)} | raw={show(raw_url(path))}"
        )
    if not candidate_lines:
        candidate_lines = ["- none"]

    description = artist.get("description") or {}
    genres = artist.get("genres") or []
    genre_text = ", ".join(str(item) for item in genres) if genres else "none registered"

    lines = [
        "# Browser Task Packet — Spotify for Artists",
        "",
        "あなたはブラウザ操作担当です。Spotify for Artistsで、下記のKAZEX Catalog正本に従ってアーティストページのclaimまたはプロフィール整備を進めてください。",
        "",
        "## Safety / execution rules",
        "- アーティスト名、URL、実績、SNS、リリース情報を推測で補わない。",
        "- claimに必要なArtist URL/URI、UPC/EAN、本人確認情報等が不足している場合は、取得できる正規画面まで進めて停止し、必要項目を報告する。",
        "- Bioは下記Source factsだけを使って自然な文章にしてよいが、架空の実績・人物設定・受賞歴・活動歴は追加しない。",
        "- 正式採用画像 (`assets.artist_image`) が未設定なら、candidate一覧から勝手に1枚を正式採用しない。画像変更は行わず候補を報告する。",
        "- ヘッダー画像はカタログで明示的に指定されるまで勝手に作成・選択・アップロードしない。",
        "- 保存・claim申請の直前に、対象アーティスト名が正しいことを再確認する。",
        "",
        "## Task mode",
        mode,
        "",
        "## Artist identity",
        f"Artist name: {show(artist.get('name'))}",
        f"Spotify Artist URL: {show(spotify_url)}",
        "",
        "## Registered / upcoming releases in catalog",
        *release_lines,
        "",
        "## Bio source facts",
        f"Short description: {show(description.get('short'))}",
        f"Long description: {show(description.get('long'))}",
        f"Concept: {show(artist.get('concept'))}",
        f"Genres: {genre_text}",
        "",
        "Bio instruction: Spotifyの文字数上限内で、上記Source factsだけからアーティスト紹介文を作成・入力する。既存Bioがある場合は、事実を失わない範囲で更新案を作り、変更内容を報告する。",
        "",
        "## Social links",
        f"Website: {show(social.get('website'), 'none')}",
        f"Instagram: {show(social.get('instagram'), 'none')}",
        f"Facebook: {show(social.get('facebook'), 'none')}",
        f"X: {show(social.get('x'), 'none')}",
        f"TikTok: {show(social.get('tiktok'), 'none')}",
        "",
        "## Selected artist image",
        f"Selected asset: {show(selected_asset, 'NOT SELECTED — do not change avatar/header')}",
        f"Selected repo path: {show(selected_path, 'none')}",
        "",
        "## Candidate artist images — reference only, do not auto-select",
        *candidate_lines,
        "",
        "## Completion report",
        "最後に、claim/access状況、更新したBio/SNS/画像、保存・申請の有無、不足情報、Spotify画面で新たに判明した仕様を箇条書きで報告してください。",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render self-contained browser task packets from KAZEX Catalog YAML.")
    sub = parser.add_subparsers(dest="task", required=True)

    pitch = sub.add_parser("priority-pitch", help="Render a Too Lost Priority Pitch browser task")
    pitch.add_argument("release_id")

    spotify = sub.add_parser("spotify-profile", help="Render a Spotify for Artists browser task")
    spotify.add_argument("artist_id")

    args = parser.parse_args()
    if args.task == "priority-pitch":
        text = render_priority_pitch(args.release_id)
    else:
        text = render_spotify_profile(args.artist_id)
    sys.stdout.write(text + "\n")


if __name__ == "__main__":
    main()
