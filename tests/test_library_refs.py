import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

DIR=Path(__file__).resolve().parents[1]/'skills/aoi-develop-ideas/scripts'
spec=importlib.util.spec_from_file_location('check_library_refs',DIR/'check_library_refs.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class LibraryReferenceTests(unittest.TestCase):
    def test_copied_snapshot_must_have_sources_at_its_own_relative_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); snapshot=root/'site/files/ideas/ONE/snapshots/v1.json';snapshot.parent.mkdir(parents=True)
            snapshot.write_text(json.dumps({'tldr':{'targets':[{'ratings':[{'receipt':'../../../sources/ratings.md#panel'}]}]}}))
            other=root/'public/sources/ratings.md';other.parent.mkdir(parents=True);other.write_text('# Panel')
            report=module.audit(root)
            self.assertEqual(report['status'],'revise')
            self.assertEqual(report['errors'][0]['file'],'site/files/ideas/ONE/snapshots/v1.json')
            correct=root/'site/files/sources/ratings.md';correct.parent.mkdir(parents=True);correct.write_text('# Panel')
            self.assertEqual(module.audit(root)['status'],'pass')
            correct.write_text('# Different section')
            self.assertEqual(module.audit(root)['errors'][0]['error'],'missing Markdown fragment')

    def test_scenario_and_hypothetical_calculation_links_are_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'snapshot.json').write_text(json.dumps({'scenarios': {'hypothetical': {'calculation': 'missing.json'}}, 'tldr': {'annual_return': {'hypothetical_calculation': 'also-missing.json'}}}))
            report = module.audit(root)
            self.assertEqual({e['target'] for e in report['errors']}, {'missing.json','also-missing.json'})

    def test_json_fragments_and_external_fixture_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'model.json').write_text('{"models":{"bear":{}}}')
            (root/'idea.json').write_text(json.dumps({'tldr':{'model':'model.json#models/bear','source':'https://source.invalid/receipt'}}))
            self.assertEqual(module.audit(root)['status'],'pass')
            (root/'idea.json').write_text(json.dumps({'tldr':{'model':'model.json#models/missing'}}))
            self.assertEqual(module.audit(root)['errors'][0]['error'],'missing JSON fragment')
