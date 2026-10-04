"""Download a balanced subset of the Pre-Roast Coffee Bean Grading Dataset (MIT, SamruddhK on Hugging Face),
resize to 256 px on the short side, keep only the small copy."""
import io, json, os, random, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
API = 'https://huggingface.co/api/datasets/SamruddhK/coffee-bean-grading-dataset'
BASE = 'https://huggingface.co/datasets/SamruddhK/coffee-bean-grading-dataset/resolve/main/'
files = [s['rfilename'] for s in json.load(urllib.request.urlopen(API))['siblings'] if '/images/' in s['rfilename']]
R = random.Random(3); pick = []
for g in 'ABCD':
    fs = sorted(f for f in files if f.startswith(f'CG{g}/')); R.shuffle(fs); pick += fs[:300]
os.makedirs('img', exist_ok=True)
def get(f):
    out = 'img/' + f.split('/')[0] + '_' + os.path.splitext(os.path.basename(f))[0] + '.jpg'
    if os.path.exists(out): return 1
    for _ in range(3):
        try:
            data = urllib.request.urlopen(BASE + f, timeout=60).read()
            im = Image.open(io.BytesIO(data)).convert('RGB'); im.thumbnail((256 * 3, 256 * 3))
            w, h = im.size; s = 256 / min(w, h); im = im.resize((max(1, round(w * s)), max(1, round(h * s))))
            im.save(out, quality=90); return 1
        except Exception: pass
    return 0
with ThreadPoolExecutor(8) as ex: ok = sum(ex.map(get, pick))
print(ok, 'of', len(pick), 'images saved')
