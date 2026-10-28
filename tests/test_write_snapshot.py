import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('write_snapshot', Path(__file__).resolve().parents[1] / 'skills/aoi-develop-ideas/scripts/write_snapshot.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class SnapshotTests(unittest.TestCase):
    def test_retry_preserves_identity_and_changed_creation_time_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'v1.json'
            original = {'version': 1, 'created_at': '2026-10-28T12:00:00Z'}
            self.assertTrue(module.write_snapshot(path, original)['created'])
            before = path.read_bytes()
            self.assertFalse(module.write_snapshot(path, original)['created'])
            with self.assertRaises(ValueError):
                module.write_snapshot(path, dict(original, created_at='2026-10-28T13:00:00Z'))
            self.assertEqual(path.read_bytes(), before)
