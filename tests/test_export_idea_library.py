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
            (source / 'ideas/ONE/snapshot.json').write_text(json.dumps({'idea_id':'ONE','thesis':'Test', 'synthetic':True, 'as_of':'2026-10-26', 'source_cutoff':'2026-10-26T16:30:00-04:00', 'score':{'total':None}, 'tldr':{'idea':'Test thesis','targets':[{'annual_return':{'status':'unavailable','reason':'No current quote'}}]}, 'extraction_path':'/private/extraction.json'}))
            (source / 'current-snapshot-index.json').write_text(json.dumps([{'idea_id':'ONE','ticker':'ONE','reading_page':'ideas/ONE/IDEA.md','snapshot':'ideas/ONE/snapshot.json','prior_snapshot':'/private/history.json'}]))
            (source / 'score-table.json').write_text('{"ideas": [{"idea_id":"ONE","total":null}]}')
            (source / 'INDEX.md').write_text('# Idea index\n\n## Incomplete, not investment ranks\n\n| Idea | Known subtotal | Status | Risk |\n|---|---|---|---|\n| [ONE](ideas/ONE/IDEA.md) | 40 / 100, incomplete | Needs evidence | Missing valuation |\n\n[Private receipt](private.json)\n')
            (source / 'private.json').write_text('PRIVATE')
            (source / 'article-memory.sqlite3').write_text('PRIVATE')
            self.assertEqual(module.export(source, output), 1)
            text = (output / 'ideas/ONE/IDEA.md').read_text()
            self.assertIn('https://seekingalpha.com/article/123', text)
            self.assertIn('[Snapshot](snapshot.json)', text)
            self.assertNotIn('../../private.json', text)
            index = (output / 'INDEX.md').read_text()
            self.assertIn('40 / 100, incomplete', index)
            self.assertIn('not investment ranks', index)
            self.assertIn('[ONE](ideas/ONE/IDEA.md)', index)
            self.assertNotIn('](private.json)', index)
            self.assertFalse((output / 'private.json').exists())
            self.assertFalse((output / 'article-memory.sqlite3').exists())
            snapshot = json.loads((output / 'ideas/ONE/snapshot.json').read_text())
            self.assertIsNone(snapshot['score']['total'])
            self.assertTrue(snapshot['synthetic'])
            self.assertIn('not live market research', snapshot['research_scope'])
            self.assertEqual(snapshot['source_cutoff'], '2026-10-26T16:30:00-04:00')
            self.assertEqual(snapshot['tldr']['targets'][0]['annual_return']['reason'], 'No current quote')
            self.assertNotIn('extraction_path', snapshot)
            self.assertNotIn('prior_snapshot', json.loads((output / 'current-snapshot-index.json').read_text())[0])
            with self.assertRaises(ValueError):
                module.export(source, output)

    def test_standalone_snapshot_retains_research_fields_and_public_lineage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'private'; output = root / 'public'
            folder = source / 'ideas/ONE'; folder.mkdir(parents=True)
            (folder / 'IDEA.md').write_text('# ONE')
            required = {'prior_snapshot':'v1.json', 'variant_perception':'Unestablished',
                        'success_event':'Positive net return by resolution', 'execution_status':'not-executed',
                        'evidence_ids':['E1'], 'catalysts':[], 'falsifiers':['Cancellation'],
                        'scenarios':{'current':{'status':'unavailable','reason':'Missing bridge'}},
                        'entry_conditions':{'later':'Not established'}, 'next_review':'After next filing'}
            (folder / 'v2.json').write_text(json.dumps(dict(required, idea_id='ONE', version=2)))
            (folder / 'v1.json').write_text(json.dumps({'idea_id':'ONE','version':1,'prior_snapshot':None,'extraction_path':'PRIVATE'}))
            (source / 'current-snapshot-index.json').write_text(json.dumps([{'idea_id':'ONE','ticker':'ONE','reading_page':'ideas/ONE/IDEA.md','snapshot':'ideas/ONE/v2.json'}]))
            (source / 'score-table.json').write_text('{"ideas": []}')
            module.export(source, output)
            current = json.loads((output / 'ideas/ONE/v2.json').read_text())
            for field, value in required.items():
                self.assertEqual(current[field], value)
            prior = json.loads((output / 'ideas/ONE' / current['prior_snapshot']).read_text())
            self.assertEqual(prior['version'], 1)
            self.assertNotIn('extraction_path', prior)

    def test_export_cannot_replace_private_source(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                module.export(directory, directory)
