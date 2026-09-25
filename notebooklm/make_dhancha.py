import re, html
from bs4 import BeautifulSoup
M=BeautifulSoup(open('master-notes.html',encoding='utf-8').read(),'html.parser')
page=open('uttar-dhancha.html',encoding='utf-8').read()
head=page[:page.find('<!-- ① -->')]
tail=page[page.find('<div class="rule">\n  <h3>अनजान प्रश्न आए तो</h3>'):]

head=head.replace('''  <nav class="jump" aria-label="ढाँचे">
    <a href="#d1">① हाँ-पर-हल-बच्चा</a>
    <a href="#d2">② परिस्थिति</a>
    <a href="#d3">③ श्लोक-कहानी</a>
    <a href="#d4">④ तथ्य</a>
    <a href="#d5">⑤ अपने क्रम वाले</a>
  </nav>''','''  <nav class="jump" aria-label="हिस्से">
    <a href="#d1">पूरे चार खाने · 51</a>
    <a href="#d2">छोटा रूप · 6</a>
    <a href="#d3">अपने क्रम वाले · 8</a>
  </nav>''')
head=re.sub(r'<p>उत्तर शब्द-दर-शब्द नहीं रटने।.*?</p>','<p>उत्तर शब्द-दर-शब्द नहीं रटने। बस यह याद रखिए कि उत्तर <b>किस क्रम में चलता है</b>। 71 में से 51 उत्तर एक ही क्रम में चलते हैं:</p>',head,count=1,flags=re.S)
head=head.replace('इस पन्ने में कोई उत्तर बदला नहीं गया है। सारी पंक्तियाँ आपकी मास्टर नोट्स से ही हैं। यहाँ हर उत्तर को सिर्फ़ इन चार खानों में बाँटकर दिखाया है।',
 'सारी पंक्तियाँ मास्टर नोट्स से ही हैं। परिस्थिति वाले उत्तर भी इसी में हैं: शांत = हाँ, समझ = पर, सुधार और संपर्क = हल, दिल वाली पंक्ति = बच्चा।')

SEC={'shuru':'पहला और आख़िरी मिनट','pakke':'सबसे पक्के सवाल','kaksha':'कक्षा और शिक्षण','apne':'अपने बारे में','paristhiti':'परिस्थिति वाले प्रश्न','aaj':'AI और आज','kvs':'केंद्रीय विद्यालय और नीति'}
def txt(el):
    if el is None: return ''
    for st in el.select('.stage'): st.decompose()
    return el.decode_contents().strip()
full=[];short=[];own=[]
for art in M.select('article.card'):
    cid=art['data-id']; sec=art.find_parent('section')['id']
    q=art.find(class_='q').get_text(' ',strip=True)
    lab=art.select_one('.row.first .lab')
    fl=txt(art.select_one('.row.first p')); ll=txt(art.select_one('.row.last p'))
    slots=art.select('.beats .n.slot')
    if slots:
        par=txt(art.select('.row.keys .t')[0]); hal=txt(art.select('.row.keys .t')[1])
        full.append((sec,cid,q,fl,par,hal,ll))
    elif lab and 'हाँ' in lab.get_text():
        mid=' · '.join(txt(t) for t in art.select('.row.keys .t'))
        short.append((sec,cid,q,fl,mid,ll))
    else:
        keys=[txt(t) for t in art.select('.row.keys .t')]
        own.append((sec,cid,q,fl,keys,ll))
assert len(full)==51 and len(short)==6, (len(full),len(short),len(own))

def li(lab,cls,cue): return f'      <li><span class="lab {cls}">{lab}</span><span class="cue">{cue}</span></li>\n'
out=[]
out.append('''<!-- ① -->
<section class="group" id="d1">
  <div class="ghead">
    <div class="gnum">पूरे चार खाने · 51 उत्तर</div>
    <h2>हाँ → पर → हल → बच्चा</h2>
    <p>“क्यों”, “आपके बारे में”, “आपकी राय”, “कैसे पढ़ाएँगी”, परिस्थिति, श्लोक-कहानी वाले, और दबाव वाले प्रश्न।</p>
  </div>
  <div class="legend">
    <span class="ch k1">हाँ</span><span class="say">सीधा उत्तर, या बात मान लेना, या पहली शांत बात। शुरू: <b>“जी सर…”</b></span>
    <span class="ch k2">पर</span><span class="say">असली बात: कारण, कमी, सच्चाई या सबूत (बच्ची, श्लोक, मार्कशीट)। शुरू: <b>“पर सर…”</b></span>
    <span class="ch k3">हल</span><span class="say">मैं क्या करूँगी, या केंद्रीय विद्यालय कैसे बेहतर करेगा। शुरू: <b>“इसलिए…”</b></span>
    <span class="ch k4">बच्चा</span><span class="say">आख़िरी पंक्ति, बच्चे के फ़ायदे पर या आगे की बात पर। शुरू: <b>(1 सेकंड) “सर…”</b></span>
  </div>
  <div class="example">
    <h3>याद रखने का तरीका</h3>
    <p>चार पुल-शब्द, बस मन में: <b>“जी सर… पर सर… इसलिए… सर…”</b> पुल-शब्द आते ही अगला खाना अपने आप याद आ जाता है।</p>
  </div>
''')
cur=None
for sec,cid,q,fl,par,hal,ll in full:
    if sec!=cur:
        if cur: out.append('  </div>\n')
        out.append(f'  <h3 class="subhead">{SEC[sec]}</h3>\n  <div class="cards">\n'); cur=sec
    out.append(f'    <article class="card" id="{cid}"><header><span class="id">{cid}</span><h3>{html.escape(q)}</h3></header><ol class="beats">\n'
               + li('हाँ','k1',fl)+li('पर','k2',par)+li('हल','k3',hal)+li('बच्चा','k4',f'<q>{ll}</q>')+'    </ol></article>\n')
out.append('  </div>\n</section>\n')
out.append('''
<section class="group" id="d2">
  <div class="ghead">
    <div class="gnum">छोटा रूप · 6 तथ्य वाले उत्तर · 15-20 सेकंड</div>
    <h2>हाँ → बच्चा</h2>
    <p>तथ्य वाले प्रश्न में भाषण नहीं। सीधा उत्तर, बीच में एक पंक्ति, और आख़िरी पंक्ति। बस।</p>
  </div>
  <div class="cards">
''')
for sec,cid,q,fl,mid,ll in short:
    out.append(f'    <article class="card" id="{cid}"><header><span class="id">{cid}</span><h3>{html.escape(q)}</h3></header><ol class="beats">\n'
               + li('हाँ','k1',fl)+li('बीच में','k3',mid)+li('बच्चा','k4',f'<q>{ll}</q>')+'    </ol></article>\n')
out.append('  </div>\n</section>\n')
out.append('''
<section class="group" id="d3">
  <div class="ghead">
    <div class="gnum">अपने क्रम वाले · रटने हैं</div>
    <h2>इनका क्रम ही उत्तर है</h2>
    <p>ये उत्तर जानबूझकर अपने तय क्रम में हैं। ‘संस्कृत का महत्व’ वाला उत्तर (B4) पैनल के ही शब्द पकड़ता है, इसलिए उसे बदला नहीं गया।</p>
  </div>
  <div class="cards">
''')
for sec,cid,q,fl,keys,ll in own:
    beats=[fl]+keys+([f'<q>{ll}</q>'] if ll else [])
    beats=[x for x in beats if x]
    if not beats: continue
    out.append(f'    <article class="card" id="{cid}"><header><span class="id">{cid}</span><h3>{html.escape(q)}</h3></header><ol class="beats">\n'
               + ''.join(li(str(i+1),['k1','k5','k3','k2','k4'][min(i,4)] if i<len(beats)-1 else 'k4',b) for i,b in enumerate(beats))+'    </ol></article>\n')
out.append('  </div>\n  <p class="note">बाक़ी छोटे उत्तर (A3 अंग्रेज़ी परिचय, C10 विधियाँ, D13 और F6 छोटे प्रश्न, E11 भूकंप, G5, G6, G8) नोट्स में जैसे हैं वैसे ही।</p>\n</section>\n\n')
new=head+''.join(out)+tail
new=new.replace('.note{font-size:14px;color:var(--muted)}','.note{font-size:14px;color:var(--muted)}\n.subhead{margin-top:10px;font-size:15px;color:var(--muted);font-weight:600;letter-spacing:.02em}',1)
open('uttar-dhancha.html','w',encoding='utf-8').write(new)
print(len(full),len(short),len(own),[o[1] for o in own])
