"""Validated fixed content and pure study functions; no model calls or learner storage."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {'IA-1': (2, 2), 'IA-3': (2, 2), 'IA-4': (2, 2),
            'IB-1': (2, 2), 'IB-2': (2, 1), 'IC-4': (2, 1)}

def validate_bank(bank):
    for kind, count, prefix in [('flashcards', 12, 'FC'), ('questions', 10, 'MCQ')]:
        items = bank.get(kind, [])
        if len(items) != count:
            raise ValueError(f'{kind}: expected {count} items, found {len(items)}')
        for n, item in enumerate(items, 1):
            if item.get('id') != f'{prefix}{n:02}':
                raise ValueError(f'{kind}: IDs must be ordered and unique')
            for field in ['code', 'topic', 'objective', 'source', 'adapted_from']:
                if not isinstance(item.get(field), str) or not item[field].strip():
                    raise ValueError(f'{item["id"]}: missing {field}')
            if item['code'] not in EXPECTED:
                raise ValueError(f'{item["id"]}: unexpected topic')
            if not item.get('reference_pages') or any(type(p) is not int or not 1 <= p <= 47 for p in item['reference_pages']):
                raise ValueError(f'{item["id"]}: invalid reference pages')
            if kind == 'flashcards':
                for field in ['front', 'back']:
                    if not isinstance(item.get(field), str) or not item[field].strip():
                        raise ValueError(f'{item["id"]}: missing {field}')
            else:
                if not item.get('prompt') or item.get('answer') not in ('A', 'B', 'C'):
                    raise ValueError(f'{item["id"]}: invalid prompt or key')
                for field in ['options', 'rationales']:
                    if set(item.get(field, {})) != set('ABC') or not all(isinstance(v, str) and v.strip() for v in item[field].values()):
                        raise ValueError(f'{item["id"]}: expected three {field}')
                if len(set(item['options'].values())) != 3:
                    raise ValueError(f'{item["id"]}: duplicate choices')
        for code, counts in EXPECTED.items():
            if sum(item['code'] == code for item in items) != counts[0 if kind == 'flashcards' else 1]:
                raise ValueError(f'{code}: allocation mismatch in {kind}')
    return bank

def load_bank(path=ROOT / 'content.json'):
    return validate_bank(json.loads(Path(path).read_text(encoding='utf-8')))

def move(index, step, count):
    return max(0, min(count - 1, int(index) + step))

def check_answer(item, choice):
    if choice not in item['options']:
        return {'status': 'Choose an answer', 'message': 'Select A, B, or C, then choose Check Answer.', 'answer': None}
    return {'status': 'Correct' if choice == item['answer'] else 'Incorrect',
            'message': f'You selected {choice}.', 'answer': item['answer']}
