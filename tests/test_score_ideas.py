import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('score_ideas', Path(__file__).resolve().parents[1] / 'skills/aoi-develop-ideas/scripts/score_ideas.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def idea(name='a', score=2, **updates):
    result = {'idea_id': name, 'scores': dict.fromkeys(module.WEIGHTS, score), 'valuation_inputs_verified': True, 'eligibility_gates_passed': True, 'missing_required_inputs': []}
    result.update(updates)
    return result


class ScoringTests(unittest.TestCase):
    def test_unknown_valuation_cannot_get_complete_total(self):
        row = idea(valuation_inputs_verified=False)
        with self.assertRaises(ValueError):
            module.score_ideas([row])
        row['scores']['valuation'] = None
        result = module.score_ideas([row])[0]
        self.assertIsNone(result['total'])
        self.assertIsNone(result['rank'])
        self.assertEqual(result['possible_range'], [37.5, 62.5])

    def test_rejected_and_gated_ideas_are_unranked(self):
        rows = [idea('low', 1), idea('missing', 4, missing_required_inputs=['quote']), idea('failed', 4, eligibility_gates_passed=False)]
        self.assertTrue(all(r['rank'] is None for r in module.score_ideas(rows)))

    def test_weights_bands_and_tied_ranking(self):
        rows = module.score_ideas([idea('low'), idea('high', 4), idea('high-tie', 4)])
        self.assertEqual([r['total'] for r in rows], [50, 100, 100])
        self.assertEqual([r['rank'] for r in rows], [3, 1, 1])
        self.assertEqual(rows[0]['band'], 'low priority')

    def test_invalid_scores_and_duplicate_ids(self):
        for bad in (True, -1, 5, 1.5):
            row = idea(); row['scores']['evidence'] = bad
            with self.assertRaises(ValueError):
                module.score_ideas([row])
        with self.assertRaises(ValueError):
            module.score_ideas([idea(), idea()])


if __name__ == '__main__':
    unittest.main()
