import base64
import hashlib
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'viewer'))
from server import Catalog, PrivateCandidates, ReviewServer, spotify_track_id, release_smartlink, service_links


class LocalReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.repo, self.private = base / 'repo', base / 'private'
        self.private.mkdir()
        self.body = 'PRIVATE_CANDIDATE_SAMPLE\n'
        header = '［本文版A / 表示1：保存原稿］\n\n'
        review = (header + self.body).encode()
        vid = 'a' * 20
        self.key = 'example:AA1234567890'
        source = {'tracks': [{'track_id': self.key, 'versions': [{'version_id': vid, 'origins': [
            {'kind': 'suno', 'source_url': 'https://' + 'suno' + '.com/song/example',
             'source_path': '/private/never-expose', 'confidence': 'candidate', 'version_label': '確認用'}
        ]}]}]}
        checks = {'sha256': hashlib.sha256(review).hexdigest(), 'bodies': [{
            'track_id': self.key, 'version_id': vid, 'clean_start_byte': len(header.encode()),
            'clean_end_byte': len(review), 'clean_sha256': hashlib.sha256(self.body.encode()).hexdigest(),
        }]}
        config = {}
        for key, name, value in [('private_index', 'index.json', source), ('review_validation', 'checks.json', checks)]:
            path = self.private / name
            path.write_text(json.dumps(value))
            config[key] = str(path)
        (self.private / 'review.txt').write_bytes(review)
        config['review_file'] = str(self.private / 'review.txt')
        self.config = self.private / 'config.json'
        self.config.write_text(json.dumps(config))
        self.write('artists/example.yaml', {'id': 'example', 'name': '確認アーティスト', 'assets': {
            'artist_photo_candidates': [{'github_path': 'assets/candidate.png', 'status': 'candidate'},
                                        {'github_path': 'assets/old.png', 'status': 'archived'}]}})
        self.write('releases/example.yaml', {'id': 'example', 'title': '確認作品', 'artist_id': 'example',
            'tracks': [{'title': '確認曲', 'isrc': 'AA1234567890'}], 'lyrics': {'index_path': 'lyrics/example/index.yaml'}})
        self.write('lyrics/example/index.yaml', {'tracks': [{'isrc': 'AA1234567890', 'status': 'pending_selection'}]})
        pixel = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jWZkAAAAASUVORK5CYII=')
        for name in ['candidate.png', 'old.png']:
            path = self.repo / 'assets' / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(pixel)

    def write(self, name, data):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, allow_unicode=True))

    def start(self, private=True):
        store = PrivateCandidates(self.repo, self.config if private else None)
        server = ReviewServer(Catalog(self.repo, store), 0)
        thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server

    def get(self, server, path, headers=None, method='GET'):
        conn = http.client.HTTPConnection('127.0.0.1', server.server_port)
        conn.request(method, path, headers=headers or {})
        response = conn.getresponse()
        result = (response.status, dict(response.getheaders()), response.read())
        conn.close()
        return result

    def test_private_config_in_repository_is_rejected(self):
        path = self.repo / 'config.json'
        path.write_text(self.config.read_text())
        with self.assertRaisesRegex(ValueError, 'outside the repository'):
            PrivateCandidates(self.repo, path)

    def test_private_input_in_repository_is_rejected(self):
        data = json.loads(self.config.read_text())
        data['private_index'] = str(self.repo / 'private.json')
        self.config.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'outside the repository'):
            PrivateCandidates(self.repo, self.config)

    def test_checksum_failure_does_not_silently_show_wrong_lyrics(self):
        (self.private / 'review.txt').write_text('altered')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            PrivateCandidates(self.repo, self.config)

    def test_public_api_never_includes_private_lyrics(self):
        server = self.start()
        for path in ['/api/catalog', '/api/track?key=' + self.key]:
            status, headers, body = self.get(server, path)
            self.assertEqual(status, 200)
            self.assertNotIn(self.body.encode(), body)
            self.assertNotIn(b'source_path', body)
            self.assertNotIn(b'https://', body)
            self.assertEqual(headers['Cache-Control'], 'no-store')

    def test_private_endpoint_exposes_only_whitelisted_candidate_fields(self):
        server = self.start()
        status, _, body = self.get(server, '/api/candidates?key=' + self.key)
        data = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(data['versions'][0]['body'], self.body)
        self.assertNotIn(b'source_path', body)
        self.assertNotIn(b'/private/', body)
        self.assertEqual(data['versions'][0]['reference'], self.key + ':' + 'a' * 20)

    def test_without_private_config_no_candidates_can_be_fetched(self):
        server = self.start(private=False)
        _, _, body = self.get(server, '/api/candidates?key=' + self.key)
        self.assertEqual(json.loads(body), {'available': False, 'versions': []})

    def test_loopback_only_and_foreign_host_origin_are_denied(self):
        server = self.start()
        self.assertEqual(server.server_address[0], '127.0.0.1')
        for headers in [{'Host': 'example.com'}, {'Origin': 'https://example.com'}, {'Sec-Fetch-Site': 'cross-site'}]:
            self.assertEqual(self.get(server, '/api/catalog', headers)[0], 403)

    def test_no_arbitrary_files_or_raw_repository(self):
        server = self.start()
        for path in ['/../private/config.json', '/api/image/../../private', '/.git/config', '/releases/example.yaml', '/viewer/server.py']:
            self.assertEqual(self.get(server, path)[0], 404)

    def navigation_headers(self):
        # Captured from the user's Chrome reload of the blocked local page.
        return {'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Dest': 'document', 'Sec-Fetch-User': '?1'}

    def test_user_navigation_can_open_only_the_data_free_entry_page(self):
        server = self.start()
        headers = self.navigation_headers()
        for site in ['cross-site', 'same-site']:
            with self.subTest(site=site):
                headers['Sec-Fetch-Site'] = site
                status, response_headers, body = self.get(server, '/', headers)
                self.assertEqual(status, 200)
                self.assertIn('text/html', response_headers['Content-Type'])
                self.assertNotIn(self.body.encode(), body)
                self.assertNotIn(b'source_url', body)
                self.assertNotIn('Access-Control-Allow-Origin', response_headers)
                self.assertIn("frame-ancestors 'none'", response_headers['Content-Security-Policy'])

    def test_navigation_exception_never_allows_foreign_host_or_origin(self):
        server = self.start()
        for bad in [{'Host': 'example.com'}, {'Origin': 'https://example.com'},
                    {'Origin': 'null'}, {'Host': '127.0.0.1:1'}]:
            with self.subTest(headers=bad):
                headers = {**self.navigation_headers(), **bad}
                self.assertEqual(self.get(server, '/', headers)[0], 403)

    def test_cross_site_navigation_cannot_fetch_api_assets_or_lyrics(self):
        server = self.start()
        for path in ['/api/catalog', '/api/track?key=' + self.key,
                     '/api/candidates?key=' + self.key, '/api/image/example',
                     '/app.js', '/style.css', '/lyrics/example/index.yaml']:
            with self.subTest(path=path):
                self.assertEqual(self.get(server, path, self.navigation_headers())[0], 403)

    def test_cross_site_embedding_fetch_and_script_navigation_stay_denied(self):
        server = self.start()
        for change in [{'Sec-Fetch-User': None}, {'Sec-Fetch-User': '?0'},
                       {'Sec-Fetch-Dest': 'iframe'}, {'Sec-Fetch-Dest': 'image'},
                       {'Sec-Fetch-Mode': 'cors'}, {'Sec-Fetch-Mode': 'no-cors'}]:
            with self.subTest(change=change):
                headers = {k: v for k, v in {**self.navigation_headers(), **change}.items() if v is not None}
                self.assertEqual(self.get(server, '/', headers)[0], 403)

    def test_same_origin_requests_work_after_opening_entry_page(self):
        server = self.start()
        for path in ['/', '/app.js', '/api/catalog', '/api/candidates?key=' + self.key]:
            with self.subTest(path=path):
                headers = {'Sec-Fetch-Site': 'same-origin',
                           'Origin': 'http://127.0.0.1:' + str(server.server_port)}
                self.assertEqual(self.get(server, path, headers)[0], 200)

    def test_mutating_requests_are_not_supported(self):
        server = self.start()
        before = (self.repo / 'releases/example.yaml').read_bytes()
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.assertEqual(self.get(server, '/api/candidates?key=' + self.key, method=method)[0], 405)
        self.assertEqual((self.repo / 'releases/example.yaml').read_bytes(), before)

    def test_image_status_is_preserved(self):
        server = self.start()
        _, _, body = self.get(server, '/api/catalog')
        images = json.loads(body)['artists'][0]['images']
        self.assertEqual([i['status'] for i in images], ['candidate', 'archived'])
        for image in images:
            self.assertEqual(self.get(server, image['url'])[0], 200)

    def test_candidate_or_unassigned_selected_is_not_a_representative_photo(self):
        server = self.start()
        _, _, body = self.get(server, '/api/catalog')
        self.assertIsNone(json.loads(body)['artists'][0]['portrait'])
        data = yaml.safe_load((self.repo / 'artists/example.yaml').read_text())
        data['assets']['artist_photo_candidates'][0]['status'] = 'selected'
        self.write('artists/example.yaml', data)
        _, _, body = self.get(server, '/api/catalog')
        self.assertIsNone(json.loads(body)['artists'][0]['portrait'])
        data['assets']['artist_image'] = {'github_path': 'assets/candidate.png'}
        self.write('artists/example.yaml', data)
        _, _, body = self.get(server, '/api/catalog')
        portrait = json.loads(body)['artists'][0]['portrait']
        self.assertEqual(portrait['path'], 'assets/candidate.png')
        self.assertEqual(portrait['status'], 'selected')

    def test_artist_lyric_default_and_explicit_release_exception(self):
        artist = yaml.safe_load((self.repo / 'artists/example.yaml').read_text())
        artist['lyrics'] = {'default_has_lyrics': False}
        self.write('artists/example.yaml', artist)
        server = self.start()
        _, _, body = self.get(server, '/api/catalog')
        self.assertEqual(json.loads(body)['releases'][0]['tracks'][0]['status'], 'no_lyrics')
        release = yaml.safe_load((self.repo / 'releases/example.yaml').read_text())
        release['lyrics']['has_lyrics'] = True
        self.write('releases/example.yaml', release)
        _, _, body = self.get(server, '/api/catalog')
        self.assertEqual(json.loads(body)['releases'][0]['tracks'][0]['status'], 'pending_selection')

    def test_listening_links_use_only_exact_registered_service_formats(self):
        ident = 'A' * 22
        self.assertEqual(spotify_track_id('https://open.spotify.com/track/' + ident), ident)
        for value in [None, 'javascript:alert(1)', 'https://open.spotify.com/album/' + ident,
                      'https://open.spotify.com.evil/track/' + ident,
                      'https://open.spotify.com/track/' + ident + '?private=example']:
            self.assertIsNone(spotify_track_id(value))
        self.assertEqual(release_smartlink('https://too.fm/example'), 'https://too.fm/example')
        for value in [None, 'https://too.fm.evil/example', 'https://too.fm/example?private=x']:
            self.assertIsNone(release_smartlink(value))

    def test_embed_security_headers_keep_parent_and_local_data_isolated(self):
        server = self.start()
        _, headers, _ = self.get(server, '/')
        self.assertEqual(headers['Referrer-Policy'], 'no-referrer')
        self.assertIn('autoplay=()', headers['Permissions-Policy'])
        self.assertIn('frame-src https://open.spotify.com;', headers['Content-Security-Policy'])
        self.assertIn("connect-src 'self';", headers['Content-Security-Policy'])
        self.assertIn("frame-ancestors 'none';", headers['Content-Security-Policy'])

    def test_service_links_reject_wrong_identity_kind_queries_and_foreign_hosts(self):
        good = 'https://open.spotify.com/album/' + 'A' * 22
        self.assertEqual(service_links({'spotify': good}, 'release')[0]['url'], good)
        self.assertEqual(service_links({'spotify': good}, 'track'), [])
        for value in [good + '?private=example', good + '#secret', good.replace('.com/', '.com.evil/'),
                      'javascript:alert(1)', 'https://user:password@open.spotify.com/album/' + 'A' * 22]:
            self.assertEqual(service_links({'spotify': value}, 'release'), [])
        apple = 'https://music.apple.com/jp/song/example/12345'
        amazon = 'https://music.amazon.com/tracks/B0FJV1JHVF'
        self.assertEqual(len(service_links({'apple_music': apple, 'amazon_music': amazon}, 'track')), 2)
        self.assertEqual(service_links({'apple_music': apple, 'amazon_music': amazon}, 'artist'), [])
        self.assertEqual(service_links({'unreviewed': good}, 'release'), [])

    def test_catalog_facts_refresh_from_yaml_without_private_supporting_fields(self):
        path = self.repo / 'releases/example.yaml'
        release = yaml.safe_load(path.read_text())
        release.update({'genres': ['J-Pop'], 'label': 'Example Label',
                        'identifiers': {'upc_ean': '0123456789012', 'private_note': 'NEVER_EXPORT'},
                        'copyright': {'c_line': 'PUBLIC_CREDIT'}, 'notes_public': 'NEVER_EXPORT'})
        release['tracks'][0].update({'duration_seconds': 158,
            'credits': {'songwriters': ['原 表記'], 'supporting_document': 'NEVER_EXPORT'},
            'links': {'apple_music': 'https://music.apple.com/jp/song/example/12345'}})
        self.write('releases/example.yaml', release)
        server = self.start()
        _, _, body = self.get(server, '/api/catalog')
        data = json.loads(body)['releases'][0]
        self.assertEqual(data['metadata']['identifiers']['upc_ean'], '0123456789012')
        self.assertEqual(data['tracks'][0]['duration_seconds'], 158)
        self.assertEqual(data['tracks'][0]['songwriters'], ['原 表記'])
        self.assertNotIn(b'NEVER_EXPORT', body)
        release['tracks'][0]['duration_seconds'] = 159
        self.write('releases/example.yaml', release)
        _, _, body = self.get(server, '/api/catalog')
        self.assertEqual(json.loads(body)['releases'][0]['tracks'][0]['duration_seconds'], 159)


if __name__ == '__main__':
    unittest.main()
