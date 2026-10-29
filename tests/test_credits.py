"""Exercise the catalog command against explicit credit roles and conflicts."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


class CreditValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        source = Path(__file__).resolve().parents[1]
        shutil.copytree(source / 'scripts', self.root / 'scripts')
        (self.root / 'artists').mkdir()
        (self.root / 'releases').mkdir()
        (self.root / 'artists/example.yaml').write_text('id: example\nname: Example\n')
        self.track = {'title': 'Example', 'isrc': 'AA1234567890'}

    def check(self):
        release = {'id': 'example', 'artist_id': 'example', 'tracks': [self.track]}
        (self.root / 'releases/example.yaml').write_text(yaml.safe_dump(release))
        return subprocess.run([sys.executable, str(self.root / 'scripts/validate_catalog.py')],
                              capture_output=True, text=True)

    def test_missing_roles_are_allowed_and_each_role_requires_named_arrays(self):
        self.assertEqual(self.check().returncode, 0)
        for role in ('songwriters', 'lyricists', 'composers', 'vocalists'):
            for invalid in ('Name', [None], [' ']):
                with self.subTest(role=role, invalid=invalid):
                    self.track['credits'] = {role: invalid}
                    result = self.check()
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(f'credits.{role}', result.stdout)
            self.track['credits'] = {role: ['Original Name']}
            self.assertEqual(self.check().returncode, 0)

    def test_confirmed_instrumental_cannot_name_a_singer(self):
        self.track['instrumental'] = {'basis': 'owner_confirmation', 'confirmed_on': '2026-10-28'}
        self.track['credits'] = {'composers': ['Composer'], 'vocalists': []}
        self.assertEqual(self.check().returncode, 0)
        self.track['credits']['vocalists'] = ['Singer']
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('vocalists conflicts with instrumental', result.stdout)
