#!/usr/bin/env python3
"""Build a private, offline-capable static browser from AOI's Markdown idea library."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from html import escape
import json
import math
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import quote, unquote, urlencode, urlsplit
import os
import posixpath

ASSETS = Path(__file__).resolve().parents[1] / 'web' / 'idea-browser'
MARKER = '.aoi-idea-site.json'
SAFE_DOWNLOADS = {'.json', '.txt', '.csv', '.pdf'}
LABELS = {'evidence': 'Evidence', 'valuation': 'Valuation', 'mechanism': 'Thesis',
          'catalysts': 'Catalysts', 'downside': 'Downside', 'implementation': 'Implementation'}


def finite(value):
    return value if type(value) in (int, float) and math.isfinite(value) else None


def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-') or 'section'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def confined(root, path):
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f'Path leaves source directory: {path}')
    return resolved


class Renderer:
    """Escaped Markdown subset used by IDEA.md: no raw HTML or remote assets."""
    def __init__(self, link):
        self.link = link
        self.headings = {}

    def inline(self, text, links=True):
        out, i = [], 0
        while i < len(text):
            if text[i] == '\\' and i + 1 < len(text):
                out.append(escape(text[i + 1])); i += 2; continue
            if text[i] == '`':
                end = text.find('`', i + 1)
                if end >= 0:
                    out.append('<code>' + escape(text[i + 1:end]) + '</code>'); i = end + 1; continue
            if links and text[i] == '[':
                match = re.match(r'\[([^\]\n]+)\]\(([^\s]+?)\)', text[i:])
                if match:
                    label, target = match.groups()
                    url, external = self.link(target)
                    inner = self.inline(label, False)
                    out.append(f'<a href="{escape(url, quote=True)}"' + (' target="_blank" rel="noopener noreferrer"' if external else '') + f'>{inner}</a>' if url else f'<span class="unavailable-link" title="Unsupported or unavailable reference">{inner}</span>')
                    i += len(match[0]); continue
            token = '**' if text.startswith('**', i) else ('*' if text[i] == '*' else None)
            if token:
                end = text.find(token, i + len(token))
                if end > i + len(token):
                    tag = 'strong' if len(token) == 2 else 'em'
                    out.append(f'<{tag}>' + self.inline(text[i + len(token):end], False) + f'</{tag}>')
                    i = end + len(token); continue
            out.append(escape(text[i])); i += 1
        return ''.join(out)

    @staticmethod
    def cells(line):
        return [x.strip() for x in re.split(r'(?<!\\)\|', line.strip().strip('|'))]

    @classmethod
    def separator(cls, line):
        cells = cls.cells(line)
        return bool(cells) and all(re.fullmatch(r':?-{3,}:?', c) for c in cells)

    def render(self, markdown):
        lines, out, i = markdown.splitlines(), [], 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1; continue
            heading = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading:
                level, title = len(heading[1]), heading[2]
                base = slug(title); count = self.headings.get(base, 0); self.headings[base] = count + 1
                anchor = base + (f'-{count + 1}' if count else '')
                out.append(f'<h{level} id="{anchor}">{self.inline(title)}</h{level}>'); i += 1; continue
            if line.startswith('```'):
                code = []; i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code.append(lines[i]); i += 1
                out.append('<pre><code>' + escape('\n'.join(code)) + '</code></pre>'); i += 1; continue
            if i + 1 < len(lines) and '|' in line and self.separator(lines[i + 1]):
                headers = self.cells(line); rows = []; i += 2
                while i < len(lines) and '|' in lines[i] and lines[i].strip():
                    cells = self.cells(lines[i]); cells = (cells + [''] * len(headers))[:len(headers)]
                    rows.append('<tr>' + ''.join('<td>' + self.inline(c) + '</td>' for c in cells) + '</tr>'); i += 1
                out.append('<div class="table-scroll" role="region" aria-label="Research table" tabindex="0"><table><thead><tr>' + ''.join('<th scope="col">' + self.inline(c) + '</th>' for c in headers) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'); continue
            if re.fullmatch(r'[-*_]{3,}', line):
                out.append('<hr>'); i += 1; continue
            list_match = re.match(r'^(?:([-+*])|\d+[.)])\s+(.+)', line)
            if list_match:
                ordered = list_match[1] is None; tag = 'ol' if ordered else 'ul'; items = []
                while i < len(lines):
                    item = re.match(r'^(?:([-+*])|\d+[.)])\s+(.+)', lines[i].strip())
                    if not item or (item[1] is None) != ordered:
                        break
                    content = [item[2]]; i += 1
                    while i < len(lines) and lines[i].startswith(('  ', '\t')) and lines[i].strip():
                        content.append(lines[i].strip()); i += 1
                    items.append('<li>' + self.inline(' '.join(content)) + '</li>')
                    if i < len(lines) and not lines[i].strip() and i + 1 < len(lines) and re.match(r'^(?:[-+*]|\d+[.)])\s+', lines[i + 1].strip()):
                        i += 1
                out.append(f'<{tag}>' + ''.join(items) + f'</{tag}>'); continue
            if line.startswith('>'):
                block = []
                while i < len(lines) and lines[i].strip().startswith('>'):
                    block.append(lines[i].strip()[1:].lstrip()); i += 1
                out.append('<blockquote>' + self.render('\n'.join(block)) + '</blockquote>'); continue
            paragraph = [line]; i += 1
            while i < len(lines) and lines[i].strip():
                next_line = lines[i].strip()
                if re.match(r'^(#{1,6}\s|```|>|(?:[-+*]|\d+[.)])\s)', next_line):
                    break
                if i + 1 < len(lines) and '|' in next_line and self.separator(lines[i + 1]):
                    break
                paragraph.append(next_line); i += 1
            out.append('<p>' + self.inline(' '.join(paragraph)) + '</p>')
        return '\n'.join(out)


class Site:
    def __init__(self, source, destination):
        self.source, self.destination = source, destination
        self.references, self.warnings = {}, set()
        self.idea_routes = {}
        self.input_hashes = {}
        self.downloads = set()

    def track(self, path):
        path = confined(self.source, path)
        self.input_hashes[str(path.relative_to(self.source))] = hashlib.sha256(path.read_bytes()).hexdigest()
        return path

    def read(self, path):
        return self.track(path).read_text(encoding='utf-8')

    def link(self, target, document, output='index.html'):
        if any(ord(c) < 32 or ord(c) == 127 for c in target):
            return None, False
        try:
            url = urlsplit(target)
        except ValueError:
            self.warnings.add(f'Malformed URL in {document.name}'); return None, False
        if url.scheme in ('http', 'https') and url.hostname:
            return target, True
        if url.scheme or url.netloc:
            self.warnings.add(f'Blocked URL scheme in {document.name}'); return None, False
        if not url.path:
            if url.fragment and output == 'index.html' and document in self.idea_routes:
                return '#' + urlencode({'idea': self.idea_routes[document], 'section': unquote(url.fragment)}), False
            return ('#' + quote(unquote(url.fragment), safe='-')) if url.fragment else '#', False
        path = Path(unquote(url.path))
        try:
            path = confined(self.source, path if path.is_absolute() else document.parent / path)
        except ValueError:
            self.warnings.add(f'Reference outside library in {document.name}'); return None, False
        if not path.is_file():
            self.warnings.add(f'Missing reference: {path.relative_to(self.source)}'); return None, False
        relative = path.relative_to(self.source).as_posix()
        if path in self.idea_routes and output == 'index.html':
            params = {'idea': self.idea_routes[path]}
            if url.fragment: params['section'] = unquote(url.fragment)
            return '#' + urlencode(params), False
        if relative == 'INDEX.md':
            generated = 'index.html'
        elif path.suffix.lower() == '.md':
            generated = 'reference/' + str(Path(relative).with_suffix('.html')).replace(os.sep, '/')
            self.references[path] = generated
        elif path.suffix.lower() in SAFE_DOWNLOADS:
            generated = 'files/' + relative
            self.copy_download(path)
        else:
            self.warnings.add(f'Unsupported reference type: {relative}'); return None, False
        result = quote(posixpath.relpath(generated, posixpath.dirname(output) or '.'), safe='/.-_')
        if url.fragment:
            result += '#' + quote(unquote(url.fragment), safe='-')
        return result, False

    def copy_download(self, path):
        """Preserve a download's confined local dependency graph at matching paths."""
        path = confined(self.source, path)
        if path in self.downloads:
            return
        self.downloads.add(path)
        dest = self.destination / 'files' / path.relative_to(self.source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.track(path), dest)
        targets = []
        if path.suffix.lower() == '.json':
            def walk(value, key=''):
                if isinstance(value, dict):
                    for k, v in value.items(): walk(v, k)
                elif isinstance(value, list):
                    for v in value: walk(v, key)
                elif isinstance(value, str) and (key in {'source','sources','model','receipt','receipts','reference','references','file','path','url','locator','locators','calculation','calculations','prior_snapshot'} or key.endswith(('_ref','_path','_url','_locator','_receipt','_reference','_calculation','_snapshot'))):
                    targets.append(value)
            walk(json.loads(self.read(path)))
        elif path.suffix.lower() == '.md':
            targets = re.findall(r'\]\(([^\s)]+)\)', self.read(path))
        for target in targets:
            try:
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                linked = confined(self.source, path.parent / unquote(url.path))
                if linked.suffix.lower() not in SAFE_DOWNLOADS | {'.md'}:
                    continue
                if linked.is_file():
                    self.copy_download(linked)
                else:
                    self.warnings.add(f'Missing download dependency in {path.relative_to(self.source)}: {target}')
            except ValueError:
                self.warnings.add(f'Invalid download dependency in {path.relative_to(self.source)}')

    def renderer(self, document, output='index.html'):
        return Renderer(lambda target: self.link(target, document, output))

    def reference_page(self, title, content, output):
        css = posixpath.relpath('assets/styles.css', posixpath.dirname(output) or '.')
        home = posixpath.relpath('index.html', posixpath.dirname(output) or '.')
        return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + escape(title) + ' · AOI</title><link rel="stylesheet" href="' + css + '"></head><body class="reference-page"><main><a class="back-link" href="' + home + '">← Idea library</a><article class="prose">' + content + '</article></main></body></html>'

    def ideas(self):
        metadata = []
        for name in ('current-snapshot-index.json', 'current-idea-index.json'):
            path = self.source / name
            if path.exists():
                metadata = json.loads(self.read(path))
                if not isinstance(metadata, list):
                    raise ValueError(f'{name} must contain an array')
                break
        by_path = {}
        for item in metadata:
            if not isinstance(item, dict) or not item.get('idea_id'):
                raise ValueError('Every current-index entry needs an idea_id')
            path = item.get('reading_page') or f"ideas/{item['idea_id']}/IDEA.md"
            resolved = confined(self.source, self.source / path)
            if resolved in by_path:
                raise ValueError('Duplicate idea reading path in current index')
            by_path[resolved] = item
            if not resolved.is_file():
                raise ValueError(f'Indexed idea page is missing: {path}')
        scores = {}
        weights = {'evidence':25,'valuation':25,'mechanism':15,'catalysts':10,'downside':15,'implementation':10}
        table = self.source / 'score-table.json'
        if table.exists():
            payload = json.loads(self.read(table)); rows = payload.get('ideas', []) if isinstance(payload, dict) else payload
            if isinstance(payload, dict) and 'weights' in payload:
                supplied = payload['weights']
                if not isinstance(supplied, dict) or set(supplied) != set(LABELS) or any(finite(v) is None or not 0 <= v <= 100 for v in supplied.values()) or abs(sum(supplied.values()) - 100) > 1e-8:
                    raise ValueError('Score weights must define the six dimensions and sum to 100')
                weights = supplied
            if not isinstance(rows, list):
                raise ValueError('score-table.json needs an ideas array')
            for row in rows:
                if row['idea_id'] in scores:
                    raise ValueError('Duplicate idea ID in score table')
                scores[row['idea_id']] = row
        pages = set(by_path) | {confined(self.source, p) for p in (self.source / 'ideas').glob('*/IDEA.md')}
        self.idea_routes = {page: by_path.get(page, {}).get('idea_id', page.parent.name) for page in pages}
        results, seen = [], set()
        for page in sorted(pages):
            item = by_path.get(page, {}); identity = item.get('idea_id', page.parent.name)
            if identity in seen:
                raise ValueError('Duplicate idea ID: ' + identity)
            seen.add(identity)
            markdown = self.read(page)
            heading = re.search(r'^#\s+(.+)$', markdown, re.M)
            title = heading[1] if heading else identity
            snapshot = {}
            if item.get('snapshot'):
                sp = confined(self.source, self.source / item['snapshot'])
                if not sp.is_file():
                    raise ValueError('Missing current snapshot: ' + item['snapshot'])
                snapshot = json.loads(self.read(sp))
            score = scores.get(identity, snapshot.get('score', {}))
            score = score if isinstance(score, dict) else {}
            total, known = finite(score.get('total')), finite(score.get('known_subtotal'))
            # Never substitute the partial subtotal for a missing total.
            eligible = score.get('eligible_for_ranking') is True
            missing = score.get('missing_required_inputs', [])
            gates = score.get('eligibility_gates_passed')
            status = str(item.get('status', snapshot.get('status', 'Needs review')))
            if re.search(r'invalidat|closed|expired', status, re.I):
                group = 'closed'
            elif gates is False or re.search(r'ineligible|reject', status + ' ' + str(score.get('band', '')), re.I) or (total is not None and not eligible):
                group = 'ineligible'
            elif total is not None and eligible:
                group = 'complete'
            else:
                group = 'incomplete'
            # Remove only navigation and duplicated heading; all research content remains available.
            clean = re.sub(r'^#\s+.*\n?', '', markdown, count=1)
            clean = re.sub(r'^\[Back[^\n]*\n?', '', clean, flags=re.M)
            parts = re.split(r'^##\s+(.+)\s*$', clean, flags=re.M)
            intro = parts[0]
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n', intro) if p.strip() and not p.strip().startswith(('**Status:', '[Back'))]
            tldr = snapshot.get('tldr', {})
            summary = (tldr.get('idea') if isinstance(tldr, dict) else None) or snapshot.get('thesis') or (paragraphs[0] if paragraphs else '')
            # Summary/card text is text, never executable HTML.
            summary = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', str(summary))
            sections = [{'id': 'overview', 'title': 'Overview', 'html': self.renderer(page).render(intro)}]
            ids = {'overview'}
            for n in range(1, len(parts), 2):
                base = slug(parts[n]); section_id = base; duplicate = 2
                while section_id in ids:
                    section_id = f'{base}-{duplicate}'; duplicate += 1
                ids.add(section_id)
                sections.append({'id': section_id, 'title': parts[n], 'html': self.renderer(page).render(parts[n + 1])})
            ticker = str(item.get('ticker') or (snapshot.get('target_equities') or [{}])[0].get('ticker') or page.parent.name)
            company = str((snapshot.get('target_equities') or [{}])[0].get('company') or title.split(':')[0])
            source_url = 'https://seekingalpha.com/article/' + str(item['source_article_id']) if str(item.get('source_article_id', '')).isdigit() else None
            md_relative = 'notes/' + page.relative_to(self.source).as_posix()
            md_copy = self.destination / md_relative; md_copy.parent.mkdir(parents=True, exist_ok=True)
            def portable_markdown_link(match):
                label, target = match.groups()
                target, _ = self.link(target, page, md_relative)
                return '[' + label + '](' + target + ')' if target else label + ' (reference unavailable)'
            portable_markdown = re.sub(r'\[([^\]\n]+)\]\(([^\s]+?)\)', portable_markdown_link, markdown)
            md_copy.write_text(portable_markdown, encoding='utf-8')
            static_path = 'ideas/' + quote(identity, safe='-_') + '/index.html'
            # No untrusted identity may become a filesystem traversal path.
            if not re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*', identity):
                raise ValueError('Idea ID must be a safe folder name: ' + identity)
            standalone = self.renderer(page, static_path).render(markdown)
            dest = self.destination / static_path; dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(self.reference_page(title, standalone, static_path), encoding='utf-8')
            dimensions = score.get('scores', {})
            horizon = snapshot.get('horizon', '')
            resolution = snapshot.get('resolution_date') or snapshot.get('resolution_at', '')
            if isinstance(horizon, dict):
                window = horizon.get('decision_window', horizon)
                if not isinstance(window, dict):
                    window = {}
                early = window.get('earliest_check', '')
                resolution = resolution or window.get('resolution') or window.get('latest_resolution', '')
                horizon = horizon.get('description') or '; '.join(part for part in [('Early check: ' + str(early)) if early else '', ('Resolution: ' + str(resolution)) if resolution else '']) or 'See decision window'
            elif not isinstance(horizon, str):
                horizon = 'See decision window'
            results.append({'id': identity, 'ticker': ticker, 'company': company, 'title': title,
                'summary': summary, 'status': status, 'group': group, 'total': total, 'known': known,
                'range': score.get('possible_range'), 'eligible': eligible, 'band': score.get('band', 'not scored'),
                'missing': missing if isinstance(missing, list) else [], 'dimensions': dimensions,
                'labels': LABELS, 'weights': weights,
                'asOf': item.get('as_of_session', snapshot.get('as_of_session', '')),
                'updated': item.get('last_research_updated_at', snapshot.get('created_at', '')),
                'horizon': horizon, 'resolution': resolution,
                'likelihood': snapshot.get('likelihood', {}).get('display', snapshot.get('likelihood', {}).get('current', 'not estimable')) if isinstance(snapshot.get('likelihood', {}), dict) else 'not estimable',
                'sourceUrl': source_url, 'sections': sections, 'searchText': markdown,
                'markdownUrl': 'notes/' + quote(page.relative_to(self.source).as_posix(), safe='/'),
                'staticUrl': static_path})
        return results

    def finish_references(self):
        processed = set()
        while pending := [(p, o) for p, o in self.references.items() if p not in processed]:
            for path, output in pending:
                processed.add(path)
                text = self.read(path)
                heading = re.search(r'^#\s+(.+)$', text, re.M)
                title = heading[1] if heading else path.stem
                rendered = self.renderer(path, output).render(text)
                dest = self.destination / output; dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(self.reference_page(title, rendered, output), encoding='utf-8')


def build(source, output):
    source, output = Path(source).expanduser().resolve(), Path(output).expanduser().resolve()
    if not source.is_dir():
        raise ValueError('Source directory does not exist')
    if source == output or source.is_relative_to(output) or output.is_relative_to(source / 'ideas'):
        raise ValueError('Output must be separate from source and idea folders')
    if output.exists() and any(output.iterdir()):
        marker = output / MARKER
        if not marker.is_file():
            raise ValueError('Refusing to replace a non-generated output directory')
        previous = read_json(marker)
        if previous.get('generator') != 'aoi-idea-site-v1':
            raise ValueError('Unknown output ownership marker')
        unexpected = {p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()} - set(previous.get('files', [])) - {MARKER}
        if unexpected:
            raise ValueError('Output contains files not owned by the generator: ' + ', '.join(sorted(unexpected)))
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.aoi-site-', dir=output.parent)); backup = None
    try:
        site = Site(source, stage); ideas = site.ideas()
        site.finish_references()
        assets = stage / 'assets'; assets.mkdir()
        for name in ('styles.css', 'app.js', 'favicon.svg'):
            shutil.copyfile(ASSETS / name, assets / name)
        data = json.dumps({'ideas': ideas}, ensure_ascii=False, allow_nan=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        template = (ASSETS / 'index.html').read_text(encoding='utf-8')
        fallback = ''.join('<li><a href="' + i['staticUrl'] + '">' + escape(i['title']) + '</a></li>' for i in ideas) or '<li>No ideas yet.</li>'
        (stage / 'index.html').write_text(template.replace('<!--APP_DATA-->', data).replace('<!--FALLBACK-->', fallback), encoding='utf-8')
        manifest = {'generator': 'aoi-idea-site-v1', 'generated_at': datetime.now(timezone.utc).isoformat(),
            'idea_count': len(ideas), 'source_hashes': site.input_hashes, 'warnings': sorted(site.warnings),
            'files': sorted(p.relative_to(stage).as_posix() for p in stage.rglob('*') if p.is_file())}
        (stage / MARKER).write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        # Validate source immutability while generating; a concurrent update needs another build.
        for name, expected in site.input_hashes.items():
            if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
                raise ValueError('Source changed during build; rerun after update completes: ' + name)
        if output.exists():
            backup = Path(tempfile.mkdtemp(prefix='.aoi-site-old-', dir=output.parent)); backup.rmdir(); os.replace(output, backup)
        os.replace(stage, output)
        if backup:
            shutil.rmtree(backup)
        return manifest
    except Exception:
        if backup and backup.exists() and not output.exists():
            os.replace(backup, output)
        raise
    finally:
        if stage.exists(): shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('/Volumes/Agent/AOI-data'), help='AOI data root containing ideas/*/IDEA.md')
    parser.add_argument('--output', type=Path, help='Generated directory; defaults to <source>/site')
    parser.add_argument('--serve', action='store_true', help='After building, serve generated files on 127.0.0.1 until Ctrl-C')
    parser.add_argument('--port', type=int, default=8000, help='Local preview port; use 0 for an available port (default: 8000)')
    args = parser.parse_args(); output = args.output or args.source / 'site'
    if not 0 <= args.port <= 65535:
        parser.error('--port must be between 0 and 65535')
    try:
        result = build(args.source, output)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'Build failed: {exc}\n')
    print(f"Built {result['idea_count']} ideas: {output.expanduser().resolve() / 'index.html'}", flush=True)
    for warning in result['warnings']: print('Note: ' + warning)
    if args.serve:
        try:
            server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(SimpleHTTPRequestHandler, directory=str(output.expanduser().resolve())))
        except OSError as exc:
            parser.exit(1, f'Preview could not start (generated files are intact): {exc}\n')
        print(f'Local: http://127.0.0.1:{server.server_port} — Ctrl-C to stop', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == '__main__':
    main()
