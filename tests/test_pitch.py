from pathlib import Path
import sys
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'viewer'))
from server import release_pitch


class PitchTests(unittest.TestCase):
    def test_empty_and_nontext_summary_do_not_create_pitch(self):
        for value in [None, '', '  \n', [], {}]:
            with self.subTest(value=value):
                self.assertEqual(release_pitch(ROOT, {'promotion': {'priority_pitch': {'release_summary': value}}}), [])
        self.assertEqual(release_pitch(ROOT, {}), [])

    def test_sales_pitch_path_cannot_escape_public_docs(self):
        for path in ['../../private/example.md', 'docs/releases/../../secret-sales-pitch.md',
                     '/tmp/example-sales-pitch.md', 'docs/releases/example.md', 123]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                release_pitch(ROOT, {'promotion': {'sales_pitch_path': path}})

    def test_sales_pitch_symlink_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'repo'
            folder = root / 'docs/releases'
            folder.mkdir(parents=True)
            source = base / 'secret.md'
            source.write_text('## English\n\nSecret')
            (folder / 'example-sales-pitch.md').symlink_to(source)
            with self.assertRaisesRegex(ValueError, 'outside allowed'):
                release_pitch(root, {'promotion': {'sales_pitch_path': 'docs/releases/example-sales-pitch.md'}})

    def test_missing_or_unrecognized_full_pitch_fails_instead_of_silent_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = {'promotion': {'sales_pitch_path': 'docs/releases/example-sales-pitch.md',
                                  'priority_pitch': {'release_summary': 'Do not fall back'}}}
            with self.assertRaises(FileNotFoundError):
                release_pitch(root, data)
            path = root / data['promotion']['sales_pitch_path']
            path.parent.mkdir(parents=True)
            path.write_text('# Notes only\n\nNo approved text')
            with self.assertRaisesRegex(ValueError, 'no English or Japanese body'):
                release_pitch(root, data)

    def test_existing_public_pitch_bodies_come_from_canonical_sources(self):
        for ident in ['please-remain-still', 'unseen-dragon', 'ghost-velocity', 'shirasu']:
            data = yaml.safe_load((ROOT / f'releases/{ident}.yaml').read_text())
            self.assertEqual(release_pitch(ROOT, data)[0]['body'], data['promotion']['priority_pitch']['release_summary'])
        data = yaml.safe_load((ROOT / 'releases/heijitsu.yaml').read_text())
        self.assertEqual([p['language'] for p in release_pitch(ROOT, data)], ['en', 'ja'])
