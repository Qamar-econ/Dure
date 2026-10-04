import json,sys
T=json.load(open(sys.argv[2] if len(sys.argv)>2 and not sys.argv[2].startswith('-') else 'test.json'));P=json.load(open(sys.argv[1]))
F=['lang','crop','kg','ask','any','grade','yn']
ok={f:0 for f in F};ex=0;bad=[]
def eq(f,a,b):
    if f in('kg','ask'):
        return (a is None and b is None) or (a is not None and b is not None and abs(float(a)-float(b))<1e-6)
    if f=='any': return bool(a)==bool(b)
    return a==b
for t,p in zip(T,P):
    l=t['label'];good=True
    for f in F:
        if l['lang']=='unknown' and f!='lang': ok[f]+=1;continue
        # a bare number: any language guess is acceptable (conversation language is kept)
        if f=='lang' and l['lang'] is None: ok[f]+=1;continue
        if eq(f,l.get(f),p.get(f)): ok[f]+=1
        else: good=False
    ex+=good
    if not good: bad.append((t['msg'],{f:(l.get(f),p.get(f)) for f in F if not(f=='lang' and l['lang'] is None) and not(l['lang']=='unknown' and f!='lang') and not eq(f,l.get(f),p.get(f))}))
n=len(T);print(f"exact {ex}/{n} = {ex/n:.0%}  | "+'  '.join(f"{f} {ok[f]/n:.0%}" for f in F))
if '-v' in sys.argv:
    for b in bad: print(' ✗',b[0],b[1])
