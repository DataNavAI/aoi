#!/usr/bin/env python3
"""Durable, atomic Seeking Alpha article deduplication. Uses Python stdlib only."""
import argparse
import datetime
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit


def article_id(url):
    parts = urlsplit(url)
    if parts.scheme not in ('http', 'https') or parts.hostname not in ('seekingalpha.com', 'www.seekingalpha.com'):
        raise ValueError('Expected a Seeking Alpha article URL')
    match = re.match(r'^/article/(\d+)(?:[-/]|$)', parts.path)
    if not match:
        raise ValueError('URL has no Seeking Alpha article ID')
    return match.group(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    for command in ('claim', 'read', 'finish'):
        p = sub.add_parser(command)
        p.add_argument('url')
        p.add_argument('--run', required=True)
        if command == 'claim':
            p.add_argument('--retry-blocked', action='store_true')
        else:
            p.add_argument('--record', required=True)
        if command == 'finish':
            p.add_argument('--status', required=True, choices=('mined', 'rejected', 'blocked'))
    args = parser.parse_args()
    db = Path(args.db).expanduser().resolve()
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute('CREATE TABLE IF NOT EXISTS articles (article_id TEXT PRIMARY KEY, canonical_url TEXT NOT NULL, state TEXT NOT NULL, run_id TEXT NOT NULL, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, read_at TEXT, extraction_path TEXT, result_path TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS events (event_id INTEGER PRIMARY KEY, article_id TEXT NOT NULL, at TEXT NOT NULL, run_id TEXT NOT NULL, action TEXT NOT NULL, record_path TEXT)')
    if args.command == 'list':
        print(json.dumps({'articles': [dict(r) for r in conn.execute('SELECT * FROM articles ORDER BY article_id')], 'events': [dict(r) for r in conn.execute('SELECT * FROM events ORDER BY event_id')]}, indent=2))
        return
    aid = article_id(args.url)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record_path, record = None, None
    if args.command != 'claim':
        path = Path(args.record).expanduser().resolve()
        record = json.loads(path.read_text())
        record_path = str(path)
        if str(record.get('article_id')) != aid:
            raise ValueError('Record article_id does not match URL')
    conn.execute('BEGIN IMMEDIATE')
    try:
        row = conn.execute('SELECT * FROM articles WHERE article_id=?', (aid,)).fetchone()
        claimed = False
        event = None
        if args.command == 'claim':
            if row is None:
                conn.execute('INSERT INTO articles VALUES (?,?,?,?,?,?,NULL,NULL,NULL)', (aid, 'https://seekingalpha.com/article/' + aid, 'claimed', args.run, now, now))
                claimed, event = True, 'claimed'
            elif row['state'] == 'blocked' and row['read_at'] is None and args.retry_blocked:
                conn.execute('UPDATE articles SET state=?,run_id=?,last_seen=?,result_path=NULL WHERE article_id=?', ('claimed', args.run, now, aid))
                claimed, event = True, 'retry-unread-blocked'
            else:
                conn.execute('UPDATE articles SET last_seen=? WHERE article_id=?', (now, aid))
        else:
            if row is None or row['run_id'] != args.run:
                raise ValueError('Only the existing claim owner may advance this article')
            if row['state'] in ('mined', 'rejected', 'blocked'):
                raise ValueError('Terminal record cannot be processed again')
            if args.command == 'read':
                if row['state'] != 'claimed' or row['read_at'] is not None:
                    raise ValueError('Article reading already recorded; reuse extraction')
                for field in ('read_at', 'body_access', 'author_thesis', 'locators', 'ideas'):
                    if field not in record:
                        raise ValueError('Missing extraction field: ' + field)
                if record['body_access'] not in ('full', 'sufficient-body') or not record['author_thesis'] or not record['locators']:
                    raise ValueError('A readable thesis-bearing body and locators are required')
                conn.execute('UPDATE articles SET state=?,read_at=?,extraction_path=?,last_seen=? WHERE article_id=?', ('read', record['read_at'], record_path, now, aid))
                event = 'read'
            else:
                if not record.get('reason'):
                    raise ValueError('Result requires a reason')
                if args.status == 'mined':
                    if row['state'] != 'read' or not record.get('idea_paths'):
                        raise ValueError('Mining requires a saved reading and nonempty idea paths')
                    for name in record['idea_paths']:
                        target = Path(name)
                        if not target.is_absolute():
                            target = Path(record_path).parent / target
                        if not target.is_file():
                            raise ValueError('Idea file missing: ' + name)
                if args.status == 'blocked' and row['read_at'] is not None:
                    raise ValueError('Already read; resume from saved extraction')
                conn.execute('UPDATE articles SET state=?,result_path=?,last_seen=? WHERE article_id=?', (args.status, record_path, now, aid))
                event = args.status
        if event:
            conn.execute('INSERT INTO events(article_id,at,run_id,action,record_path) VALUES (?,?,?,?,?)', (aid, now, args.run, event, record_path))
        result = dict(conn.execute('SELECT * FROM articles WHERE article_id=?', (aid,)).fetchone())
        conn.execute('COMMIT')
    except Exception:
        conn.execute('ROLLBACK')
        raise
    print(json.dumps({'claimed': claimed, 'article': result}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError, sqlite3.Error) as error:
        raise SystemExit(str(error))
