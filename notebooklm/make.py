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
old = b.parse('../notes/master-notes.html')
def pick(secs=(), ids=()):
    out = []
    for sid, cid, lines in old:
        if (cid is None and sid in secs) or (cid in ids):
            out.append(lines)
    return out
R = lambda p, a, z: [f'{p}{i}' for i in range(a, z+1)]
N1 = [
 ('01-niyam-kavach-pehla-aakhri.txt','भाग 1 / 14 — नोट्स कैसे पढ़ें, नियम और कवच, पहला और आख़िरी मिनट (A1–A4)', ['kaise','kavach','shuru'], R('A',1,4)),
 ('02-pakke-sawal-B1-B5.txt','भाग 2 / 14 — सबसे पक्के सवाल: B1 से B5', ['pakke'], R('B',1,5)),
 ('03-pakke-sawal-B6-B9.txt','भाग 3 / 14 — सबसे पक्के सवाल: B6 से B9', [], R('B',6,9)),
 ('04-kaksha-C1-C5.txt','भाग 4 / 14 — कक्षा और शिक्षण: C1 से C5', ['kaksha'], R('C',1,5)),
 ('05-kaksha-C6-C10.txt','भाग 5 / 14 — कक्षा और शिक्षण: C6 से C10', [], R('C',6,10)),
 ('06-apne-baare-D1-D7.txt','भाग 6 / 14 — अपने बारे में: D1 से D7', ['apne'], R('D',1,7)),
 ('07-apne-baare-D8-D13.txt','भाग 7 / 14 — अपने बारे में: D8 से D13', [], R('D',8,13)),
 ('08-paristhiti-E1-E6.txt','भाग 8 / 14 — परिस्थिति वाले प्रश्न: E1 से E6', ['paristhiti'], R('E',1,6)),
 ('09-paristhiti-E7-E11.txt','भाग 9 / 14 — परिस्थिति वाले प्रश्न: E7 से E11', [], R('E',7,11)),
 ('10-AI-F1-F8.txt','भाग 10 / 14 — AI और आज: F1 से F8', ['aaj'], R('F',1,8)),
 ('11-aaj-F9-F15.txt','भाग 11 / 14 — AI और आज: F9 से F15', [], R('F',9,15)),
 ('12-kv-niti-G1-G9.txt','भाग 12 / 14 — केंद्रीय विद्यालय और नीति: G1 से G9', ['kvs'], ['G1','G2','G3','G4','G5','G8','G6','G7','G9']),
 ('13-tathya-card-naya-prashn.txt','भाग 13 / 14 — तथ्य-कार्ड (सब जाँचे हुए) और जो प्रश्न नोट्स में नहीं', ['tathya','anjaan'], []),
 ('14-sanskrit-kit-punch-din.txt','भाग 14 / 14 — संस्कृत किट (पूरा व्याकरण), पंच पंक्तियाँ, साक्षात्कार का दिन', ['kit','punch','din'], []),
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
    report.append(('N1',) + dump('notebook-1-master-notes', fn, title, blocks))
missing = [(s, c) for s, c, _ in old if (s, c) not in used]
print('N1 missing:', missing)

# ---------- Notebook 2: answer-structure page ----------
ds = BeautifulSoup(open('../notes/uttar-dhancha.html', encoding='utf-8').read(), 'html.parser')
inl = b.inline
def beats(card):
    cid = inl(card.find(class_='id')); q = inl(card.find('h3'))
    out = [f'\n### {cid} — {q}']
    out += [f'- {inl(li.find(class_="lab"))}: {inl(li.find(class_="cue"))}' for li in card.select('ol.beats li')]
    return out
intro = ['## मंजू जी, हर उत्तर का एक ही रास्ता: हाँ → पर → हल → बच्चा',
 '71 में से 51 उत्तर इन्हीं चार खानों में चलते हैं। हाँ = सीधा उत्तर या बात मान लेना। पर = असली बात, कारण या सबूत। हल = मैं क्या करूँगी। बच्चा = आख़िरी पंक्ति, बच्चे के फ़ायदे पर। चार पुल-शब्द, बस मन में: “जी सर… पर सर… इसलिए… सर…”। परिस्थिति वाले उत्तरों में: शांत = हाँ, समझ = पर, सुधार और संपर्क = हल, दिल वाली पंक्ति = बच्चा।']
d1 = ds.find('section', id='d1')
partA, partB = [], []
cur = partA
for el in d1.find_all(['h3', 'article'], recursive=True):
    if el.name == 'h3' and 'subhead' in (el.get('class') or []):
        if inl(el) in ('परिस्थिति वाले प्रश्न',): cur = partB
        cur.append('\n## ' + inl(el))
    elif el.name == 'article':
        cur += beats(el)
report.append(('N2',) + dump('notebook-2-naye-notes', '01-dhancha-A-se-D.txt', 'भाग 1 / 3 — हाँ → पर → हल → बच्चा: पहला मिनट, पक्के सवाल, कक्षा, अपने बारे में', [intro, partA]))
report.append(('N2',) + dump('notebook-2-naye-notes', '02-dhancha-E-se-G.txt', 'भाग 2 / 3 — हाँ → पर → हल → बच्चा: परिस्थिति, AI और आज, केंद्रीय विद्यालय', [intro[:1], partB]))
rest = []
for sid, title in (('d2', 'छोटा रूप — हाँ → बच्चा (तथ्य वाले, 15-20 सेकंड)'), ('d3', 'अपने क्रम वाले — इनका क्रम ही उत्तर है')):
    sec = ds.find('section', id=sid); rest.append('\n## ' + title)
    rest += [inl(p) for p in sec.select('.ghead p')]
    for a in sec.select('article.card'): rest += beats(a)
last = ds.find_all('div', class_='rule')[-1]
rest.append('\n## अनजान प्रश्न आए तो'); rest += ['- ' + inl(li) for li in last.find_all('li')]
report.append(('N2',) + dump('notebook-2-naye-notes', '03-chhota-roop-aur-apne-kram.txt', 'भाग 3 / 3 — छोटा रूप (हाँ → बच्चा) और अपने क्रम वाले उत्तर', [rest]))

for r in report: print(r)

