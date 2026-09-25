"""Word-for-word revision audio from the master notes (edge-tts, two voices)."""
import asyncio, os, re, subprocess, sys, hashlib
import edge_tts, imageio_ffmpeg
from bs4 import BeautifulSoup, NavigableString, Tag

FF = imageio_ffmpeg.get_ffmpeg_exe()
PROXY = os.environ.get('HTTPS_PROXY')
Q, A = 'hi-IN-MadhurNeural', 'hi-IN-SwaraNeural'   # panel voice, answer voice
RATE = '-8%'
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, '.cache'); os.makedirs(CACHE, exist_ok=True)
NUM = ['एक','दो','तीन','चार','पाँच','छह','सात','आठ','नौ','दस','ग्यारह','बारह','तेरह','चौदह','पंद्रह']

def clean(el):
    if el is None: return ''
    el = BeautifulSoup(str(el), 'html.parser')
    for st in el.select('.stage, .nl'): st.decompose()
    t = el.get_text(' ', strip=True)
    t = t.replace('→', ', ').replace('·', ', ').replace('—', ', ').replace('|', ', ')
    t = re.sub(r'\(\s*\)', '', t)
    return re.sub(r'\s+', ' ', t).strip(' ,')

def card_segments(art, n):
    S = []
    q = clean(art.find(class_='q'))
    S += [(Q, f'प्रश्न {NUM[n] if n < len(NUM) else n+1}। {q}', 4000)]   # 4 s: say it yourself first
    first = art.select_one('.row.first p'); last = art.select_one('.row.last p')
    slots = art.select('.row.keys .n.slot'); keys = art.select('.row.keys .t')
    flab = art.select_one('.row.first .lab'); haan = flab is not None and 'हाँ' in flab.get_text()
    if slots:
        S += [(A, 'हाँ। ' + clean(first), 700)]
        for sl, k in zip(slots, keys): S += [(A, sl.get_text(strip=True) + '। ' + clean(k), 700)]
        S += [(A, 'बच्चा। ' + clean(last), 1500)]
    elif first or keys:
        if first: S += [(A, ('हाँ। ' if haan else '') + clean(first), 700)]
        for k in keys: S += [(A, clean(k), 600)]
        if last: S += [(A, ('बच्चा। ' if haan else '') + clean(last), 1500)]
    ans = art.find(class_='ans')
    if ans:
        paras = [clean(p) for p in ans.find_all('p') if 'anslab' not in (p.get('class') or [])]
        paras = [p for p in paras if p]
        if paras:
            S += [(Q, 'अब पूरा उत्तर।' if (first or keys) else 'उत्तर।', 500)]
            S += [(A, p, 600) for p in paras]
            S[-1] = (S[-1][0], S[-1][1], 1500)
    for note in art.select('.reveal > aside.note'):
        lab = note.find(class_='nl'); lt = lab.get_text(strip=True) if lab else 'ध्यान दें'
        S += [(Q, f'{lt}। {clean(note)}', 1000)]
    xs = art.select('.cross .xq')
    if xs:
        S += [(Q, f'अब पैनल के {len(xs)} क्रॉस-प्रश्न।', 700)]
        for x in xs:
            S += [(Q, clean(x.find(class_='xqq')), 2500), (A, clean(x.find(class_='xqa')), 1200)]
    if first and last:
        S += [(Q, 'एक बार फिर, पहली और आख़िरी पंक्ति।', 500), (A, clean(first), 700), (A, clean(last), 2500)]
    return S

def static_segments(sec):
    S = []
    for el in sec.find_all(['h2','h3','p','li','tr','div'], recursive=True):
        cls = el.get('class') or []
        if el.name in ('h2','h3'): S += [(Q, clean(el), 800)]
        elif 'trow' in cls: S += [(A, clean(el.find(class_='tk')) + '। ' + clean(el.find(class_='tv')), 700)]
        elif el.name == 'tr': S += [(A, clean(el), 500)]
        elif el.name == 'p' and not el.find_parent(class_='trow') and not el.find_parent('li') and not el.find_parent('tr'):
            t = clean(el)
            if t: S += [(A, t, 600)]
        elif el.name == 'li' and not el.find(['ul','ol','p']):
            t = clean(el)
            if t: S += [(A, t, 600)]
    return S

async def tts(voice, text, sem):
    h = hashlib.md5(f'{voice}|{RATE}|{text}'.encode()).hexdigest()
    out = os.path.join(CACHE, h + '.mp3')
    if os.path.exists(out) and os.path.getsize(out) > 0: return out
    async with sem:
        for attempt in range(6):
            try:
                await edge_tts.Communicate(text, voice, rate=RATE, proxy=PROXY).save(out)
                if os.path.getsize(out) > 0: return out
            except Exception as e:
                print('retry', attempt, type(e).__name__, str(e)[:80], flush=True)
                await asyncio.sleep(3 * (attempt + 1))
        raise RuntimeError('tts failed: ' + text[:60])

def silence(ms):
    out = os.path.join(CACHE, f'sil{ms}.mp3')
    if not os.path.exists(out):
        subprocess.run([FF, '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', str(ms/1000), '-c:a', 'libmp3lame', '-b:a', '48k', out], check=True)
    return out

async def build(segments, outfile):
    sem = asyncio.Semaphore(3)
    files = await asyncio.gather(*[tts(v, t, sem) for v, t, _ in segments])
    lst = outfile + '.txt'
    with open(lst, 'w') as f:
        for (v, t, p), fn in zip(segments, files):
            f.write(f"file '{fn}'\nfile '{silence(p)}'\n")
    subprocess.run([FF, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c:a', 'libmp3lame', '-b:a', '64k', '-ar', '24000', '-ac', '1', outfile], check=True)
    os.remove(lst)

PARTS = [
 ('01','नियम, कवच, पहला और आख़िरी मिनट', ['kaise','kavach'], ['A1','A2','A3','A4']),
 ('02','सबसे पक्के सवाल, पहला हिस्सा', [], ['B1','B2','B3','B4','B5']),
 ('03','सबसे पक्के सवाल, दूसरा हिस्सा', [], ['B6','B7','B8','B9']),
 ('04','कक्षा और शिक्षण, पहला हिस्सा', [], ['C1','C2','C3','C4','C5']),
 ('05','कक्षा और शिक्षण, दूसरा हिस्सा', [], ['C6','C7','C8','C9','C10']),
 ('06','अपने बारे में, पहला हिस्सा', [], ['D1','D2','D3','D4','D5','D6','D7']),
 ('07','अपने बारे में, दूसरा हिस्सा', [], ['D8','D9','D10','D11','D12','D13']),
 ('08','परिस्थिति वाले प्रश्न, पहला हिस्सा', [], ['E1','E2','E3','E4','E5','E6']),
 ('09','परिस्थिति वाले प्रश्न, दूसरा हिस्सा', [], ['E7','E8','E9','E10','E11']),
 ('10','AI और आज, पहला हिस्सा', [], ['F1','F2','F3','F4','F5','F6','F7','F8']),
 ('11','AI और आज, दूसरा हिस्सा', [], ['F9','F10','F11','F12','F13','F14','F15']),
 ('12','केंद्रीय विद्यालय और नीति', [], ['G1','G2','G3','G4','G5','G8','G6','G7','G9']),
 ('13','तथ्य-कार्ड और नए प्रश्न', ['tathya','anjaan'], []),
 ('14','संस्कृत किट, पंच पंक्तियाँ, साक्षात्कार का दिन', ['kit','punch','din'], []),
]

def part_segments(soup, pid, title, secs, ids):
    num = NUM[int(pid)-1]
    S = [(Q, f'नमस्ते मंजू जी। यह भाग {num} है: {title}।', 600)]
    if ids:
        S += [(Q, 'हर प्रश्न के बाद चार सेकंड का ठहराव है। पहले खुद बोलकर देखिए, फिर उत्तर सुनिए। उत्तर हाँ, पर, हल, बच्चा के क्रम में है।', 1200)]
    for sid in secs:
        S += static_segments(BeautifulSoup(str(soup.find('section', id=sid)), 'html.parser'))
    for n, cid in enumerate(ids):
        S += card_segments(soup.find('article', attrs={'data-id': cid}), n)
    S += [(Q, f'भाग {num} पूरा हुआ। बहुत बढ़िया, मंजू जी।', 500)]
    return S

if __name__ == '__main__':
    soup = BeautifulSoup(open(os.path.join(HERE, '../notes/master-notes.html'), encoding='utf-8').read(), 'html.parser')
    want = sys.argv[1:] or [p[0] for p in PARTS]
    os.makedirs(os.path.join(HERE, 'mp3'), exist_ok=True)
    for pid, title, secs, ids in PARTS:
        if pid not in want: continue
        segs = part_segments(soup, pid, title, secs, ids)
        out = os.path.join(HERE, 'mp3', f'भाग-{pid}.mp3')
        asyncio.run(build(segs, out))
        print(pid, len(segs), 'segments', out)
