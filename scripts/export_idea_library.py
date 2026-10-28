#!/usr/bin/env python3
"""Export a deliberately small public reading library; never copy private runtime files."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

INDEX_FIELDS = ('idea_id', 'ticker', 'snapshot', 'version', 'rank', 'total', 'band',
                'eligible_for_ranking', 'status', 'source_article_id', 'reading_page',
                'as_of_session', 'last_research_updated_at', 'known_subtotal', 'possible_range')
SNAPSHOT_FIELDS = ('idea_id', 'version', 'created_at', 'as_of_session', 'resolution_date',
                   'horizon', 'status', 'target_equities', 'source_article_id', 'thesis',
                   'likelihood', 'score')


def export(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output or output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('Export destination must be separate from the private library')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Export destination must be empty; inspect existing research before replacing it')
    rows = json.loads((source / 'current-snapshot-index.json').read_text())
    files = {'INDEX.md', 'score-table.json', 'current-snapshot-index.json'}
    snapshots, notes, index = {}, {}, []
    for row in rows:
        item = {k: row[k] for k in INDEX_FIELDS if k in row}
        for field in ('reading_page', 'snapshot'):
            relative = item[field]
            path = (source / relative).resolve()
            if Path(relative).is_absolute() or not path.is_relative_to(source) or path.is_symlink():
                raise ValueError('Unsafe library path')
            files.add(relative)
        snapshot = json.loads((source / item['snapshot']).read_text())
        snapshots[item['snapshot']] = {k: snapshot[k] for k in SNAPSHOT_FIELDS if k in snapshot}
        notes[item['reading_page']] = (source / item['reading_page']).read_text()
        index.append(item)
    def clean_link(match, document):
        label, target = match.groups()
        parsed = urlsplit(target)
        if parsed.scheme:
            return match[0] if parsed.scheme in ('http', 'https') else label
        if not parsed.path:
            return match[0]
        path = (source / document).parent / unquote(parsed.path)
        try:
            relative = path.resolve().relative_to(source).as_posix()
        except ValueError:
            return label
        return match[0] if relative in files else label + ' (private supporting record)'
    output.mkdir(parents=True, exist_ok=True)
    def write(name, value):
        path = output / name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding='utf-8')
    for name, note in notes.items():
        note = re.sub(r'\[([^\]\n]+)\]\(([^\s]+?)\)', lambda m: clean_link(m, name), note)
        write(name, note)
    for name, snapshot in snapshots.items():
        write(name, json.dumps(snapshot, indent=2) + '\n')
    write('current-snapshot-index.json', json.dumps(index, indent=2) + '\n')
    write('score-table.json', (source / 'score-table.json').read_text())
    write('INDEX.md', '# AOI investment ideas\n\nPublic reading library. Research dates and missing inputs remain explicit.\n\n' + '\n'.join(f"- [{r['ticker']}: {r['idea_id']}]({r['reading_page']})" for r in index) + '\n')
    return len(index)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, default=Path('research'))
    args = p.parse_args()
    print(f'Exported {export(args.source, args.output)} ideas to {args.output}')
