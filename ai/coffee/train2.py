"""Adapter v2: continue training the v1 LoRA adapter (lora/) for one short pass on train2.jsonl (targeted data + replay, from gen2.py).
Same LoRA shape and loss as train.py; lower learning rate because we start from a trained adapter.
Usage: python3 train2.py BASE_DIR  -> lora_v2/ (adapter) and MERGED_OUT (merged model, path from argv[2], default merged_v2)"""
import json, math, random, sys, time, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

torch.set_num_threads(2); torch.manual_seed(0); random.seed(0)
BASE = sys.argv[1] if len(sys.argv) > 1 else 'base'
MERGED = sys.argv[2] if len(sys.argv) > 2 else 'merged_v2'
BS, LR, MB = 8, 1e-4, 2

tok = AutoTokenizer.from_pretrained(BASE)
model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32)
model.gradient_checkpointing_enable(); model.enable_input_require_grads(); model.config.use_cache = False
model = PeftModel.from_pretrained(model, 'lora', is_trainable=True)
model.print_trainable_parameters()

def encode(ex):
    msgs = ex['messages']
    prompt = tok.apply_chat_template(msgs[:-1], add_generation_prompt=True, tokenize=False)
    full = prompt + msgs[-1]['content'] + '<|im_end|>\n'
    p_ids = tok(prompt, add_special_tokens=False)['input_ids']
    f_ids = tok(full, add_special_tokens=False)['input_ids']
    return f_ids, [-100] * len(p_ids) + f_ids[len(p_ids):]

data = [encode(json.loads(l)) for l in open('train2.jsonl')]
steps = math.ceil(len(data) / BS)
print(len(data), 'examples,', steps, 'steps', flush=True)
opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=LR, weight_decay=0.0)
sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1, (s + 1) / 10) * max(0.05, 1 - s / steps))
model.train(); order = random.sample(range(len(data)), len(data)); t0 = time.time()
for step in range(steps):
    batch = [data[order.pop()] for _ in range(min(BS, len(order)))]
    tot = 0.0
    for k in range(0, len(batch), MB):
        mb = batch[k:k + MB]; L = max(len(b[0]) for b in mb)
        ids = torch.tensor([b[0] + [tok.pad_token_id] * (L - len(b[0])) for b in mb])
        lab = torch.tensor([b[1] + [-100] * (L - len(b[1])) for b in mb])
        att = torch.tensor([[1] * len(b[0]) + [0] * (L - len(b[0])) for b in mb])
        loss = model(input_ids=ids, attention_mask=att, labels=lab).loss / math.ceil(len(batch) / MB)
        loss.backward(); tot += loss.item()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step(); sched.step(); opt.zero_grad()
    if step % 10 == 0 or step == steps - 1:
        el = time.time() - t0
        print(f'step {step+1}/{steps} loss {tot:.4f}  {el/(step+1):.1f}s/step  eta {el/(step+1)*(steps-step-1)/60:.1f} min', flush=True)
model.save_pretrained('lora_v2')
merged = model.merge_and_unload(); merged.save_pretrained(MERGED); tok.save_pretrained(MERGED)
print('saved lora_v2 and merged model', flush=True)
