#!/usr/bin/env python3
"""Create a JSON snapshot once; accept identical retries and reject changed history."""
import argparse
import hashlib
import json
from pathlib import Path


def write_snapshot(path, value):
    path = Path(path)
    payload = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb') as handle:
            handle.write(payload)
        created = True
    except FileExistsError:
        if path.read_bytes() != payload:
            raise ValueError('Snapshot already exists with different bytes; append a new version with prior_snapshot')
        created = False
    return {'path': str(path), 'created': created, 'sha256': hashlib.sha256(payload).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(write_snapshot(args.output, json.loads(args.input.read_text()))))
