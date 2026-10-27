import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('build_idea_site', Path(__file__).resolve().parents[1] / 'scripts/build_idea_site.py')
site = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(site)


class IdeaSiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='aoi-site-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'research'
        self.source.mkdir()
        self.output = self.root / 'site'

    def fixture(self, identity='ONE', total=None, known=40, gate=True):
        page = self.source / 'ideas' / identity / 'IDEA.md'
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text('# Example (ONE): a thesis\n\nA source-derived thesis.\n\n## Evidence\n\n| Fact | Implication |\n| --- | --- |\n| **Original** | Contrary evidence matters. |\n\n## Next checks\n\n1. Verify the source.\n\n2. Check costs.\n')
        index = [{'idea_id': identity, 'ticker': 'ONE', 'reading_page': str(page.relative_to(self.source)), 'as_of_session': '2026-10-26'}]
        (self.source / 'current-snapshot-index.json').write_text(json.dumps(index))
        (self.source / 'score-table.json').write_text(json.dumps({'ideas': [{'idea_id': identity, 'total': total, 'known_subtotal': known, 'possible_range': [known, known + 25], 'scores': {'evidence': 3, 'valuation': None}, 'eligibility_gates_passed': gate, 'eligible_for_ranking': False}]}))
        return page

    def data(self):
        html = (self.output / 'index.html').read_text()
        payload = html.split('<script id="idea-data" type="application/json">', 1)[1].split('</script>', 1)[0]
        return json.loads(payload)

    def test_missing_total_stays_missing_and_source_is_unchanged(self):
        self.fixture()
        before = {str(p): p.read_bytes() for p in self.source.rglob('*') if p.is_file()}
        manifest = site.build(self.source, self.output)
        idea = self.data()['ideas'][0]
        self.assertIsNone(idea['total'])
        self.assertEqual(idea['known'], 40)
        self.assertEqual(idea['group'], 'incomplete')
        self.assertIn('<table>', idea['sections'][1]['html'])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.source.rglob('*') if p.is_file()})
        self.assertEqual(manifest['idea_count'], 1)
        self.assertTrue((self.output / idea['staticUrl']).is_file())
        self.assertTrue((self.output / idea['markdownUrl']).is_file())

    def test_untrusted_content_and_links_are_inert(self):
        page = self.fixture()
        page.write_text('# </script><script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n\n[Bad](javascript:alert) [Malformed](https://[) [Remote](https://example.com/proof) [Encoded](%2e%2e/%2e%2e/%2e%2e/secret.txt)\n')
        (self.root / 'secret.txt').write_text('DO NOT COPY')
        site.build(self.source, self.output)
        text = (self.output / 'index.html').read_text()
        self.assertNotIn('</script><script>alert', text)
        data = self.data()['ideas'][0]['sections'][0]['html']
        self.assertNotIn('<img', data)
        self.assertIn('&lt;img', data)
        self.assertNotIn('href="javascript:', data)
        self.assertIn('rel="noopener noreferrer"', data)
        self.assertFalse(any('DO NOT COPY' in p.read_text(errors='ignore') for p in self.output.rglob('*') if p.is_file()))

    def test_reference_pages_are_portable_and_symlinks_cannot_escape(self):
        page = self.fixture()
        (self.source / 'AUDIT.md').write_text('# Supporting record\n\n[Home](INDEX.md) [Data](facts.json)\n')
        (self.source / 'INDEX.md').write_text('# Library')
        (self.source / 'facts.json').write_text('{"evidence": true}')
        outside = self.root / 'secret.json'; outside.write_text('{"secret": true}')
        (self.source / 'outside.json').symlink_to(outside)
        with page.open('a') as out:
            out.write('\n[Audit](../../AUDIT.md) [Hidden](../../outside.json)\n')
        result = site.build(self.source, self.output)
        reference = (self.output / 'reference/AUDIT.html').read_text()
        self.assertIn('href="../index.html"', reference)
        self.assertIn('href="../files/facts.json"', reference)
        self.assertTrue((self.output / 'files/facts.json').is_file())
        self.assertFalse((self.output / 'files/outside.json').exists())
        self.assertTrue(result['warnings'])

    def test_uses_authoritative_weights_instead_of_normalizing_missing_data(self):
        self.fixture()
        payload = json.loads((self.source / 'score-table.json').read_text())
        payload['weights'] = {'evidence': 30, 'valuation': 20, 'mechanism': 15, 'catalysts': 10, 'downside': 15, 'implementation': 10}
        (self.source / 'score-table.json').write_text(json.dumps(payload))
        site.build(self.source, self.output)
        self.assertEqual(self.data()['ideas'][0]['weights']['valuation'], 20)
        self.assertIsNone(self.data()['ideas'][0]['total'])
        payload['weights']['valuation'] = 25
        (self.source / 'score-table.json').write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, 'sum to 100'):
            site.build(self.source, self.output)

    def test_plain_markdown_library_works_without_metadata(self):
        page = self.source / 'ideas/PLAIN/IDEA.md'; page.parent.mkdir(parents=True)
        page.write_text('# A plain note\n\nNo score has been assigned.\n')
        site.build(self.source, self.output)
        idea = self.data()['ideas'][0]
        self.assertIsNone(idea['known'])
        self.assertIsNone(idea['total'])
        self.assertEqual(idea['ticker'], 'PLAIN')

    def test_markdown_section_and_cross_idea_links_keep_app_navigation(self):
        page = self.fixture()
        other = self.source / 'ideas/OTHER/IDEA.md'; other.parent.mkdir(parents=True)
        other.write_text('# Other idea\n\n## Evidence\n\nA second note.\n')
        with page.open('a') as out:
            out.write('\n[Next](#next-checks) [Compare](../OTHER/IDEA.md#evidence)\n')
        site.build(self.source, self.output)
        rendered = ''.join(section['html'] for section in self.data()['ideas'][0]['sections'])
        self.assertIn('idea=ONE', rendered)
        self.assertIn('section=next-checks', rendered)
        self.assertIn('idea=OTHER', rendered)
        self.assertIn('section=evidence', rendered)
        standalone = (self.output / 'ideas/ONE/index.html').read_text()
        self.assertIn('href="#next-checks"', standalone)

    def test_ineligible_is_distinct_from_incomplete(self):
        self.fixture(gate=False)
        site.build(self.source, self.output)
        self.assertEqual(self.data()['ideas'][0]['group'], 'ineligible')

    def test_zero_complete_score_remains_zero_and_is_not_rank_eligible(self):
        self.fixture(total=0, known=0)
        payload = json.loads((self.source / 'score-table.json').read_text())
        payload['ideas'][0]['band'] = 'reject/defer'
        payload['ideas'][0]['scores'] = dict.fromkeys(site.LABELS, 0)
        (self.source / 'score-table.json').write_text(json.dumps(payload))
        site.build(self.source, self.output)
        idea = self.data()['ideas'][0]
        self.assertEqual(idea['total'], 0)
        self.assertEqual(idea['group'], 'ineligible')

    def test_dotted_idea_ids_have_safe_static_pages(self):
        self.fixture(identity='SA-BRK.B')
        site.build(self.source, self.output)
        self.assertTrue((self.output / 'ideas/SA-BRK.B/index.html').is_file())

    def test_rebuild_removes_stale_generated_files_but_protects_user_files(self):
        page = self.fixture()
        site.build(self.source, self.output)
        generated = self.output / 'ideas/ONE/index.html'
        self.assertTrue(generated.exists())
        page.unlink(); (self.source / 'current-snapshot-index.json').write_text('[]')
        site.build(self.source, self.output)
        self.assertFalse(generated.exists())
        user_file = self.output / 'my-notes.txt'; user_file.write_text('Keep this')
        with self.assertRaisesRegex(ValueError, 'not owned'):
            site.build(self.source, self.output)
        self.assertEqual(user_file.read_text(), 'Keep this')

    def test_rejects_bad_source_paths_and_unmanaged_output(self):
        self.fixture()
        self.output.mkdir(); (self.output / 'important.txt').write_text('Keep')
        with self.assertRaisesRegex(ValueError, 'non-generated'):
            site.build(self.source, self.output)
        with self.assertRaises(ValueError):
            site.build(self.source, self.source)
        index = [{'idea_id': 'BAD', 'reading_page': '../secret.md'}]
        (self.source / 'current-snapshot-index.json').write_text(json.dumps(index))
        with self.assertRaisesRegex(ValueError, 'leaves source'):
            site.build(self.source, self.root / 'other-output')

    def test_empty_library_renders_a_valid_offline_page(self):
        result = site.build(self.source, self.output)
        self.assertEqual(result['idea_count'], 0)
        self.assertEqual(self.data()['ideas'], [])
        self.assertIn('No ideas yet.', (self.output / 'index.html').read_text())


if __name__ == '__main__':
    unittest.main()
