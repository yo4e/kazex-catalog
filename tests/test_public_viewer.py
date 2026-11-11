import hashlib
import json
from pathlib import Path
import shutil
import sys
import unittest
import yaml

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

    def test_export_instrumental_requires_per_track_confirmation(self):
        release = yaml.safe_load((self.root / 'releases/example.yaml').read_text())
        release['lyrics']['has_lyrics'] = False
        release['tracks'][0]['instrumental'] = {'basis': 'owner_confirmation', 'confirmed_on': '2026-10-28'}
        release['tracks'].append({'title': 'New unconfirmed track', 'isrc': 'AA1234567891'})
        self.fixture.write('releases/example.yaml', release)
        export(self.root, self.destination)
        raw = (self.destination / 'data/tracks.json').read_text()
        tracks = json.loads(raw)
        self.assertTrue(tracks[self.fixture.key]['instrumental'])
        self.assertIsNone(tracks['example:AA1234567891']['instrumental'])
        self.assertNotIn('owner_confirmation', raw)
        self.assertNotIn('confirmed_on', raw)

    def test_new_profile_and_release_facts_do_not_export_unreviewed_fields(self):
        artist = yaml.safe_load((self.root / 'artists/example.yaml').read_text())
        artist['description'] = {'short': 'Public summary', 'long': 'Public biography', 'draft': 'NEVER_EXPORT'}
        artist['platforms'] = {'spotify_artist_url': 'https://open.spotify.com/artist/' + 'A' * 22,
                               'private_source': 'NEVER_EXPORT'}
        self.fixture.write('artists/example.yaml', artist)
        release = yaml.safe_load((self.root / 'releases/example.yaml').read_text())
        release['tracks'][0]['credits'] = {'songwriters': ['Original Name'], 'lyricists': ['Lyricist'],
            'composers': ['Composer'], 'vocalists': ['Singer'], 'private_proof': 'NEVER_EXPORT'}
        release['links'] = {'amazon_music': 'https://music.amazon.com/albums/B0FJTPVPSJ',
                            'private_source': 'NEVER_EXPORT'}
        self.fixture.write('releases/example.yaml', release)
        export(self.root, self.destination)
        raw = (self.destination / 'data/catalog.json').read_text()
        data = json.loads(raw)
        self.assertEqual(data['artists'][0]['biography'], 'Public biography')
        self.assertIsNone(data['artists'][0]['portrait'])
        self.assertEqual(data['releases'][0]['tracks'][0]['songwriters'], ['Original Name'])
        for role, name in [('lyricists', 'Lyricist'), ('composers', 'Composer'), ('vocalists', 'Singer')]:
            self.assertEqual(data['releases'][0]['tracks'][0][role], [name])
            tracks = json.loads((self.destination / 'data/tracks.json').read_text())
            self.assertEqual(tracks[self.fixture.key][role], [name])
        self.assertNotIn('NEVER_EXPORT', raw)
        self.assertEqual(data['releases'][0]['tracks'][0]['candidate_count'], 0)

    def test_prerelease_is_exported_even_without_website_publish(self):
        release = yaml.safe_load((self.root / 'releases/example.yaml').read_text())
        release.update({'status': 'planned', 'release_date': None, 'website': {'publish': False}})
        self.fixture.write('releases/example.yaml', release)
        export(self.root, self.destination)
        data = json.loads((self.destination / 'data/catalog.json').read_text())
        self.assertEqual(data['releases'][0]['release_status'], 'planned')
        self.assertEqual(data['releases'][0]['release_date'], '')
        self.assertEqual(data['releases'][0]['tracks'][0]['title'], '確認曲')
        self.assertNotIn('website', data['releases'][0])

    def test_upcoming_without_tracks_remains_in_catalog(self):
        release = yaml.safe_load((self.root / 'releases/example.yaml').read_text())
        release.update({'status': 'upcoming', 'release_date': '2027-01-02', 'tracks': []})
        self.fixture.write('releases/example.yaml', release)
        result = export(self.root, self.destination)
        data = json.loads((self.destination / 'data/catalog.json').read_text())
        self.assertEqual(result['releases'], 1)
        self.assertEqual(result['tracks'], 0)
        self.assertEqual(data['releases'][0]['release_status'], 'upcoming')
        self.assertEqual(data['releases'][0]['release_date'], '2027-01-02')

    def test_export_pitch_preserves_public_summary_and_omits_submission_fields(self):
        release = yaml.safe_load((self.root / 'releases/example.yaml').read_text())
        summary = 'Approved <pitch> & text.\n\nSecond paragraph.\n'
        translation = '公開ピッチの日本語訳。\n\n二つ目の段落。\n'
        release['promotion'] = {'priority_pitch': {'status': 'draft', 'release_summary': summary,
            'release_summary_ja': translation,
            'draft_translation': 'NEVER_EXPORT', 'marketing_elements': ['NEVER_EXPORT'],
            'attachments': {'epk_url': 'NEVER_EXPORT'}}}
        self.fixture.write('releases/example.yaml', release)
        export(self.root, self.destination)
        raw = (self.destination / 'data/catalog.json').read_text()
        self.assertEqual(json.loads(raw)['releases'][0]['pitch'], [
            {'language': 'en', 'label': 'English', 'body': summary},
            {'language': 'ja', 'label': '日本語訳', 'body': translation}])
        self.assertNotIn('NEVER_EXPORT', raw)
        self.assertEqual(yaml.safe_load((self.root / 'releases/example.yaml').read_text())['promotion']['priority_pitch']['status'], 'draft')

    def test_export_approved_full_sales_pitch_without_document_notes_or_duplicate_summary(self):
        release = yaml.safe_load((self.root / 'releases/example.yaml').read_text())
        release['promotion'] = {'sales_pitch_path': 'docs/releases/example-sales-pitch.md',
            'priority_pitch': {'release_summary': 'SHORT_VERSION', 'release_summary_ja': 'SHORT_TRANSLATION'}}
        self.fixture.write('releases/example.yaml', release)
        path = self.root / release['promotion']['sales_pitch_path']
        path.parent.mkdir(parents=True)
        path.write_text('# Approved pitch\n\nNEVER_EXPORT metadata\n\n## English\n\nFull English.\n\nParagraph two.\n\n## 日本語訳\n\n日本語の全文。\n\n## 申請時の確認\n\nNEVER_EXPORT notes\n')
        export(self.root, self.destination)
        raw = (self.destination / 'data/catalog.json').read_text()
        self.assertEqual(json.loads(raw)['releases'][0]['pitch'], [
            {'language': 'en', 'label': 'English', 'body': 'Full English.\n\nParagraph two.'},
            {'language': 'ja', 'label': '日本語訳', 'body': '日本語の全文。'}])
        for private in ['NEVER_EXPORT', 'SHORT_VERSION', 'SHORT_TRANSLATION', 'sales_pitch_path']:
            self.assertNotIn(private, raw)

    def test_export_no_pitch_is_an_empty_list(self):
        export(self.root, self.destination)
        data = json.loads((self.destination / 'data/catalog.json').read_text())
        self.assertEqual(data['releases'][0]['pitch'], [])

    def test_export_pitch_rejects_unexpected_fields(self):
        export(self.root, self.destination)
        path = self.destination / 'data/catalog.json'
        data = json.loads(path.read_text())
        data['releases'][0]['pitch'] = [{'language': 'en', 'label': 'English',
            'body': 'Approved', 'private_note': 'NEVER_EXPORT'}]
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Unexpected pitch fields'):
            validate_export(self.destination)
