#!/usr/bin/env python3
"""Read-only, loopback-only catalog review. Private inputs never enter the repo."""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
import threading
from urllib.parse import parse_qs, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
WEB = Path(__file__).resolve().parent / 'web'
HASH = lambda data: hashlib.sha256(data).hexdigest()


def confirmed_instrumental(value):
    if not isinstance(value, dict) or value.get('basis') != 'owner_confirmation':
        return None
    try:
        dt.date.fromisoformat(value.get('confirmed_on'))
    except (TypeError, ValueError):
        return None
    return True


def spotify_track_id(value):
    match = re.fullmatch(r'https://open\.spotify\.com/track/([A-Za-z0-9]{22})', value or '')
    return match.group(1) if match else None


def release_smartlink(value):
    return value if re.fullmatch(r'https://too\.fm/[A-Za-z0-9_-]+', value or '') else None


def service_links(values, kind):
    """Only canonical public service URLs; never export arbitrary URL fields."""
    spotify_kind = {'artist': 'artist', 'release': 'album', 'track': 'track'}[kind]
    apple_kind = {'artist': 'artist', 'release': 'album', 'track': 'song'}[kind]
    amazon_kind = {'artist': 'artists', 'release': 'albums', 'track': 'tracks'}[kind]
    formats = {
        'spotify': ('Spotify', rf'https://open\.spotify\.com/{spotify_kind}/[A-Za-z0-9]{{22}}'),
        'apple_music': ('Apple Music', rf'https://music\.apple\.com/jp/{apple_kind}/(?:[^/?#\s]+/)?[0-9]+'),
        'amazon_music': ('Amazon Music', rf'https://music\.amazon\.(?:com|co\.jp|co\.uk)/{amazon_kind}/[A-Z0-9]{{10}}'),
    }
    result = []
    for key, (label, pattern) in formats.items():
        value = values.get(key)
        if isinstance(value, str) and re.fullmatch(pattern, value):
            result.append({'service': key, 'label': label, 'url': value})
    return result


def text_fields(values, fields):
    return {key: values.get(key) if isinstance(values.get(key), str) else None for key in fields}


def text_list(value):
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def contained(root: Path, value: str) -> Path:
    target = (root / value).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Path outside allowed directory')
    return target


class PrivateCandidates:
    def __init__(self, repo: Path, config: Path | None):
        self.versions: dict[str, list[dict]] = {}
        self.enabled = config is not None
        if config is None:
            return
        def external(path):
            target = Path(path).expanduser().resolve()
            if target.is_relative_to(repo.resolve()):
                raise ValueError('Private configuration and inputs must be outside the repository')
            return target
        settings = json.loads(external(config).read_text())
        source = json.loads(external(settings['private_index']).read_text())
        checks = json.loads(external(settings['review_validation']).read_text())
        review = external(settings['review_file']).read_bytes()
        if HASH(review) != checks['sha256']:
            raise ValueError('Private review checksum mismatch')
        originals = {(t['track_id'], v['version_id']): v for t in source['tracks'] for v in t['versions']}
        previous_end = 0
        for body in checks['bodies']:
            key = (body['track_id'], body['version_id'])
            original = originals[key]
            start, end = body['clean_start_byte'], body['clean_end_byte']
            content = review[start:end]
            if not (previous_end <= start < end <= len(review)) or HASH(content) != body['clean_sha256']:
                raise ValueError('Invalid private body boundary or checksum')
            prefix = review[previous_end:start].decode('utf-8')
            label = re.findall(r'［(本文版[A-Z]+ / 表示\d+)：[^\n]+］', prefix)
            if len(label) != 1:
                raise ValueError('Private review label missing')
            previous_end = end
            # Explicit allowlist: never expose raw paths or supporting documents.
            sources = []
            for origin in original['origins']:
                url = origin.get('source_url') or origin.get('suno_url')
                if url and not re.fullmatch(r'https://suno\.com/(?:song|playlist)/[a-zA-Z0-9-]+', url):
                    url = None
                item = {'kind': origin['kind'], 'url': url,
                        'label': origin.get('version_label') or '保存原稿',
                        'confidence': origin.get('confidence')}
                if item not in sources:
                    sources.append(item)
            self.versions.setdefault(key[0], []).append({
                'id': key[1], 'reference': f'{key[0]}:{key[1]}', 'label': label[0],
                'body': content.decode('utf-8'), 'sha256': HASH(content),
                'kinds': sorted({s['kind'] for s in sources}), 'sources': sources,
                'master_audio_verified': False,
            })


class Catalog:
    def __init__(self, root: Path, private: PrivateCandidates):
        self.root = root
        self.private = private
        self.lock = threading.RLock()
        self.refresh()

    def yaml(self, path: str):
        return yaml.safe_load(contained(self.root, path).read_text(encoding='utf-8'))

    def image(self, path, status, title, kind):
        if not path:
            return None
        target = contained(self.root / 'assets', str(path).removeprefix('assets/'))
        if not str(path).startswith('assets/') or not target.is_file() or target.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'}:
            return None
        ident = HASH(str(path).encode())[:16]
        self.image_files[ident] = target
        return {'id': ident, 'url': f'/api/image/{ident}', 'path': path, 'status': status,
                'title': title or target.stem, 'kind': kind, 'sha256': HASH(target.read_bytes())}

    def refresh(self):
        with self.lock:
            self.image_files = {}
            self.track_details = {}
            artists = []
            lyric_defaults = {}
            for path in sorted((self.root / 'artists').glob('*.yaml')):
                data = self.yaml(str(path.relative_to(self.root)))
                assets = data.get('assets', {})
                pictures = []
                for kind, field in [('アー写', 'artist_photo_candidates'), ('参考画像', 'concept_art')]:
                    for value in assets.get(field, []):
                        image = self.image(value.get('github_path'), value.get('status', 'candidate'),
                                           value.get('description') or value.get('role'), kind)
                        if image:
                            pictures.append(image)
                primary = assets.get('artist_image') or {}
                primary_path = primary.get('github_path')
                if primary_path and not any(p['path'] == primary_path for p in pictures):
                    image = self.image(primary_path, 'selected', '登録アー写', 'アー写')
                    if image:
                        pictures.insert(0, image)
                portrait = next((p for p in pictures if p['path'] == primary_path
                                 and p['status'] == 'selected'), None)
                lyric_defaults[data['id']] = (data.get('lyrics') or {}).get('default_has_lyrics')
                artists.append({'id': data['id'], 'name': data['name'],
                                'description': (data.get('description') or {}).get('short'), 'images': pictures,
                                'biography': (data.get('description') or {}).get('long'),
                                'links': service_links({key: (data.get('platforms') or {}).get(field) for key, field in
                                    [('spotify', 'spotify_artist_url'), ('apple_music', 'apple_music_artist_url')]}, 'artist'),
                                'portrait': portrait, 'default_has_lyrics': lyric_defaults[data['id']]})
            releases = []
            for path in sorted((self.root / 'releases').glob('*.yaml')):
                data = self.yaml(str(path.relative_to(self.root)))
                lyrics = data.get('lyrics', {})
                has_lyrics = lyrics.get('has_lyrics')
                if has_lyrics is None:
                    has_lyrics = lyric_defaults.get(data['artist_id'])
                indexed = {}
                if lyrics.get('index_path'):
                    indexed = {t['isrc']: t for t in self.yaml(lyrics['index_path'])['tracks']}
                tracks = []
                for number, track in enumerate(data.get('tracks', []), 1):
                    isrc = track.get('isrc')
                    key = f"{data['id']}:{isrc or number}"
                    saved = indexed.get(isrc, {})
                    status = 'no_lyrics' if has_lyrics is False else saved.get('status') or 'not_collected'
                    public = {'key': key, 'number': number, 'title': track['title'], 'isrc': isrc,
                              'status': status, 'candidate_count': len(self.private.versions.get(key, [])),
                              'instrumental': confirmed_instrumental(track.get('instrumental')),
                              'duration_seconds': track.get('duration_seconds'),
                              **{role: text_list((track.get('credits') or {}).get(role))
                                 for role in ('songwriters', 'lyricists', 'composers', 'vocalists')},
                              'links': service_links(track.get('links') or {}, 'track'),
                              'spotify_id': spotify_track_id((track.get('links') or {}).get('spotify'))}
                    tracks.append(public)
                    adopted = None
                    if status == 'adopted':
                        body = contained(self.root, saved['text_path']).read_bytes()
                        if HASH(body) != saved['sha256']:
                            raise ValueError('Public lyric checksum mismatch')
                        adopted = {'id': 'adopted', 'label': '採用済み', 'body': body.decode('utf-8'), 'sha256': HASH(body)}
                    self.track_details[key] = {**public, 'adopted': adopted}
                cover = self.image((data.get('cover') or {}).get('github_path'), 'registered', '登録ジャケット', 'ジャケット')
                releases.append({'id': data['id'], 'title': data['title'], 'artist_id': data['artist_id'],
                                 'release_date': str(data.get('release_date') or ''), 'type': data.get('release_type'),
                                 'cover': cover, 'tracks': tracks,
                                 'links': service_links(data.get('links') or {}, 'release'),
                                 'metadata': {'genres': text_list(data.get('genres')), 'label': data.get('label'),
                                     'identifiers': text_fields(data.get('identifiers') or {}, ['upc_ean', 'catalog_number', 'amazon_asin']),
                                     'copyright': text_fields(data.get('copyright') or {}, ['c_line', 'p_line'])},
                                 'smartlink': release_smartlink((data.get('links') or {}).get('smartlink'))})
            brand = {'name': 'KazeX Records', 'logo': None, 'colors': {}}
            if (self.root / 'assets/label/brand.yaml').is_file():
                settings = self.yaml('assets/label/brand.yaml')
                brand = {'name': settings['name'],
                         'logo': self.image(settings['logo']['github_path'], 'selected', settings['name'], 'レーベルロゴ'),
                         'colors': {k: v for k, v in settings.get('colors', {}).items()
                                    if k in {'accent', 'background'} and re.fullmatch(r'#[0-9a-fA-F]{6}', v)}}
            self.catalog = {'artists': artists, 'releases': releases, 'brand': brand, 'private_available': self.private.enabled,
                            'counts': dict(collections.Counter(t['status'] for r in releases for t in r['tracks']))}


class ReviewServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, catalog: Catalog, port: int):
        self.catalog = catalog
        super().__init__(('127.0.0.1', port), Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Request URLs and private candidate IDs do not enter access logs.

    def send(self, status, content, content_type='application/json; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Permissions-Policy', 'autoplay=(), camera=(), microphone=(), geolocation=()')
        self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; frame-src https://open.spotify.com; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(content)

    def json(self, value, status=200):
        self.send(status, json.dumps(value, ensure_ascii=False).encode('utf-8'))

    def permitted(self):
        port = self.server.server_port
        allowed = {f'127.0.0.1:{port}', f'localhost:{port}'}
        host = self.headers.get('Host')
        origin = self.headers.get('Origin')
        if host not in allowed or (origin is not None and origin not in {'http://' + h for h in allowed}):
            return False
        if self.headers.get('Sec-Fetch-Site') not in {'cross-site', 'same-site'}:
            return True
        # A user following a link (and Chrome reloading that navigation) may
        # remain cross-site. Only the data-free entry HTML may be opened this
        # way; APIs and assets still require a local same-origin request.
        return (self.command == 'GET' and urlsplit(self.path).path == '/'
                and origin is None
                and self.headers.get('Sec-Fetch-Mode') == 'navigate'
                and self.headers.get('Sec-Fetch-Dest') == 'document'
                and self.headers.get('Sec-Fetch-User') == '?1')

    def do_POST(self):
        self.json({'error': 'Read-only preview'}, 405)

    do_PUT = do_DELETE = do_PATCH = do_POST

    def do_GET(self):
        if not self.permitted():
            self.json({'error': 'Local same-origin access only'}, 403)
            return
        parsed = urlsplit(self.path)
        route = parsed.path
        if route == '/favicon.ico':
            self.send(204, b'', 'image/x-icon')
            return
        static = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                  '/style.css': ('style.css', 'text/css; charset=utf-8')}
        try:
            if route in static:
                filename, content_type = static[route]
                self.send(200, (WEB / filename).read_bytes(), content_type)
                return
            catalog = self.server.catalog
            with catalog.lock:
                if route == '/api/catalog':
                    catalog.refresh()
                    self.json(catalog.catalog)
                elif route in {'/api/track', '/api/candidates'}:
                    key = parse_qs(parsed.query).get('key', [''])[0]
                    if key not in catalog.track_details:
                        self.json({'error': 'Track not found'}, 404)
                    elif route == '/api/track':
                        self.json(catalog.track_details[key])
                    else:
                        self.json({'available': catalog.private.enabled, 'versions': catalog.private.versions.get(key, [])})
                elif route.startswith('/api/image/') and route.removeprefix('/api/image/') in catalog.image_files:
                    path = catalog.image_files[route.removeprefix('/api/image/')]
                    self.send(200, path.read_bytes(), mimetypes.guess_type(path.name)[0] or 'image/png')
                else:
                    self.json({'error': 'Not found'}, 404)
        except (ValueError, KeyError, OSError):
            self.json({'error': '資料を読み込めません。起動設定と検証結果を確認してください。'}, 500)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8767)
    parser.add_argument('--private-config', type=Path)
    args = parser.parse_args()
    private = PrivateCandidates(ROOT, args.private_config)
    server = ReviewServer(Catalog(ROOT, private), args.port)
    print(f'Catalog review: http://127.0.0.1:{server.server_port}/', flush=True)
    print('Private candidates enabled' if private.enabled else 'Public catalog only', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
