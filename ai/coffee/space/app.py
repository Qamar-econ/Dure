"""Dure message reader: a fine-tuned 0.5B model behind one small HTTP endpoint.

POST /parse {"msg": "...", "expect": "none|kg|ask|decide"}
 -> {"ok": true, "result": {lang, crop, kg, ask, any, grade, yn}, "ms": 812, "model": "..."}
The web demo calls this and falls back to its rule-based reader when the
endpoint is slow, asleep or returns something it cannot use.
"""
import json, os, time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# MODEL_ID: a .gguf file (8-bit, llama.cpp; what a hub laptop would run) or a Hugging Face model folder (full precision)
MODEL = os.environ.get('MODEL_ID', './dure-reader-q8_0.gguf')
SYSTEM = "You read SMS from coffee farmers for Dure. Return one line of JSON only."
KEYS = ['lang', 'crop', 'kg', 'ask', 'any', 'grade', 'yn']
THREADS = max(1, os.cpu_count() or 1)
if MODEL.endswith('.gguf'):
    from llama_cpp import Llama
    llm = Llama(model_path=MODEL, n_ctx=512, n_threads=THREADS, seed=0, verbose=False)
    def generate(msgs):
        r = llm.create_chat_completion(messages=msgs, temperature=0, max_tokens=60)
        return r['choices'][0]['message']['content'].strip()
else:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.set_num_threads(THREADS)
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32).eval()
    def generate(msgs):
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors='pt', return_dict=True)
        with torch.no_grad():
            o = model.generate(**ids, max_new_tokens=60, do_sample=False)
        return tok.decode(o[0][ids['input_ids'].shape[1]:], skip_special_tokens=True).strip()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

class Req(BaseModel):
    msg: str
    expect: str = 'none'

def clean(d):
    """Keep only the fields we expect, with the types the demo expects."""
    out = {k: d.get(k) for k in KEYS}
    if out['lang'] not in ('tet', 'en', 'unknown', None): out['lang'] = None
    if out['crop'] not in ('coffee', 'other', None): out['crop'] = None
    for k in ('kg', 'ask'):
        try: out[k] = None if out[k] is None else float(out[k])
        except (TypeError, ValueError): out[k] = None
    out['any'] = bool(out['any'])
    if out['grade'] not in ('A', 'B', 'C', None): out['grade'] = None
    if out['yn'] not in ('yes', 'no', None): out['yn'] = None
    return out

@app.get('/')
@app.get('/health')
def health():
    return {'ok': True, 'model': os.path.basename(MODEL)}

@app.post('/parse')
def parse(r: Req):
    t0 = time.time()
    msgs = [{'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': f"expect={r.expect}\nmsg: {r.msg[:300]}"}]
    txt = generate(msgs)
    ms = int((time.time() - t0) * 1000)
    try:
        return {'ok': True, 'result': clean(json.loads(txt.split('\n')[0])), 'ms': ms, 'model': os.path.basename(MODEL)}
    except Exception:
        return {'ok': False, 'raw': txt, 'ms': ms, 'model': os.path.basename(MODEL)}
