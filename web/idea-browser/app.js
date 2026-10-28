'use strict';
(() => {
  const ideas = JSON.parse(document.getElementById('idea-data').textContent).ideas;
  const $ = id => document.getElementById(id);
  const groups = {complete:'Eligible to rank',incomplete:'Needs evidence',ineligible:'Ineligible / rejected',closed:'Invalidated / closed'};
  const groupOrder = {complete:0,incomplete:1,ineligible:2,closed:3};
  const state = {query:'',filter:'all',sort:'priority',selected:null,rendered:null};
  const num = value => Number.isFinite(value) ? new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(value) : '—';
  const isNumber = value => typeof value === 'number' && Number.isFinite(value);
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }
  function date(value) {
    if (!value) return 'Not recorded';
    const parsed = new Date(value.length === 10 ? value+'T12:00:00Z' : value);
    if (Number.isNaN(parsed.getTime())) return value;
    return new Intl.DateTimeFormat('en-US',{year:'numeric',month:'short',day:'numeric',timeZone: value.length === 10 ? 'UTC' : 'America/Los_Angeles'}).format(parsed);
  }
  function badge(idea) { return el('span','badge '+idea.group,groups[idea.group]); }
  function track(idea) {
    const trackNode = el('div','score-track');
    const known = isNumber(idea.total) ? idea.total : idea.known;
    const unknown = isNumber(idea.total) ? 0 : Object.entries(idea.weights).reduce((sum,[key,weight]) => sum+(idea.dimensions[key] == null ? weight : 0),0);
    trackNode.setAttribute('role','img');
    trackNode.setAttribute('aria-label',isNumber(known) ? `${num(known)} ${isNumber(idea.total) ? 'total' : 'known'} points; ${unknown} points of weight unscored` : 'No score available');
    const filled = el('span','known-segment'); filled.style.width = Math.max(0,Math.min(100,known || 0))+'%';
    const missing = el('span','unknown-segment'); missing.style.width = Math.max(0,Math.min(100-(known||0),unknown))+'%';
    trackNode.append(filled,missing); return trackNode;
  }
  function scoreText(idea) {
    if (isNumber(idea.total)) return `${num(idea.total)} / 100`;
    if (isNumber(idea.known)) return num(idea.known)+' known pts';
    return 'Not scored';
  }
  function visibleIdeas() {
    const query = state.query.trim().toLocaleLowerCase();
    return ideas.filter(idea => (state.filter === 'all' || idea.group === state.filter) && (!query || [idea.ticker,idea.title,idea.company,idea.summary,idea.searchText].join(' ').toLocaleLowerCase().includes(query))).sort((a,b) => {
      if (state.sort === 'ticker') return a.ticker.localeCompare(b.ticker);
      if (state.sort === 'updated') return ((Date.parse(b.updated)||0)-(Date.parse(a.updated)||0)) || a.ticker.localeCompare(b.ticker);
      const groupDiff = groupOrder[a.group]-groupOrder[b.group];
      if (groupDiff) return groupDiff;
      const av = state.sort === 'known' ? (a.known ?? a.total) : (a.total ?? a.known);
      const bv = state.sort === 'known' ? (b.known ?? b.total) : (b.total ?? b.known);
      if ((av ?? -Infinity) !== (bv ?? -Infinity)) return (bv ?? -Infinity)-(av ?? -Infinity);
      if (a.group === 'complete') {
        const evidence = (b.dimensions.evidence ?? -1)-(a.dimensions.evidence ?? -1);
        if (evidence) return evidence;
        const downside = (b.dimensions.downside ?? -1)-(a.dimensions.downside ?? -1);
        if (downside) return downside;
      }
      return a.ticker.localeCompare(b.ticker);
    });
  }
  function card(idea) {
    const button = el('button','idea-card'+(idea.id===state.selected?' selected':''));
    button.type='button'; button.dataset.ideaId=idea.id; button.setAttribute('aria-pressed',String(idea.id===state.selected));
    button.setAttribute('aria-label',`${idea.ticker}: ${idea.title}. ${groups[idea.group]}. ${scoreText(idea)}.`);
    const top=el('span','card-top'); top.append(el('span','ticker',idea.ticker),badge(idea));
    const prefix=idea.ticker+':';
    const headline=idea.title.startsWith(prefix)?idea.title.slice(prefix.length).trim():idea.title;
    const score=el('span','card-score'); score.append(el('strong','',scoreText(idea)),el('span','',isNumber(idea.total)?'Complete score':'Total incomplete'));
    button.append(top,el('span','card-title',headline),el('span','card-summary',idea.summary),score,track(idea));
    if (!isNumber(idea.total) && Array.isArray(idea.range) && idea.range.length===2) button.append(el('span','card-range',`Possible ${num(idea.range[0])}–${num(idea.range[1])} / 100 · not a rank`));
    return button;
  }
  function renderList(visible) {
    $('idea-list').replaceChildren(...visible.map(card));
    $('result-count').textContent=visible.length+' / '+ideas.length;
    if (!visible.length) $('idea-list').append(el('div','empty-list',ideas.length ? 'No matching ideas. Try a different ticker, term, or status.' : 'Your idea library is empty.'));
  }
  function fact(label,value) {
    const node=el('div'); node.append(el('span','',label),el('strong','',value)); return node;
  }
  function link(label,href) {
    const node=el('a','',label); node.href=href; return node;
  }
  function emptyReader() {
    const box=el('div','empty-state');box.append(el('span','empty-glyph','↗'),el('h2','',ideas.length?'No matching ideas':'A place for your next idea'));
    box.append(el('p','',ideas.length?'Reset the filters to return to your research library.':'Add an IDEA.md in an idea folder and rebuild the site to get started.'));
    if (ideas.length) {const reset=el('button','reset-button','Reset filters');reset.type='button';reset.addEventListener('click',resetFilters);box.append(reset);}
    $('reader').replaceChildren(box);state.rendered=null;
  }
  function renderReader(idea) {
    if (!idea) {emptyReader();return;}
    if (state.rendered===idea.id) return;
    state.rendered=idea.id;
    document.title=idea.ticker+' · AOI Idea desk';
    const hero=el('header','idea-hero');const top=el('div','hero-top');const identity=el('div');identity.append(el('span','ticker',idea.ticker),badge(idea));
    const actions=el('div','hero-actions');const markdown=link('Source Markdown ↗',idea.markdownUrl);markdown.setAttribute('download','IDEA.md');actions.append(markdown);
    const print=el('button','icon-button','Print idea');print.type='button';print.addEventListener('click',()=>window.print());actions.append(print);top.append(identity,actions);
    const prefix=idea.ticker+':';
    const headline=idea.title.startsWith(prefix)?idea.title.slice(prefix.length).trim():idea.title;
    hero.append(top,el('p','hero-meta',idea.company+' / SOURCE-DERIVED THESIS'),el('h2','',headline),el('p','hero-summary',idea.summary));
    const facts=el('div','hero-facts');facts.append(fact('Research as of',date(idea.asOf)),fact('Horizon',idea.horizon||'See research note'),fact('Event likelihood',isNumber(idea.likelihood)?num(idea.likelihood)+'%':String(idea.likelihood||'Not estimable')));
    if (idea.resolution) facts.append(fact('Resolution',date(idea.resolution)));
    hero.append(facts);
    const summary=el('aside','score-summary');summary.setAttribute('aria-label','Research score');const number=el('div','score-number',isNumber(idea.total)?num(idea.total):num(idea.known));
    number.append(el('small','',isNumber(idea.total)?'Complete score / 100':isNumber(idea.known)?'Known contribution':'Not scored'));
    const explanation=el('div');const note=el('p');
    if (isNumber(idea.total)) note.append(el('strong','',`Complete score: ${num(idea.total)} / 100. `),document.createTextNode('A research assessment, not a return forecast or an execution approval.'));
    else { note.append(el('strong','','The total score is incomplete. '));note.append(document.createTextNode(Array.isArray(idea.range)?`Possible range ${num(idea.range[0])}–${num(idea.range[1])} / 100. `:''));note.append(document.createTextNode('Known points are not comparable to complete scores and do not establish an investment rank.')); }
    explanation.append(note,track(idea));const strip=el('div','dimension-strip');
    for (const [key,label] of Object.entries(idea.labels)) {const dim=el('div');dim.append(el('span','',label),el('strong','',isNumber(idea.dimensions[key])?num(idea.dimensions[key])+'/4':'Unscored'));strip.append(dim);}
    explanation.append(strip);summary.append(number,explanation);
    const nav=el('nav','jump-nav');nav.setAttribute('aria-label','Research sections');
    const names={'research-question':'Thesis & horizon','source-derived-thesis':'Source thesis','strongest-countercase':'Countercase','evidence-that-matters':'Evidence','catalysts-and-falsifiers':'Catalysts','score-and-decision-status':'Score','entry-today-versus-later':'Returns','prioritized-next-research-checks':'Next checks','dates-and-supporting-record':'Record'};
    const fragment=document.createDocumentFragment();fragment.append(hero);
    const hasTldr=idea.sections.some(section=>section.id==='tldr');
    if (!hasTldr) fragment.append(summary,nav);
    for (let index=0;index<idea.sections.length;index++) {
      const section=idea.sections[index];const params=new URLSearchParams({idea:idea.id,section:section.id});const jump=link(names[section.id]||section.title,'#'+params.toString());jump.dataset.section=section.id;nav.append(jump);
      const container=el('section','research-section');container.id='research-'+section.id;
      container.append(el('span','section-label',String(index+1).padStart(2,'0')+' / RESEARCH NOTE'),el('h3','',section.title));
      const prose=el('div','prose');prose.innerHTML=section.html; // HTML is escaped/sanitized by the local Python renderer.
      container.append(prose);
      if (section.id==='tldr') {fragment.insertBefore(container,hero.nextSibling);fragment.append(summary,nav);}
      else fragment.append(container);
    }
    $('reader').replaceChildren(fragment);
  }
  function route(idea,section,replace=false) {
    const params=new URLSearchParams();if(idea) params.set('idea',idea);if(section)params.set('section',section);
    const hash='#'+params.toString();
    if(replace) history.replaceState(null,'',hash);else if(location.hash!==hash) location.hash=hash;
  }
  function reconcile(replaceRoute=true) {
    const visible=visibleIdeas();if(!visible.some(idea=>idea.id===state.selected))state.selected=visible[0]?.id||null;
    renderList(visible);renderReader(visible.find(idea=>idea.id===state.selected));if(replaceRoute)route(state.selected,null,true);
  }
  function resetFilters() {state.query='';state.filter='all';state.sort='priority';$('search').value='';$('status').value='all';$('sort').value='priority';reconcile();}
  $('search').addEventListener('input',event=>{state.query=event.target.value;reconcile();});
  $('status').addEventListener('change',event=>{state.filter=event.target.value;reconcile();});
  $('sort').addEventListener('change',event=>{state.sort=event.target.value;reconcile();});
  $('idea-list').addEventListener('click',event=>{
    const button=event.target.closest('button[data-idea-id]');if(!button)return;
    state.selected=button.dataset.ideaId;route(state.selected);reconcile(false);
    const reader=$('reader');reader.focus({preventScroll:true});
    if(matchMedia('(max-width: 760px)').matches || window.scrollY>reader.offsetTop+24) {
      reader.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    }
  });
  window.addEventListener('hashchange',()=>{
    const params=new URLSearchParams(location.hash.slice(1));const target=ideas.find(idea=>idea.id===params.get('idea'));
    if(target){state.selected=target.id;if(!visibleIdeas().some(idea=>idea.id===target.id)){state.query='';state.filter='all';$('search').value='';$('status').value='all';}}
    reconcile(false);const section=params.get('section');
    if(section){const node=document.getElementById('research-'+section);if(node){node.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});$('reader').querySelectorAll('.jump-nav a').forEach(a=>a.classList.toggle('active',a.dataset.section===section));}}
  });
  window.addEventListener('keydown',event=>{if(event.key==='/'&&!event.metaKey&&!event.ctrlKey&&!event.altKey&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!document.activeElement.isContentEditable){event.preventDefault();$('search').focus();}});
  $('idea-count').textContent=ideas.length;$('complete-count').textContent=ideas.filter(idea=>isNumber(idea.total)).length;$('gap-count').textContent=ideas.filter(idea=>!isNumber(idea.total)).length;
  const dates=ideas.map(idea=>idea.asOf).filter(Boolean).sort();$('research-date').textContent=dates.length?date(dates[dates.length-1]):'No research yet';
  const initial=new URLSearchParams(location.hash.slice(1));state.selected=ideas.find(idea=>idea.id===initial.get('idea'))?.id||null;
  reconcile(!initial.get('section'));
  if(initial.get('section'))window.dispatchEvent(new HashChangeEvent('hashchange'));
})();
