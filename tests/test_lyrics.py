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

    def test_confirmed_no_lyrics_is_distinct_from_missing(self):
        self.catalog['lyrics']['has_lyrics'] = False
        for track in self.index['tracks']:
            track.update(status='no_lyrics', text_path=None, sha256=None, adoption=None)
        (self.root / self.body_path).unlink()
        self.write(self.release, self.catalog)
        self.write(self.index_path, self.index)
        self.write(self.root / 'lyrics/collection.yaml', {'schema_version': 2, 'publication_scope': 'adopted_lyrics_only',
            'counts': {'adopted_tracks': 0, 'pending_selection_tracks': 0, 'not_collected_tracks': 0, 'no_lyrics_tracks': 3}})
        self.assertEqual([], self.check())

    def test_no_lyrics_cannot_be_inferred_from_missing_text(self):
        self.index['tracks'][2]['status'] = 'no_lyrics'
        self.write(self.index_path, self.index)
        self.assertTrue(any('requires release lyrics.has_lyrics=false' in x for x in self.check()))

    def test_instrumental_confirmation_is_checked_without_a_lyrics_index(self):
        extra = self.root / 'releases/instrumental.yaml'
        release = {'lyrics': {'has_lyrics': False}, 'tracks': [{'isrc': 'AA1234567893',
            'instrumental': {'basis': 'owner_confirmation', 'confirmed_on': '2026-10-28'}}]}
        self.write(extra, release)
        self.assertEqual([], validate_lyrics(self.root, [self.release, extra]))
        for value in [True, {'basis': 'inferred', 'confirmed_on': '2026-10-28'},
                      {'basis': 'owner_confirmation', 'confirmed_on': '2026-02-30'}]:
            with self.subTest(value=value):
                release['tracks'][0]['instrumental'] = value
                self.write(extra, release)
                self.assertTrue(any('instrumental' in x for x in validate_lyrics(self.root, [self.release, extra])))

    def test_instrumental_confirmation_cannot_conflict_with_lyric_adoption(self):
        self.catalog['tracks'][0]['instrumental'] = {'basis': 'owner_confirmation', 'confirmed_on': '2026-10-28'}
        self.catalog['lyrics']['has_lyrics'] = True
        self.write(self.release, self.catalog)
        errors = self.check()
        self.assertTrue(any('conflicts with has_lyrics=true' in x for x in errors))
        self.assertTrue(any('requires no_lyrics in the index' in x for x in errors))

    def test_no_lyrics_release_cannot_keep_missing_tasks(self):
        self.catalog['lyrics']['has_lyrics'] = False
        self.write(self.release, self.catalog)
        self.assertTrue(any('index status differs' in x for x in self.check()))

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
