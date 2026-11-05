"""Download a fixed subset of the Pre-Roast Coffee Bean Grading Dataset (MIT, SamruddhK on Hugging Face)
and cut each bean out with its labelme polygon -> RGBA crop (max side 256 px)."""
import base64, io, json, os, random, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw
REPO = 'SamruddhK/coffee-bean-grading-dataset'; N_PER = int(sys.argv[1]) if len(sys.argv) > 1 else 320
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'crops'); os.makedirs(OUT, exist_ok=True)
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'DureGraderEval/0.1'})
    with urllib.request.urlopen(req, timeout=120) as r: return r.read()
def one(args):
    g, path = args
    out = os.path.join(OUT, f"{g}_{os.path.basename(path).rsplit('.',1)[0]}.png")
    if os.path.exists(out): return 'skip'
    try:
        d = json.loads(get(f'https://huggingface.co/datasets/{REPO}/resolve/main/{path}'))
        im = Image.open(io.BytesIO(base64.b64decode(d['imageData']))).convert('RGB')
        pts = [tuple(p) for s in d['shapes'] if s.get('shape_type') == 'polygon' for p in s['points']]
        if len(d['shapes']) != 1 or len(pts) < 3: return 'multi'
        m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
        bb = m.getbbox(); c = im.crop(bb); c.putalpha(m.crop(bb))
        c.thumbnail((256, 256), Image.LANCZOS); c.save(out); return 'ok'
    except Exception as e: return f'err {e}'
jobs = []
for g in ['CGA', 'CGB', 'CGC', 'CGD']:
    lst = json.loads(get(f'https://huggingface.co/api/datasets/{REPO}/tree/main/{g}/json'))
    paths = sorted(x['path'] for x in lst if x['path'].endswith('.json'))
    random.Random(0).shuffle(paths); jobs += [(g, p) for p in paths[:N_PER]]
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(one, jobs))
from collections import Counter; print(Counter(r.split()[0] for r in res)); print([r for r in res if r.startswith('err')][:5])
