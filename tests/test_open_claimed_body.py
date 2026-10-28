import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

DIR = Path(__file__).resolve().parents[1] / 'skills/aoi-develop-ideas/scripts'
spec = importlib.util.spec_from_file_location('open_claimed_body', DIR / 'open_claimed_body.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class GatedBodyTests(unittest.TestCase):
    def test_claim_is_durable_before_body_and_second_call_cannot_open_body(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); db=root/'ledger.sqlite3'; body=root/'body.md'
            subprocess.run([sys.executable,str(DIR/'article_memory.py'),'--db',str(db),'list'],check=True,capture_output=True)
            body.write_text('SYNTHETIC body')
            first=module.open_body(db,'https://seekingalpha.com/article/123-test','run',body,root/'receipts',True)
            claim=Path(first['claim_receipt']); access=json.loads(Path(first['access_receipt']).read_text())
            self.assertEqual(first['body'],'SYNTHETIC body')
            self.assertEqual(access['claim_sha256'],hashlib.sha256(claim.read_bytes()).hexdigest())
            self.assertLessEqual(json.loads(claim.read_text())['recorded_at'],access['started_at'])
            self.assertEqual(access['body_sha256'],hashlib.sha256(body.read_bytes()).hexdigest())
            body.unlink()
            second=module.open_body(db,'https://www.seekingalpha.com/article/123-another-slug','another-run',body,root/'receipts',True)
            self.assertFalse(second['body_opened'])
            self.assertNotIn('body',second)
            self.assertEqual(len(list((root/'receipts').glob('*-access.json'))),1)

    def test_missing_ledger_is_not_silently_created(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaises(ValueError):
                module.open_body(root/'missing.sqlite3','https://seekingalpha.com/article/123-test','run',root/'body.md',root/'receipts',True)
            self.assertFalse((root/'missing.sqlite3').exists())
