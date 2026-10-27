#!/usr/bin/env python3
"""Compute AOI rubric totals and ranks without promoting incomplete ideas."""
import argparse
import json

WEIGHTS = {'evidence': 25, 'valuation': 25, 'mechanism': 15, 'catalysts': 10, 'downside': 15, 'implementation': 10}


def score_ideas(ideas):
    results = []
    ids = set()
    for idea in ideas:
        identity = idea['idea_id']
        if identity in ids:
            raise ValueError('Duplicate idea_id: ' + identity)
        ids.add(identity)
        scores = idea['scores']
        if set(scores) != set(WEIGHTS):
            raise ValueError('Exactly the six rubric dimension names are required')
        for name, score in scores.items():
            if score is not None and (type(score) is not int or not 0 <= score <= 4):
                raise ValueError('Scores must be integer 0–4 or null: ' + name)
        for field in ('valuation_inputs_verified', 'eligibility_gates_passed'):
            if type(idea.get(field)) is not bool:
                raise ValueError('Explicit boolean required: ' + field)
        if not isinstance(idea.get('missing_required_inputs'), list):
            raise ValueError('Explicit missing_required_inputs list required')
        if not idea['valuation_inputs_verified'] and scores['valuation'] is not None:
            raise ValueError('Unavailable required valuation inputs require an unscored valuation dimension')
        subtotal = sum(WEIGHTS[k] * v / 4 for k, v in scores.items() if v is not None)
        unknown_weight = sum(WEIGHTS[k] for k, v in scores.items() if v is None)
        total = None if unknown_weight else subtotal
        if total is None:
            band = 'incomplete'
        elif total >= 80:
            band = 'high-priority diligence'
        elif total >= 65:
            band = 'watchlist/further diligence'
        elif total >= 50:
            band = 'low priority'
        else:
            band = 'reject/defer'
        eligible = bool(total is not None and total >= 50 and idea['eligibility_gates_passed'] and not idea['missing_required_inputs'])
        results.append({**idea, 'contributions': {k: None if v is None else WEIGHTS[k] * v / 4 for k, v in scores.items()}, 'known_subtotal': subtotal, 'possible_range': [subtotal, subtotal + unknown_weight], 'total': total, 'band': band, 'eligible_for_ranking': eligible, 'rank': None})
    ranked = sorted((r for r in results if r['eligible_for_ranking']), key=lambda r: (r['total'], r['scores']['evidence'], r['scores']['downside']), reverse=True)
    previous, rank = None, None
    for position, row in enumerate(ranked, 1):
        key = (row['total'], row['scores']['evidence'], row['scores']['downside'])
        if key != previous:
            rank = position
        row['rank'] = rank
        previous = key
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='JSON array of idea scoring inputs; output is JSON on stdout')
    args = parser.parse_args()
    with open(args.input) as stream:
        inputs = json.load(stream)
    print(json.dumps({'rubric_version': 1, 'weights': WEIGHTS, 'ideas': score_ideas(inputs)}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit(str(error))
