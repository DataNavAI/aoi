#!/usr/bin/env python3
"""Read-only local-reference audit for Markdown, HTML and structured TLDRs in every bundle.

Network references are not fetched. Structured local locators are relative to their
containing JSON file, including generated site/files snapshots. This verifies link
integrity, not whether the linked source supports a claim.
"""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

EXTENSIONS = {'.md', '.json', '.html', '.txt', '.csv', '.pdf', '.css', '.js', '.svg'}


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set()
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if attrs.get('id'): self.ids.add(attrs['id'])
        self.links.extend(attrs[k] for k in ('href','src') if attrs.get(k))


def audit(root):
    root=Path(root).resolve(); errors=[]; checked=0
    def check(document, target, field):
        nonlocal checked
        try: u=urlsplit(target)
        except ValueError:
            errors.append({'file':str(document.relative_to(root)),'field':field,'target':target,'error':'malformed locator'}); return
        if u.scheme or u.netloc or not u.path: return
        path=(document.parent/unquote(u.path)).resolve(); checked+=1
        problem=None
        if not path.is_relative_to(root): problem='outside audited bundle'
        elif not path.is_file(): problem='missing file'
        elif u.fragment:
            fragment=unquote(u.fragment)
            if path.suffix=='.json':
                try:
                    value=json.loads(path.read_text())
                    for key in fragment.strip('/').split('/'):
                        key=key.replace('~1','/').replace('~0','~')
                        value=value[int(key)] if isinstance(value,list) else value[key]
                except (KeyError,ValueError,TypeError,IndexError): problem='missing JSON fragment'
            elif path.suffix=='.html':
                parser=Links();parser.feed(path.read_text())
                if fragment not in parser.ids and not fragment.startswith('idea='): problem='missing HTML fragment'
            elif path.suffix=='.md':
                text=path.read_text(); headings=re.findall(r'^#+\s+(.+)$',text,re.M)
                ids={re.sub(r'[^a-z0-9]+','-',h.lower()).strip('-') for h in headings}
                ids.update(re.findall(r'\bid=["\x27]([^"\x27]+)',text))
                if fragment not in ids: problem='missing Markdown fragment'
        if problem:errors.append({'file':str(document.relative_to(root)),'field':field,'target':target,'error':problem})
    def scan_tldr(document,value,field='tldr'):
        if isinstance(value,dict):
            for k,v in value.items():scan_tldr(document,v,field+'.'+k)
        elif isinstance(value,list):
            for i,v in enumerate(value):scan_tldr(document,v,field+f'[{i}]')
        elif isinstance(value,str):
            key=field.rsplit('.',1)[-1].split('[')[0]
            reference_keys={'source','sources','source_url','source_path','source_locator','source_locators','model','model_reference','model_ref','receipt','receipts','reference','references','file','path','url','locator','locators','calculation','calculation_ref'}
            if key not in reference_keys and not key.endswith(('_ref','_path','_url','_locator','_receipt','_reference','_calculation','_snapshot')): return
            try: u=urlsplit(value)
            except ValueError:return
            if not u.scheme and not u.netloc and Path(unquote(u.path)).suffix.lower() in EXTENSIONS:
                check(document,value,field)
    def find_tldrs(document,value):
        if isinstance(value,dict):
            if 'tldr' in value:
                scan_tldr(document,value,'snapshot')
            else:
                for v in value.values():find_tldrs(document,v)
        elif isinstance(value,list):
            for v in value:find_tldrs(document,v)
    for path in sorted(root.rglob('*')):
        if not path.is_file():continue
        if path.suffix=='.md':
            for target in re.findall(r'\]\(([^\s)]+)\)',path.read_text()):check(path,target,'Markdown link')
        elif path.suffix=='.html':
            parser=Links();parser.feed(path.read_text())
            for target in parser.links:check(path,target,'HTML link')
        elif path.suffix=='.json':find_tldrs(path,json.loads(path.read_text()))
    return {'root':str(root),'checked':checked,'errors':errors,'status':'pass' if not errors else 'revise',
            'scope':'local reference integrity only; no claim-fidelity, network-source or research-quality verdict'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);a=p.parse_args()
    report=audit(a.root);print(json.dumps(report,indent=2));raise SystemExit(bool(report['errors']))
