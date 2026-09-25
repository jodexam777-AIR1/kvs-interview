"""Build NotebookLM source text files from the master-notes HTML."""
import re, sys
from bs4 import BeautifulSoup, NavigableString, Tag

TIER = {'क': 'लगभग पक्का आएगा', 'ख': 'बहुत संभव', 'ग': 'कभी-कभी'}
BLOCK = {'p','li','h2','h3','tr','div','ul','ol','table','thead','tbody','details','aside','section','article','header','summary'}

def inline(el):
    out = []
    for c in el.children:
        if isinstance(c, NavigableString):
            out.append(str(c))
        elif isinstance(c, Tag):
            cls = c.get('class') or []
            if 'stage' in cls:
                t = c.get_text(' ', strip=True).strip('()')
                out.append(f' [बोलने का तरीका: {t}] ')
            elif c.name == 'mark':
                out.append(' [सच-जाँच — यह तभी बोलें जब सच हो:] ' + inline(c) + ' ')
            elif c.name == 'br':
                out.append(' ')
            else:
                out.append(inline(c))
    return re.sub(r'\s+', ' ', ''.join(out)).strip()

def flat(el, lines):
    """Generic flattener for static sections."""
    for c in el.children:
        if isinstance(c, NavigableString):
            t = str(c).strip()
            if t: lines.append(t)
            continue
        if not isinstance(c, Tag) or c.name in ('script','style','button','input','nav'):
            continue
        cls = c.get('class') or []
        if c.name == 'h2': lines.append('\n## ' + inline(c))
        elif c.name == 'h3': lines.append('\n### ' + inline(c))
        elif 'trow' in cls:
            k = c.find(class_='tk'); v = c.find(class_='tv')
            lines.append(f'- {inline(k)}: {inline(v)}')
        elif 'li' in cls and c.find(class_='liq'):
            lines.append(f'- प्रश्न: {inline(c.find(class_="liq"))}\n  उत्तर: {inline(c.find(class_="lia"))}')
        elif c.name == 'tr':
            cells = [inline(x) for x in c.find_all(['th','td'])]
            lines.append('- ' + ' | '.join(cells))
        elif c.name == 'li' and c.find(class_='t'):
            lines.append('- ' + inline(c.find(class_='t')))
        elif c.name == 'li':
            if c.find(['ul','ol','p','div']):
                flat(c, lines)
            else:
                lines.append('- ' + inline(c))
        elif c.name == 'p':
            t = inline(c)
            if t: lines.append(t)
        elif 'note' in cls:
            lab = c.find(class_='nl'); labt = inline(lab) if lab else ''
            if lab: lab.extract()
            if c.find(['ul','ol']):
                lines.append(f'{labt}:'); flat(c, lines)
            else:
                lines.append(f'{labt}: {inline(c)}')
        elif c.name in ('details',):
            s = c.find('summary')
            if s: lines.append('\n### ' + inline(s)); s.extract()
            flat(c, lines)
        else:
            if c.name in BLOCK or cls:
                flat(c, lines)
            else:
                t = inline(c)
                if t: lines.append(t)

def card(art):
    L = []
    cid = art.get('data-id')
    tier = art.find(class_='tier'); tt = TIER.get(tier.get_text(strip=True), '') if tier else ''
    q = inline(art.find(class_='q'))
    L.append(f'\n### कार्ड {cid} — {q}')
    if tt: L.append(f'कितना संभव: {tt}')
    alt = art.find(class_='alt')
    if alt:
        a = inline(alt).replace('ऐसे भी:', '').strip()
        L.append(f'यही प्रश्न ऐसे भी पूछा जा सकता है: {a}')
    first = art.select_one('.row.first p'); keys = art.select('.row.keys .beats .t'); last = art.select_one('.row.last p')
    slots = art.select('.row.keys .beats .n.slot')
    flab = art.select_one('.row.first .lab')
    haan = flab is not None and 'हाँ' in flab.get_text()
    if slots:
        L.append('ढाँचा: हाँ → पर → हल → बच्चा')
        L.append(f'हाँ — पहली पंक्ति (शब्द-दर-शब्द रटनी है): “{inline(first)}”')
        for sl, k in zip(slots, keys):
            L.append(f'{sl.get_text(strip=True)}: {inline(k)}')
        L.append(f'बच्चा — आख़िरी पंक्ति (शब्द-दर-शब्द रटनी है): “{inline(last)}”')
    else:
        if first: L.append(f'{"हाँ — " if haan else ""}पहली पंक्ति (शब्द-दर-शब्द रटनी है): “{inline(first)}”')
        if keys: L.append(('छोटा रूप — बीच में बस इतना: ' if haan else 'चाबी — इसी क्रम में: ') + ' → '.join(f'({i+1}) {inline(k)}' for i, k in enumerate(keys)))
        if last: L.append(f'{"बच्चा — " if haan else ""}आख़िरी पंक्ति (शब्द-दर-शब्द रटनी है): “{inline(last)}”')
    ans = art.find(class_='ans')
    if ans:
        L.append('पूरा उत्तर:')
        for p in ans.find_all(['p','hr'], recursive=True):
            if p.name == 'hr' or 'anslab' in (p.get('class') or []): continue
            t = inline(p)
            if t: L.append(t)
    for n in art.select('.reveal > aside.note'):
        lab = n.find(class_='nl'); labt = inline(lab) if lab else 'ध्यान दें'
        body = n.get_text(' ', strip=True)[len(labt):].strip() if lab else inline(n)
        L.append(f'{labt}: {re.sub(chr(10), " ", body)}')
    xs = art.select('.cross .xq')
    if xs:
        L.append(f'क्रॉस-प्रश्न ({len(xs)}) — पैनल आगे यह पूछ सकता है:')
        for i, x in enumerate(xs, 1):
            L.append(f'  क्रॉस {i}. प्रश्न: {inline(x.find(class_="xqq"))}')
            L.append(f'     उत्तर: {inline(x.find(class_="xqa"))}')
    return L

def parse(path):
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    secs = []
    for sec in soup.select('.wrap > section.sec'):
        sid = sec.get('id')
        if sid in ('dohrao', 'badlav', 'plan'):
            continue
        lines = []
        h2 = sec.find('h2', recursive=False)
        lines.append('## ' + inline(h2) if h2 else '')
        lede = sec.find('p', class_='lede', recursive=False)
        if lede: lines.append(inline(lede))
        cards = sec.find_all('article', class_='card', recursive=False)
        if cards:
            for c in sec.children:
                if isinstance(c, Tag) and c.name not in ('h2','article') and 'lede' not in (c.get('class') or []):
                    wrapper = BeautifulSoup('<div></div>', 'html.parser').div
                    wrapper.append(c.__copy__())
                    flat(wrapper, lines)
            secs.append((sid, None, lines))
            for a in cards:
                secs.append((sid, a.get('data-id'), card(a)))
        else:
            body = []
            for c in list(sec.children):
                if isinstance(c, Tag) and c.name == 'h2': c.extract()
                if isinstance(c, Tag) and 'lede' in (c.get('class') or []): c.extract()
            flat(sec, body)
            secs.append((sid, None, lines + body))
    return secs

def write(path, title, intro, blocks):
    txt = [f'# {title}', intro, '']
    for b in blocks:
        txt += b
    out = '\n'.join(txt)
    out = re.sub(r'\n{3,}', '\n\n', out)
    open(path, 'w', encoding='utf-8').write(out.strip() + '\n')
    return len(out)
