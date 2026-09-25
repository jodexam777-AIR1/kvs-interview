import re, os, copy
from bs4 import BeautifulSoup, Tag
import build_sources as b

CTX = ('ये नोट्स श्रीमती मंजू कुमारी जी के लिए हैं। वे हरियाणा के एक राजकीय विद्यालय में छठी से आठवीं को संस्कृत पढ़ाती हैं, '
       'और सोमवार 28 सितम्बर 2026 को गुरुग्राम के पी एम श्री केंद्रीय विद्यालय क्रमांक 1 में KVS TGT संस्कृत का साक्षात्कार देंगी। '
       'हर कार्ड में: प्रश्न → पहली पंक्ति (रटनी है) → चाबी (इसी क्रम में) → आख़िरी पंक्ति (रटनी है) → पूरा उत्तर → क्रॉस-प्रश्न। '
       '[बोलने का तरीका: …] बताता है कि कैसे बोलना है — ये शब्द बोलने नहीं हैं। [सच-जाँच] वाली पंक्ति तभी बोलनी है जब वह सच में हुई हो।')

def dump(folder, name, title, blocks):
    os.makedirs(folder, exist_ok=True)
    n = b.write(os.path.join(folder, name), title, CTX, blocks)
    return name, n

# ---------- Notebook 1: old master notes ----------
old = b.parse('../notes/Manju-KVS-Notes.html')
def pick(secs=(), ids=()):
    out = []
    for sid, cid, lines in old:
        if (cid is None and sid in secs) or (cid in ids):
            out.append(lines)
    return out
R = lambda p, a, z: [f'{p}{i}' for i in range(a, z+1)]
N1 = [
 ('01-niyam-kavach-pehla-aakhri.txt','भाग 1 / 13 — नोट्स कैसे पढ़ें, नियम और कवच, पहला और आख़िरी मिनट (A1–A4)', ['kaise','kavach','shuru'], R('A',1,4)),
 ('02-pakke-sawal-B1-B5.txt','भाग 2 / 13 — सबसे पक्के सवाल: B1 से B5', ['pakke'], R('B',1,5)),
 ('03-pakke-sawal-B6-B9.txt','भाग 3 / 13 — सबसे पक्के सवाल: B6 से B9', [], R('B',6,9)),
 ('04-kaksha-C1-C5.txt','भाग 4 / 13 — कक्षा और शिक्षण: C1 से C5', ['kaksha'], R('C',1,5)),
 ('05-kaksha-C6-C10.txt','भाग 5 / 13 — कक्षा और शिक्षण: C6 से C10', [], R('C',6,10)),
 ('06-apne-baare-D1-D7.txt','भाग 6 / 13 — अपने बारे में: D1 से D7', ['apne'], R('D',1,7)),
 ('07-apne-baare-D8-D13.txt','भाग 7 / 13 — अपने बारे में: D8 से D13', [], R('D',8,13)),
 ('08-paristhiti-E1-E6.txt','भाग 8 / 13 — परिस्थिति वाले प्रश्न: E1 से E6', ['paristhiti'], R('E',1,6)),
 ('09-paristhiti-E7-E11.txt','भाग 9 / 13 — परिस्थिति वाले प्रश्न: E7 से E11', [], R('E',7,11)),
 ('10-AI-F1-F8.txt','भाग 10 / 13 — AI और आज: F1 से F8', ['aaj'], R('F',1,8)),
 ('11-aaj-F9-F15.txt','भाग 11 / 13 — AI और आज: F9 से F15', [], R('F',9,15)),
 ('12-kv-niti-tathya-naya-prashn.txt','भाग 12 / 13 — केंद्रीय विद्यालय और नीति (G1–G8), तथ्य-कार्ड, जो प्रश्न नोट्स में नहीं', ['kvs','tathya','anjaan'], ['G1','G2','G3','G4','G5','G8','G6','G7']),
 ('13-sanskrit-kit-punch-din.txt','भाग 13 / 13 — संस्कृत किट, पंच पंक्तियाँ, साक्षात्कार का दिन', ['kit','punch','din'], []),
]
report = []
used = set()
for fn, title, secs, ids in N1:
    blocks = []
    for sid, cid, lines in old:
        if cid is None and sid in secs and (sid, None) not in used:
            blocks.append(lines); used.add((sid, None))
        elif cid in ids:
            blocks.append(lines); used.add((sid, cid))
    report.append(('N1',) + dump('notebook-1-purane-notes', fn, title, blocks))
missing = [(s, c) for s, c, _ in old if (s, c) not in used]
print('N1 missing:', missing)

# ---------- Notebook 2: new material ----------
soup = BeautifulSoup(open('../notes/master-notes.html', encoding='utf-8').read(), 'html.parser')
inl = b.inline

# 2a. answer-structure page
ds = BeautifulSoup(open('../notes/uttar-dhancha.html', encoding='utf-8').read(), 'html.parser')
L = ['## मंजू जी, हर उत्तर का एक ही रास्ता',
     'उत्तर शब्द-दर-शब्द नहीं रटने। बस यह याद रखिए कि उत्तर किस क्रम में चलता है। ज़्यादातर प्रश्नों का क्रम एक ही है: हाँ → पर → हल → बच्चा। इस हिस्से में कोई उत्तर बदला नहीं गया है — सारी पंक्तियाँ मास्टर नोट्स से ही हैं, बस हर उत्तर को चार खानों में बाँटकर दिखाया है।']
rule = ds.find('div', class_='rule')
L.append('\n### हर उत्तर के तीन पक्के नियम')
L += ['- ' + inl(li) for li in rule.find_all('li')]
parts = {'a': L, 'b': ['## बाक़ी चार ढाँचे — परिस्थिति, श्लोक-कहानी, तथ्य, और अपने क्रम वाले']}
for sec in ds.find_all('section', class_='group'):
    L = parts['a'] if sec.get('id') == 'd1' else parts['b']
    gh = sec.find(class_='ghead')
    L.append('\n## ' + inl(gh.find('h2')) + ' — ' + inl(gh.find(class_='gnum')))
    L += [inl(p) for p in gh.find_all('p')]
    lg = sec.find(class_='legend')
    if lg:
        chs = lg.find_all(class_='ch'); says = lg.find_all(class_='say')
        L.append('हर खाने का मतलब:')
        L += [f'- {inl(c)}: {inl(s)}' for c, s in zip(chs, says)]
    ex = sec.find(class_='example')
    if ex: L += ['याद रखने का तरीका: ' + inl(ex.find('p'))]
    for n in sec.find_all('p', class_='note', recursive=False): L.append(inl(n))
    for card in sec.select('article.card'):
        cid = inl(card.find(class_='id')); q = inl(card.find('h3'))
        L.append(f'\n### {cid} — {q}')
        for li in card.select('ol.beats li'):
            L.append(f'- {inl(li.find(class_="lab"))}: {inl(li.find(class_="cue"))}')
        for n in card.find_all('p', class_='note'): L.append(inl(n))
    for n in sec.select(':scope > p.note'):
        pass
last = ds.find_all('div', class_='rule')[-1]
L = parts['b']
L.append('\n### अनजान प्रश्न आए तो'); L += ['- ' + inl(li) for li in last.find_all('li')]
report.append(('N2',) + dump('notebook-2-naye-notes', '01-dhancha-haan-par-hal-bachcha.txt', 'भाग 1 / 5 — उत्तर का मुख्य ढाँचा: हाँ → पर → हल → बच्चा (34 उत्तर)', [parts['a']]))
report.append(('N2',) + dump('notebook-2-naye-notes', '02-baaki-chaar-dhanche.txt', 'भाग 2 / 5 — बाक़ी चार ढाँचे: परिस्थिति, श्लोक-कहानी, तथ्य, अपने क्रम वाले', [parts['b']]))

# 2b. new card + new crosses + new anjaan answers
g9 = b.card(soup.find('article', attrs={'data-id': 'G9'}))
extra = ['\n## पुराने कार्डों में जुड़े नए क्रॉस-प्रश्न']
for cid, q in (('F15', 'संस्कृत के लिए कुछ नया?'), ('G7', 'अभी शिक्षा मंत्री कौन हैं?')):
    art = soup.find('article', attrs={'data-id': cid})
    for x in art.select('.cross .xq'):
        if inl(x.find(class_='xqq')) == q:
            extra.append(f'- कार्ड {cid} ({inl(art.find(class_="q"))}) — नया क्रॉस: {q}\n  उत्तर: {inl(x.find(class_="xqa"))}')
extra.append('\n## ‘जो प्रश्न नोट्स में नहीं’ — तीन नए उत्तर')
an = soup.find('section', id='anjaan')
newq = ('पेपर लीक', 'अभी शिक्षा मंत्री कौन हैं? / केवि के आयुक्त?', 'संस्कृत किस राज्य')
for li in an.select('.li'):
    q = inl(li.find(class_='liq'))
    if any(q.startswith(k) for k in newq):
        extra.append(f'- प्रश्न: {q}\n  उत्तर: {inl(li.find(class_="lia"))}')
report.append(('N2',) + dump('notebook-2-naye-notes', '03-naya-card-G9-naye-cross.txt', 'भाग 3 / 5 — नया कार्ड G9 (केवि में संस्कृत का नया नियम), पुराने कार्डों के नए क्रॉस, और तीन नए उत्तर', [['## नया कार्ड'] + g9, extra]))

# 2c. full fact-card section
t = copy.copy(soup.find('section', id='tathya'))
lines = []; b.flat(t, lines)
report.append(('N2',) + dump('notebook-2-naye-notes', '04-tathya-card.txt', 'भाग 4 / 5 — तथ्य-कार्ड (सब तथ्य 24-25 सितम्बर 2026 को जाँचे गए)', [lines]))

# 2d. new grammar kit sections
kit = soup.find('section', id='kit')
frag = BeautifulSoup('<div></div>', 'html.parser').div
on = False
for c in list(kit.children):
    if isinstance(c, Tag) and c.name == 'h3' and c.get('id') == 'kit-sandhi': on = True
    if isinstance(c, Tag) and c.name == 'h3' and c.get('id') == 'kit-shlok': on = False
    if on: frag.append(copy.copy(c))
lines = ['## संस्कृत व्याकरण किट — नया हिस्सा']; b.flat(frag, lines)
report.append(('N2',) + dump('notebook-2-naye-notes', '05-sanskrit-vyakaran-kit.txt', 'भाग 5 / 5 — संस्कृत व्याकरण: संधि, समास, लकार, धातु-रूप, प्रत्यय, उपसर्ग, संख्या-वार, ग्रंथ-लेखक', [lines]))

for r in report: print(r)

p = 'notebook-1-purane-notes/12-kv-niti-tathya-naya-prashn.txt'
t = open(p, encoding='utf-8').read().split('\n')
t.insert(2, 'ज़रूरी सूचना: इस भाग का तथ्य-कार्ड पुराना है। नया, जाँचा हुआ तथ्य-कार्ड दूसरे नोटबुक (नए नोट्स) के भाग 4 में है। ‘कितने केंद्रीय विद्यालय’ पर अब ‘लगभग 1,288’ नहीं, ‘लगभग तेरह सौ’ बोलना है।')
open(p, 'w', encoding='utf-8').write('\n'.join(t))
