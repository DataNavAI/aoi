import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('export_idea_library', Path(__file__).resolve().parents[1] / 'scripts/export_idea_library.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExportTests(unittest.TestCase):
    def test_public_export_preserves_unknown_scores_and_omits_private_support(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'private'; output = root / 'public'
            (source / 'ideas/ONE').mkdir(parents=True)
            (source / 'ideas/ONE/IDEA.md').write_text('# ONE\n[Source](https://seekingalpha.com/article/123)\n[Secret](../../private.json)\n[Snapshot](snapshot.json)\n')
            (source / 'ideas/ONE/snapshot.json').write_text(json.dumps({'idea_id':'ONE','thesis':'Test', 'score':{'total':None}, 'extraction_path':'/private/extraction.json'}))
            (source / 'current-snapshot-index.json').write_text(json.dumps([{'idea_id':'ONE','ticker':'ONE','reading_page':'ideas/ONE/IDEA.md','snapshot':'ideas/ONE/snapshot.json','prior_snapshot':'/private/history.json'}]))
            (source / 'score-table.json').write_text('{"ideas": [{"idea_id":"ONE","total":null}]}')
            (source / 'private.json').write_text('PRIVATE')
            (source / 'article-memory.sqlite3').write_text('PRIVATE')
            self.assertEqual(module.export(source, output), 1)
            text = (output / 'ideas/ONE/IDEA.md').read_text()
            self.assertIn('https://seekingalpha.com/article/123', text)
            self.assertIn('[Snapshot](snapshot.json)', text)
            self.assertNotIn('../../private.json', text)
            self.assertFalse((output / 'private.json').exists())
            self.assertFalse((output / 'article-memory.sqlite3').exists())
            snapshot = json.loads((output / 'ideas/ONE/snapshot.json').read_text())
            self.assertIsNone(snapshot['score']['total'])
            self.assertNotIn('extraction_path', snapshot)
            self.assertNotIn('prior_snapshot', json.loads((output / 'current-snapshot-index.json').read_text())[0])
            with self.assertRaises(ValueError):
                module.export(source, output)

    def test_export_cannot_replace_private_source(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                module.export(directory, directory)
