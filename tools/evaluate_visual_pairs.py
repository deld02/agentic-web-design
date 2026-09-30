"""Score blind reviewer decisions against separately curated human judgments.

No generated ground truth or universal premium score. Reference format:
{"pairs": [{"id": "P01", "winner": "A", "category": "minimal_vs_empty"}]}.
Predictions: {"pairs": [{"id": "P01", "winner": "B", "reason": "Visible ..."}]}.
Give the reviewer only independently prepared A/B images and project context,
never the reference answers. This scorer does not run or certify the reviewer.
"""
import argparse
import json
from pathlib import Path


def score(reference: dict, predictions: dict) -> dict:
    def index(data, human=False):
        rows = data.get('pairs')
        if not isinstance(rows, list) or not rows:
            raise ValueError('pairs must be a nonempty list')
        result = {}
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError('pair must be an object')
            ident = row.get('id')
            if not isinstance(ident, str) or not ident or ident in result:
                raise ValueError('pair IDs must be unique and nonempty')
            if row.get('winner') not in {'A', 'B', 'TIE'}:
                raise ValueError('winner must be A, B or TIE')
            field = 'category' if human else 'reason'
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f'pair requires {field}')
            result[ident] = row
        return result
    expected, actual = index(reference, True), index(predictions)
    if expected.keys() != actual.keys():
        raise ValueError('predictions must cover exactly the reference pair IDs')
    groups = {}
    misses = []
    for ident, row in expected.items():
        group = groups.setdefault(row['category'], {'pairs': 0, 'agreements': 0})
        group['pairs'] += 1
        if row['winner'] == actual[ident]['winner']:
            group['agreements'] += 1
        else:
            misses.append(ident)
    return {'pairs': len(expected), 'agreements': len(expected)-len(misses),
            'disagreements': misses, 'by_category': groups,
            'limitation': 'Agreement with this human-curated set only; not proof of universal aesthetic quality.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--predictions', type=Path, required=True)
    args = parser.parse_args()
    result = score(json.loads(args.reference.read_text(encoding='utf-8')),
                   json.loads(args.predictions.read_text(encoding='utf-8')))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
