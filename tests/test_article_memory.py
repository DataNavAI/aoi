"""Behavior checks for durable article identity and processing transitions."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/aoi-develop-ideas/scripts/article_memory.py'
URL = 'https://seekingalpha.com/article/12345-original?source=tracking'


class ArticleMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='aoi-memory-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / 'memory.sqlite3'

    def call(self, *args, success=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--db', str(self.db), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stderr)
        return json.loads(result.stdout) if success else result.stderr

    def record(self, name, **fields):
        path = self.root / name
        path.write_text(json.dumps({'article_id': '12345', **fields}))
        return str(path)

    def read(self, run='owner'):
        path = self.record('read.json', read_at='2026-10-26T21:00:00-07:00', body_access='full', author_thesis='Synthetic workflow fixture', locators=['body section'], ideas=[])
        return self.call('read', URL, '--run', run, '--record', path)

    def test_atomic_claim_and_url_alias(self):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            results = list(pool.map(lambda n: self.call('claim', URL, '--run', str(n)), range(4)))
        self.assertEqual(sum(r['claimed'] for r in results), 1)
        alias = self.call('claim', 'https://www.seekingalpha.com/article/12345-new-slug?x=1', '--run', 'new')
        self.assertFalse(alias['claimed'])
        self.assertEqual(len(self.call('list')['articles']), 1)

    def test_mined_is_terminal_across_processes(self):
        self.call('claim', URL, '--run', 'owner')
        self.read()
        idea = self.root / 'idea.json'
        idea.write_text('{}')
        result = self.record('result.json', reason='Fixture completed', idea_paths=[str(idea)])
        self.call('finish', URL, '--run', 'owner', '--status', 'mined', '--record', result)
        self.assertFalse(self.call('claim', URL, '--run', 'next')['claimed'])
        self.call('finish', URL, '--run', 'owner', '--status', 'mined', '--record', result, success=False)
        self.assertEqual([e['action'] for e in self.call('list')['events']].count('mined'), 1)

    def test_claim_owner_and_saved_read_are_enforced(self):
        self.call('claim', URL, '--run', 'owner')
        self.call('read', URL, '--run', 'intruder', '--record', self.record('bad.json'), success=False)
        self.read()
        self.assertFalse(self.call('claim', URL, '--run', 'restarted')['claimed'])
        saved = self.call('list')['articles'][0]
        self.assertEqual(saved['state'], 'read')
        self.assertTrue(Path(saved['extraction_path']).is_file())
        self.call('read', URL, '--run', 'owner', '--record', saved['extraction_path'], success=False)
        self.call('finish', URL, '--run', 'owner', '--status', 'blocked', '--record', self.record('blocked.json', reason='cannot reread'), success=False)

    def test_unread_blocked_retry_is_explicit(self):
        self.call('claim', URL, '--run', 'owner')
        record = self.record('blocked.json', reason='Login needed')
        self.call('finish', URL, '--run', 'owner', '--status', 'blocked', '--record', record)
        self.assertFalse(self.call('claim', URL, '--run', 'next')['claimed'])
        self.assertTrue(self.call('claim', URL, '--run', 'next', '--retry-blocked')['claimed'])

    def test_incomplete_or_missing_outputs_cannot_be_mined(self):
        self.call('claim', URL, '--run', 'owner')
        invalid = self.record('teaser.json', read_at='2026-10-26T21:00:00-07:00', body_access='teaser', author_thesis='headline only', locators=['title'], ideas=[])
        self.call('read', URL, '--run', 'owner', '--record', invalid, success=False)
        result = self.record('result.json', reason='not created', idea_paths=[str(self.root / 'missing.json')])
        self.call('finish', URL, '--run', 'owner', '--status', 'mined', '--record', result, success=False)
        self.read()
        self.call('finish', URL, '--run', 'owner', '--status', 'mined', '--record', result, success=False)

    def test_reject_is_terminal_and_bad_origins_fail(self):
        self.call('claim', 'https://other.example/article/12345', '--run', 'owner', success=False)
        self.call('claim', URL, '--run', 'owner')
        result = self.record('reject.json', reason='Outside equity universe')
        self.call('finish', URL, '--run', 'owner', '--status', 'rejected', '--record', result)
        self.assertFalse(self.call('claim', URL, '--run', 'next')['claimed'])


if __name__ == '__main__':
    unittest.main()
