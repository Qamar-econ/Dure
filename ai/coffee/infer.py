import json,sys,time,torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from gen import SYSTEM
torch.set_num_threads(2)
path=sys.argv[1];out=sys.argv[2]
tok=AutoTokenizer.from_pretrained(path);m=AutoModelForCausalLM.from_pretrained(path,torch_dtype=torch.float32).eval()
FEW=[] if '--fewshot' not in sys.argv else [
 {"role":"user","content":"expect=none\nmsg: bondia hau fan kafe 40 kilu, fuhuk barak, 1 dolar"},
 {"role":"assistant","content":'{"lang":"tet","crop":"coffee","kg":40,"ask":1.0,"any":false,"grade":"C","yn":null}'},
 {"role":"user","content":"expect=decide\nmsg: yes"},
 {"role":"assistant","content":'{"lang":"en","crop":null,"kg":null,"ask":null,"any":false,"grade":null,"yn":"yes"}'}]
def run(expect,msg):
    msgs=[{"role":"system","content":SYSTEM+(' Keys: lang (tet/en/unknown), crop (coffee/other/null), kg, ask (USD per kg), any (bool), grade (A good/B ok/C bad/null), yn (yes/no/null).' if FEW else '')}]+FEW+[{"role":"user","content":f"expect={expect}\nmsg: {msg}"}]
    ids=tok.apply_chat_template(msgs,add_generation_prompt=True,return_tensors='pt',return_dict=True)
    with torch.no_grad(): o=m.generate(**ids,max_new_tokens=60,do_sample=False)
    txt=tok.decode(o[0][ids['input_ids'].shape[1]:],skip_special_tokens=True).strip()
    try: return json.loads(txt.split('\n')[0]),txt
    except Exception: return {},txt
T=json.load(open(sys.argv[sys.argv.index('--test')+1] if '--test' in sys.argv else 'test.json'));res=[];t0=time.time()
for t in T:
    p,raw=run(t['expect'],t['msg']);res.append(p)
    if '-v' in sys.argv: print(t['msg'],'=>',raw)
json.dump(res,open(out,'w'),ensure_ascii=False);print(f"{(time.time()-t0)/len(T):.2f}s per message")
