import json, math, random, sys, time, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

torch.set_num_threads(2); torch.manual_seed(0); random.seed(0)
BASE, OUT = 'base', 'lora'
EPOCHS = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
BS, LR, MB = 8, 3e-4, 2

tok = AutoTokenizer.from_pretrained(BASE)
model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32)
model.gradient_checkpointing_enable(); model.enable_input_require_grads(); model.config.use_cache=False
model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type='CAUSAL_LM',
                                         target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']))
model.print_trainable_parameters()

def encode(ex):
    msgs = ex['messages']
    prompt = tok.apply_chat_template(msgs[:-1], add_generation_prompt=True, tokenize=False)
    full = prompt + msgs[-1]['content'] + '<|im_end|>\n'
    p_ids = tok(prompt, add_special_tokens=False)['input_ids']
    f_ids = tok(full, add_special_tokens=False)['input_ids']
    labels = [-100] * len(p_ids) + f_ids[len(p_ids):]
    return f_ids, labels

data = [encode(json.loads(l)) for l in open('train.jsonl')]
print(len(data), 'examples, max len', max(len(d[0]) for d in data))
steps = math.ceil(len(data) * EPOCHS / BS)
opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=LR, weight_decay=0.0)
sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1, (s + 1) / 20) * max(0.05, 1 - s / steps))
model.train(); order = []; t0 = time.time()
for step in range(steps):
    if len(order) < BS: order += random.sample(range(len(data)), len(data))
    batch = [data[order.pop()] for _ in range(BS)]
    tot = 0.0
    for k in range(0, BS, MB):
        mb = batch[k:k+MB]; L = max(len(b[0]) for b in mb)
        ids = torch.tensor([b[0] + [tok.pad_token_id] * (L - len(b[0])) for b in mb])
        lab = torch.tensor([b[1] + [-100] * (L - len(b[1])) for b in mb])
        att = torch.tensor([[1] * len(b[0]) + [0] * (L - len(b[0])) for b in mb])
        loss = model(input_ids=ids, attention_mask=att, labels=lab).loss / (BS // MB)
        loss.backward(); tot += loss.item()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step(); sched.step(); opt.zero_grad()
    if step % 10 == 0 or step == steps - 1:
        el = time.time() - t0
        print(f'step {step+1}/{steps} loss {tot:.4f}  {el/(step+1):.1f}s/step  eta {el/(step+1)*(steps-step-1)/60:.1f} min', flush=True)
model.save_pretrained(OUT)
merged = model.merge_and_unload(); merged.save_pretrained('merged'); tok.save_pretrained('merged')
print('saved merged model')
