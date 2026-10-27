import hashlib
import json
from pathlib import Path
import shutil
import sys
import unittest

import test_viewer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_public_viewer import export, validate_export


class PublicViewerTests(unittest.TestCase):
    def setUp(self):
        fixture = test_viewer.LocalReviewTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.root = fixture.repo
        shutil.copytree(ROOT / 'viewer/web', self.root / 'viewer/web')
        self.destination = self.root.parent / 'site'

    def test_export_ignores_existing_private_candidates_and_sources(self):
        result = export(self.root, self.destination)
        self.assertEqual(result['private_candidates'], 0)
        data = json.loads((self.destination / 'data/catalog.json').read_text())
        tracks = json.loads((self.destination / 'data/tracks.json').read_text())
        self.assertFalse(data['private_available'])
        self.assertEqual(tracks[self.fixture.key]['candidate_count'], 0)
        self.assertIsNone(tracks[self.fixture.key]['adopted'])
        for path in self.destination.rglob('*'):
            if path.is_file():
                self.assertNotIn(self.fixture.body.encode(), path.read_bytes())
                self.assertNotIn(b'/private/never-expose', path.read_bytes())
        self.assertFalse((self.destination / 'api').exists())
        self.assertFalse((self.destination / 'server.py').exists())

    def test_export_includes_only_adopted_text_and_relative_image_links(self):
        text = 'PUBLIC_ADOPTED_SAMPLE\n'
        body_path = self.root / 'lyrics/example/adopted.txt'
        body_path.write_text(text)
        self.fixture.write('lyrics/example/index.yaml', {'tracks': [{'isrc': 'AA1234567890', 'status': 'adopted',
            'text_path': 'lyrics/example/adopted.txt', 'sha256': hashlib.sha256(text.encode()).hexdigest()}]})
        result = export(self.root, self.destination)
        self.assertEqual(result['adopted_lyrics'], 1)
        tracks = json.loads((self.destination / 'data/tracks.json').read_text())
        self.assertEqual(tracks[self.fixture.key]['adopted']['body'], text)
        catalog = json.loads((self.destination / 'data/catalog.json').read_text())
        for image in catalog['artists'][0]['images']:
            self.assertTrue(image['url'].startswith('assets/media/'))
            self.assertTrue((self.destination / image['url']).is_file())
        html = (self.destination / 'index.html').read_text()
        self.assertIn('data-mode="public"', html)
        self.assertIn('src="./app.js"', html)
        self.assertIn('name="referrer" content="no-referrer"', html)

    def test_export_validation_rejects_candidate_metadata_and_local_paths(self):
        export(self.root, self.destination)
        path = self.destination / 'data/tracks.json'
        data = json.loads(path.read_text())
        data[self.fixture.key]['source_path'] = '/private/example'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Unexpected track fields'):
            validate_export(self.destination)

    def test_export_never_overwrites_existing_destination(self):
        self.destination.mkdir()
        (self.destination / 'keep.txt').write_text('retain')
        with self.assertRaisesRegex(ValueError, 'never overwritten'):
            export(self.root, self.destination)
        self.assertEqual((self.destination / 'keep.txt').read_text(), 'retain')
