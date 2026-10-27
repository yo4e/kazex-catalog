import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_lyrics import validate_lyrics


class AdoptedLyricsValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.release = self.root / 'releases/example.yaml'
        self.index_path = self.root / 'lyrics/example/index.yaml'
        self.body_path = 'lyrics/example/aa1234567890.txt'
        target = self.root / self.body_path
        target.parent.mkdir(parents=True)
        content = '確認用の本文\r\n'.encode()
        target.write_bytes(content)
        self.catalog = {'id': 'example', 'lyrics': {'index_path': 'lyrics/example/index.yaml'},
                        'tracks': [{'isrc': 'AA1234567890'}, {'isrc': 'AA1234567891'}, {'isrc': 'AA1234567892'}]}
        self.index = {'schema_version': 2, 'release_id': 'example', 'tracks': [
            {'isrc': 'AA1234567890', 'status': 'adopted', 'text_path': self.body_path,
             'sha256': hashlib.sha256(content).hexdigest(),
             'adoption': {'basis': 'completed_submission_record', 'verified_on': '2026-10-27'}},
            {'isrc': 'AA1234567891', 'status': 'pending_selection', 'text_path': None, 'sha256': None, 'adoption': None},
            {'isrc': 'AA1234567892', 'status': 'not_collected', 'text_path': None, 'sha256': None, 'adoption': None},
        ]}
        self.write(self.release, self.catalog)
        self.write(self.index_path, self.index)
        self.write(self.root / 'lyrics/collection.yaml', {'schema_version': 2, 'publication_scope': 'adopted_lyrics_only',
            'counts': {'adopted_tracks': 1, 'pending_selection_tracks': 1, 'not_collected_tracks': 1}})

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data), encoding='utf-8')

    def check(self):
        return validate_lyrics(self.root, [self.release])

    def test_valid_adopted_pending_and_missing_are_distinct(self):
        self.assertEqual([], self.check())

    def test_changed_body_is_detected(self):
        (self.root / self.body_path).write_text('変更された本文')
        self.assertTrue(any('SHA256 mismatch' in x for x in self.check()))

    def test_isrc_order_mismatch(self):
        self.index['tracks'].reverse()
        self.write(self.index_path, self.index)
        self.assertTrue(any('track ISRCs' in x for x in self.check()))

    def test_pending_track_cannot_link_a_body(self):
        self.index['tracks'][1]['text_path'] = self.body_path
        self.write(self.index_path, self.index)
        self.assertTrue(any('must not expose' in x for x in self.check()))

    def test_missing_track_cannot_link_a_body(self):
        self.index['tracks'][2]['text_path'] = self.body_path
        self.write(self.index_path, self.index)
        self.assertTrue(any('must not expose' in x for x in self.check()))

    def test_unreferenced_alternative_file_is_rejected(self):
        (self.root / 'lyrics/example/alternate.txt').write_text('別版のテスト')
        self.assertTrue(any('unexpected file' in x for x in self.check()))

    def test_source_metadata_is_rejected(self):
        self.index['tracks'][0]['sources'] = [{'kind': 'private'}]
        self.write(self.index_path, self.index)
        self.assertTrue(any('unexpected or missing fields' in x for x in self.check()))

    def test_adopted_body_requires_a_record(self):
        self.index['tracks'][0]['adoption'] = None
        self.write(self.index_path, self.index)
        self.assertTrue(any('need an adoption record' in x for x in self.check()))

    def test_bad_body_path_is_rejected(self):
        self.index['tracks'][0]['text_path'] = '../private.txt'
        self.write(self.index_path, self.index)
        self.assertTrue(any('text_path must match' in x for x in self.check()))

    def test_source_url_in_documentation_is_rejected_without_echoing_it(self):
        url = 'https://' + 'suno' + '.com/song/private-example'
        (self.root / 'README.md').write_text(url)
        errors = self.check()
        self.assertTrue(any('source-service URL' in x for x in errors))
        self.assertNotIn(url, '\n'.join(errors))

    def test_invalid_utf8_is_rejected(self):
        (self.root / self.body_path).write_bytes(b'\xff')
        self.assertTrue(any('unreadable UTF-8' in x for x in self.check()))


if __name__ == '__main__':
    unittest.main()
