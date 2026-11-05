"""Fetch Wikimedia Commons photos by search query (500 px standard thumbnails) for the R (roasted), G (real green/parchment,
kind check only) and N (not coffee beans) sets. Keeps title/artist/licence for credits."""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'DureGraderEval/0.1 (research script)'}
ROOT = os.path.join(os.path.dirname(__file__), '..', 'data', 'commons')
SETS = {
 'R': ['roasted coffee beans', 'roasted coffee beans closeup', 'espresso beans', 'dark roast coffee beans', 'coffee roaster beans cooling', 'roasted arabica beans', 'medium roast coffee'],
 'G': ['green coffee beans', 'unroasted coffee beans', 'parchment coffee', 'coffee beans drying', 'raw coffee beans', 'green coffee sorting', 'coffee drying patio', 'arabica green beans'],
 'N': ['soybeans', 'peanuts shelled', 'rice grains', 'cocoa beans', 'coffee cherries', 'maize kernels', 'red kidney beans', 'lentils', 'tarpaulin', 'jute sack', 'concrete floor texture',
       'Timor-Leste village', 'vegetable market', 'dog portrait', 'human hand', 'mobile phone', 'fallen leaves ground', 'cup of coffee', 'pebbles', 'wood texture'],
}
EXCLUDE = {v['title'].replace(' ', '_') for v in json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'dure', 'ai', 'photo', 'commons', 'meta.json'))).values()}
def api(q, n):
    p = {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6, 'gsrsearch': q + ' filetype:bitmap', 'gsrlimit': n,
         'prop': 'imageinfo', 'iiprop': 'url|mime|extmetadata', 'iiurlwidth': 500}
    for k in range(6):
        try:
            r = urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p), headers=UA), timeout=60)
            return list(json.load(r).get('query', {}).get('pages', {}).values())
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(10 * (k + 1))
    return []
def strip(h): return re.sub('<[^>]+>', '', h or '').strip()
ROUND = os.environ.get('ROUND', '')
if ROUND == '2':
    SETS = {'R': ['coffee beans', 'coffee bean texture', 'roasted beans macro', 'coffee beans background', 'kopi bubuk biji sangrai', 'cafe tostado granos'],
            'G': ['green coffee', 'green coffee bean texture', 'coffee parchment', 'dried coffee beans', 'coffee processing beans', 'coffee hulling', 'Timor coffee',
                  'Ethiopian coffee beans raw', 'robusta beans', 'coffee sorting beans', 'grãos de café verde', 'kopi hijau', 'café pergamino', 'green coffee defects', 'coffee beans sack']}
    old = json.load(open(os.path.join(ROOT, 'meta.json'))); EXCLUDE |= {m['title'][5:].replace(' ', '_') for m in old.values()}
seen, meta, jobs = set(), {}, []
for s, qs in SETS.items():
    os.makedirs(os.path.join(ROOT, s + ROUND), exist_ok=True)
    per = 40 if ROUND == '2' else (30 if s != 'N' else 14)
    for q in qs:
        for pg in api(q, per):
            t = pg['title'][5:].replace(' ', '_')
            ii = (pg.get('imageinfo') or [{}])[0]
            if t in seen or t in EXCLUDE or ii.get('mime') not in ('image/jpeg', 'image/png') or 'thumburl' not in ii: continue
            seen.add(t); fn = re.sub(r'[^A-Za-z0-9_.-]', '_', t)[:120].rsplit('.', 1)[0] + '.jpg'
            em = ii.get('extmetadata', {})
            meta[f'{s}{ROUND}/{fn}'] = {'set': s, 'query': q, 'title': pg['title'], 'page': ii.get('descriptionurl'),
                                 'artist': strip(em.get('Artist', {}).get('value')), 'license': strip(em.get('LicenseShortName', {}).get('value'))}
            jobs.append((ii['thumburl'], os.path.join(ROOT, s + ROUND, fn)))
        time.sleep(1); print(s, q, len(jobs), flush=True)
print('to download', len(jobs), flush=True)
def dl(j):
    u, out = j
    if os.path.exists(out): return 'have'
    for k in range(4):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read(); open(out, 'wb').write(b); time.sleep(.3); return 'ok'
        except Exception as e:
            err = str(e); time.sleep(5 + 10 * k)
    print('fail', err, u[-60:], flush=True); return 'fail'
with ThreadPoolExecutor(2) as ex: list(ex.map(dl, jobs))
json.dump(meta, open(os.path.join(ROOT, f'meta{ROUND}.json'), 'w'), indent=1)
from collections import Counter; print(Counter(m['set'] for k, m in meta.items() if os.path.exists(os.path.join(ROOT, k))))
