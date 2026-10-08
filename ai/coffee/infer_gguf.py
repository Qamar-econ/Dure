"""Run the fine-tuned reader as a quantised GGUF file through llama.cpp, the way it would run on a hub laptop.
Usage: python3 infer_gguf.py dure-reader-q8_0.gguf pred_gguf_test3.json --test test3.json"""
import json, os, sys, time
from llama_cpp import Llama
from gen import SYSTEM
path, out = sys.argv[1], sys.argv[2]
T = json.load(open(sys.argv[sys.argv.index('--test') + 1] if '--test' in sys.argv else 'test.json'))
m = Llama(model_path=path, n_ctx=512, n_threads=int(os.environ.get('THREADS', '2')), seed=0, verbose=False)
res, times = [], []
for t in T:
    t0 = time.time()
    r = m.create_chat_completion(messages=[{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': f"expect={t['expect']}\nmsg: {t['msg']}"}],
                                 temperature=0, max_tokens=60)
    times.append(time.time() - t0)
    txt = r['choices'][0]['message']['content'].strip()
    try: res.append(json.loads(txt.split('\n')[0]))
    except Exception: res.append({})
json.dump(res, open(out, 'w'), ensure_ascii=False)
times.sort()
print(f"{sum(times) / len(times):.2f}s per message (median {times[len(times) // 2]:.2f}s, slowest {times[-1]:.2f}s), file {os.path.getsize(path) / 1e6:.0f} MB")
