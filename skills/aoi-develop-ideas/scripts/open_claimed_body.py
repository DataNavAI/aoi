#!/usr/bin/env python3
"""Gate reading a lawful saved body behind a durable canonical claim receipt.

This proves local operation order, not the source's original web retrieval time.
Use --synthetic for fixture bodies. It never writes a body copy into the receipts.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid


def now():
    return datetime.now(timezone.utc).isoformat()


def write_new(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
        f.flush()
        import os
        os.fsync(f.fileno())


def open_body(db, url, run, body_file, receipts, synthetic=False, retry_blocked=False):
    db, body_file, receipts = Path(db).resolve(), Path(body_file).absolute(), Path(receipts).resolve()
    if not db.is_file():
        raise ValueError('Existing persistent ledger is required')
    receipts.mkdir(parents=True, exist_ok=True)
    invocation = uuid.uuid4().hex
    command = [sys.executable, str(Path(__file__).with_name('article_memory.py')),
               '--db', str(db), 'claim', url, '--run', run]
    if retry_blocked:
        command.append('--retry-blocked')
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    result = json.loads(completed.stdout)
    claim_path = receipts / (invocation + '-claim.json')
    claim = {'operation': 'canonical-claim', 'recorded_at': now(), 'synthetic': synthetic,
             'command': command, 'stdout': completed.stdout, 'result': result,
             'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    write_new(claim_path, claim)
    # Do not even inspect the body file's existence, metadata or bytes on a declined claim.
    if result.get('claimed') is not True:
        return {'claimed': False, 'body_opened': False, 'claim_receipt': str(claim_path),
                'article': result.get('article')}
    started = now()
    try:
        body = body_file.read_bytes()
    except OSError as error:
        write_new(receipts / (invocation + '-access.json'), {
            'operation':'local-body-read-failed', 'started_at':started, 'finished_at':now(),
            'synthetic':synthetic, 'claim_receipt':claim_path.name, 'error':str(error)})
        raise
    access_path = receipts / (invocation + '-access.json')
    write_new(access_path, {'operation':'local-body-open', 'started_at':started, 'finished_at':now(),
        'synthetic':synthetic, 'claim_receipt':claim_path.name,
        'claim_sha256':hashlib.sha256(claim_path.read_bytes()).hexdigest(),
        'body_file':str(body_file), 'body_sha256':hashlib.sha256(body).hexdigest(),
        'bytes':len(body), 'scope':'local saved body access; original web retrieval clock not established'})
    return {'claimed': True, 'body_opened': True, 'claim_receipt': str(claim_path),
            'access_receipt': str(access_path), 'body': body.decode('utf-8')}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', required=True, type=Path)
    p.add_argument('--url', required=True)
    p.add_argument('--run', required=True)
    p.add_argument('--body-file', required=True, type=Path)
    p.add_argument('--receipts', required=True, type=Path)
    p.add_argument('--synthetic', action='store_true')
    p.add_argument('--retry-blocked', action='store_true')
    a = p.parse_args()
    print(json.dumps(open_body(a.db,a.url,a.run,a.body_file,a.receipts,a.synthetic,a.retry_blocked),indent=2))


if __name__ == '__main__':
    main()
