"""Tests 5 and 6: two new sets of farmer SMS, written on 23 Oct 2026 by Claude Opus 5.5 from the service description and the
labelling conventions of tests 2-3, before any reader was scored on them.
  test5.json  development set: used to design the hybrid's routing.
  test6.json  held-out set: frozen, used once to report the result.
Same schema and conventions as test3.json (grade words: diak/moos/maran/good/clean -> A; ok/normal/'a few black beans' -> B;
metan barak/bokon/bolor/fuhuk/basa/aat/wet/mouldy -> C; no quality words -> null; cents -> dollars; other-language messages ->
lang 'unknown', other fields ignored; a bare number -> lang null)."""
import json

def L(lang, crop=None, kg=None, ask=None, any_=False, grade=None, yn=None):
    return {"lang": lang, "crop": crop, "kg": kg, "ask": ask, "any": any_, "grade": grade, "yn": yn}

def T(msg, label, expect='none'):
    return {"expect": expect, "msg": msg, "label": label}

C = 'coffee'
U = L('unknown')

test5 = [
    # Tetum offers
    T("bondia, hau fan kafe 60 kilu, presu minimu 1.35", L('tet', C, 60, 1.35)),
    T("kafe maran 85kg, hau hakarak 1.44", L('tet', C, 85, 1.44, grade='A')),
    T("kafe 40 kilu fuan metan barak. 0.90 deit", L('tet', C, 40, 0.9, grade='C')),
    T("Botarde maun. kafe hau nian 120 kg, folin saida deit ok", L('tet', C, 120, None, True)),
    T("kafe B 70kg, 1.30", L('tet', C, 70, 1.3, grade='B')),
    T("hau iha kafe 25 kilu, kualidade normal. 1 dolar 25", L('tet', C, 25, 1.25, grade='B')),
    T("kafe bokon 50 kg, fan 1.00", L('tet', C, 50, 1.0, grade='C')),
    T("fa'an kafe 300kg minimu 1.47 dolar. kafe moos", L('tet', C, 300, 1.47, grade='A')),
    T("Bondia! kafe 15 kilu, 135 sentavu", L('tet', C, 15, 1.35)),
    T("hau iha hudi 30 kilu", L('tet', 'other', 30)),
    T("kafe 90kg. presu 1,38", L('tet', C, 90, 1.38)),
    T("ha'u nia kafe basa uitoan, 35 kilu, 1.05", L('tet', C, 35, 1.05, grade='C')),
    T("kafe 200 kilu, hau la hatene presu", L('tet', C, 200)),
    T("Bon dia. Hau hakarak fa'an kafe 65 kg ho presu 2.80", L('tet', C, 65, 2.8)),
    T("kafe diak los 45kg minimu 2.95", L('tet', C, 45, 2.95, grade='A')),
    T("batata 100 kg 0.60", L('tet', 'other', 100, 0.6)),
    T("kafe 75 kilu. laimporta presu", L('tet', C, 75, None, True)),
    T("kafe A 110kg 1.49", L('tet', C, 110, 1.49, grade='A')),
    T("hau iha kafe 20 kg deit, fuan metan balun, 1.15", L('tet', C, 20, 1.15, grade='B')),
    T("presu kafe ohin hira maun?", L('tet', C)),
    T("Hau la fa'an kafe semana ne'e, obrigadu", L('tet', C)),
    T("kafe 55 kg ho kualidade diak, presu 1.42 ka liu", L('tet', C, 55, 1.42, grade='A')),
    T("kafe 140kg. $1.33", L('tet', C, 140, 1.33)),
    T("hau fan kafe bolor 60 kilu, folin hira deit", L('tet', C, 60, None, True, grade='C')),
    T("kafe pergaminho 80 kg, folin 1.40 minimu", L('tet', C, 80, 1.4)),
    T("Bondia, ha'u Joana husi Letefoho. kafe 30 kilu. 1.20", L('tet', C, 30, 1.2)),
    T("kafe hau 50 kilu no batar 40 kilu. kafe 1.36", L('tet', C, 50, 1.36)),
    T("kafe aat 25kg, 0.85", L('tet', C, 25, 0.85, grade='C')),
    # Tetum answers to a question
    T("80 kilu", L('tet', None, 80), 'kg'),
    T("hau iha 45kg", L('tet', None, 45), 'kg'),
    T("1.40 dolar", L('tet', None, None, 1.4), 'ask'),
    T("presu hira deit", L('tet', None, None, None, True), 'ask'),
    T("130 sentavu", L('tet', None, None, 1.3), 'ask'),
    T("sin", L('tet', yn='yes'), 'decide'),
    T("lae, hau hein", L('tet', yn='no'), 'decide'),
    T("diak, fa'an", L('tet', yn='yes'), 'decide'),
    T("la, folin ki'ik", L('tet', yn='no'), 'decide'),
    T("bele maun", L('tet', yn='yes'), 'decide'),
    # English
    T("hi i have coffee 70kg, minimum 1.35", L('en', C, 70, 1.35)),
    T("coffee 40 kg good and dry. 1.46", L('en', C, 40, 1.46, grade='A')),
    T("sell 100kg coffee whatever price", L('en', C, 100, None, True)),
    T("coffee with many black beans 30kg 0.90", L('en', C, 30, 0.9, grade='C')),
    T("I want to sell parchment 150 kg at 1.40 dollar", L('en', C, 150, 1.4)),
    T("cofee 25kg ok quality 1.2", L('en', C, 25, 1.2, grade='B')),
    T("rice 50kg", L('en', 'other', 50)),
    T("Good afternoon, coffee 60 kg, price 2.85 per kg", L('en', C, 60, 2.85)),
    T("coffee B grade 90kg 1.32", L('en', C, 90, 1.32, grade='B')),
    T("what is the price this week?", L('en')),
    T("50 kg only", L('en', None, 50), 'kg'),
    T("1.45 minimum", L('en', None, None, 1.45), 'ask'),
    T("whatever is fine", L('en', None, None, None, True), 'ask'),
    T("yes please", L('en', yn='yes'), 'decide'),
    T("no, not now", L('en', yn='no'), 'decide'),
    T("ok sell", L('en', yn='yes'), 'decide'),
    # other languages: decline
    T("Selamat siang, kopi saya 60 kg, harga 1,35", U),
    T("Saya mau jual kopi bagus 40 kilo", U),
    T("Boa tarde, tenho 50 kg de café para vender", U),
    T("Quanto custa o café hoje?", U),
    T("Buenos días, vendo café 30 kilos a 1,40", U),
    T("我有咖啡50公斤", U),
    T("Terima kasih banyak", U),
    # bare numbers
    T("70", L(None, None, 70), 'kg'),
    T("1.25", L(None, None, None, 1.25), 'ask'),
    T("135", L(None, None, None, 1.35), 'ask'),
]

test6 = [
    # Tetum offers
    T("bondia maun, kafe 50 kilu, minimu 1.40", L('tet', C, 50, 1.4)),
    T("kafe moos no maran 95kg, 1.48", L('tet', C, 95, 1.48, grade='A')),
    T("ha'u fan kafe 35 kg, fuan metan uitoan deit, 1.18", L('tet', C, 35, 1.18, grade='B')),
    T("kafe 60kg folin saida de'it", L('tet', C, 60, None, True)),
    T("kafe C 40 kilu 0.95", L('tet', C, 40, 0.95, grade='C')),
    T("Botarde. hau iha kafe 130 kg, hakarak 1.37", L('tet', C, 130, 1.37)),
    T("kafe fuhuk 20kg, fan 0.80", L('tet', C, 20, 0.8, grade='C')),
    T("kafe 250 kilu diak, minimu 1.46", L('tet', C, 250, 1.46, grade='A')),
    T("kafe 45 kg, 140 sentavus", L('tet', C, 45, 1.4)),
    T("hau iha fehuk 60 kilu", L('tet', 'other', 60)),
    T("kafe 100kg presu 1,32 minimu", L('tet', C, 100, 1.32)),
    T("kafe basa 30 kilu, 1 dolar", L('tet', C, 30, 1.0, grade='C')),
    T("hau iha kafe 75kg maibe seidauk hatene folin", L('tet', C, 75)),
    T("Bondia, kafe 55 kilu, presu 2.90 bele?", L('tet', C, 55, 2.9)),
    T("kafe A 70kg minimu 3.10", L('tet', C, 70, 3.1, grade='A')),
    T("modo 40 kg", L('tet', 'other', 40)),
    T("kafe 85 kilu, presu hotu-hotu diak", L('tet', C, 85, None, True)),
    T("kafe grade B 120kg 1.31", L('tet', C, 120, 1.31, grade='B')),
    T("kafe 28 kg kualidade ok deit. 1.15", L('tet', C, 28, 1.15, grade='B')),
    T("ohin presu kafe hira?", L('tet', C)),
    T("hau seidauk iha kafe atu fa'an", L('tet', C)),
    T("Hau nia kafe diak liu, 65 kg, hakarak 1.45 ka liu", L('tet', C, 65, 1.45, grade='A')),
    T("kafe 160kg. 1.34$", L('tet', C, 160, 1.34)),
    T("kafe bolor 15 kilu, presu saida deit", L('tet', C, 15, None, True, grade='C')),
    T("kafe parchment 90 kg, minimu 1.39", L('tet', C, 90, 1.39)),
    T("Bondia, hau Ana husi Ermera. kafe 40 kilu. 1.25", L('tet', C, 40, 1.25)),
    T("hau iha kafe 70 kilu no fore 15 kilu. kafe 1.33", L('tet', C, 70, 1.33)),
    T("kafe aat los 35kg, 0.75", L('tet', C, 35, 0.75, grade='C')),
    # Tetum answers to a question
    T("60 kilu", L('tet', None, 60), 'kg'),
    T("kilu 120", L('tet', None, 120), 'kg'),
    T("hau hakarak 1.35", L('tet', None, None, 1.35), 'ask'),
    T("folin saida deit", L('tet', None, None, None, True), 'ask'),
    T("1 dolar 30", L('tet', None, None, 1.3), 'ask'),
    T("sim", L('tet', yn='yes'), 'decide'),
    T("lae obrigada", L('tet', yn='no'), 'decide'),
    T("diak, hau konkorda", L('tet', yn='yes'), 'decide'),
    T("la bele, ki'ik liu", L('tet', yn='no'), 'decide'),
    T("sin maun, fa'an", L('tet', yn='yes'), 'decide'),
    # English
    T("hello coffee 80kg minimum 1.38", L('en', C, 80, 1.38)),
    T("coffee 35 kg clean and dry, 1.47", L('en', C, 35, 1.47, grade='A')),
    T("sell coffee 60kg any price ok", L('en', C, 60, None, True)),
    T("coffee lots of black beans 25kg 0.85", L('en', C, 25, 0.85, grade='C')),
    T("I would like to sell 200 kg parchment, lowest 1.36 dollar", L('en', C, 200, 1.36)),
    T("cofee 45kg normal quality 1.22", L('en', C, 45, 1.22, grade='B')),
    T("cassava 70kg", L('en', 'other', 70)),
    T("Good morning, coffee 50 kg, price 2.75 per kg", L('en', C, 50, 2.75)),
    T("coffee grade A 100kg 1.50", L('en', C, 100, 1.5, grade='A')),
    T("when is pickup this week?", L('en')),
    T("about 40 kg", L('en', None, 40), 'kg'),
    T("minimum 1.30", L('en', None, None, 1.3), 'ask'),
    T("any price", L('en', None, None, None, True), 'ask'),
    T("yes", L('en', yn='yes'), 'decide'),
    T("no thank you", L('en', yn='no'), 'decide'),
    T("ok go ahead", L('en', yn='yes'), 'decide'),
    # other languages: decline
    T("Pagi pak, kopi 80 kg harga 1,40", U),
    T("Saya punya kopi kering 25 kilo", U),
    T("Bom dia, quero vender café, 60 quilos", U),
    T("Qual é o preço do café?", U),
    T("Hola, tengo 50 kilos de café", U),
    T("Bonsoir, café 30 kg", U),
    T("Sampai jumpa", U),
    # bare numbers
    T("90", L(None, None, 90), 'kg'),
    T("1.40", L(None, None, None, 1.4), 'ask'),
    T("125", L(None, None, None, 1.25), 'ask'),
]

if __name__ == '__main__':
    for name, d in (('test5.json', test5), ('test6.json', test6)):
        json.dump(d, open(name, 'w'), ensure_ascii=False, indent=0)
        print(name, len(d))
