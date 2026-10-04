# Hand-written test messages for the coffee reader. Written separately from the
# gen.py templates (different phrasing, word order and spellings) so the score
# is not just "the model memorised the generator". Same author as gen.py, so
# this is still not an independent test.
# (expect, message, label)  label keys: lang crop kg ask any grade yn
import json

def L(lang=None, crop=None, kg=None, ask=None, any_=False, grade=None, yn=None):
    return {"lang": lang, "crop": crop, "kg": kg, "ask": ask, "any": any_, "grade": grade, "yn": yn}

TESTS = [
 # --- Tetum: full offers
 ('none', 'bondia! kafe 40kilu diak los.. fan 1.45 bele?', L('tet', 'coffee', 40, 1.45, grade='A')),
 ('none', 'Bondia mana, ohin hau iha kafé kilu 60. Moos.', L('tet', 'coffee', 60, grade='A')),
 ('none', 'kafe 100kg, folin la importa', L('tet', 'coffee', 100, any_=True)),
 ('none', 'hau hakarak fan kafé. kilu 45', L('tet', 'coffee', 45)),
 ('none', 'botarde. kafe kg 30 aat uitoan', L('tet', 'coffee', 30, grade='C')),
 ('none', 'hau iha batar kilu 50', L('tet', 'other', 50)),
 ('none', 'fan kafé atus ida kilu, folin minimu 1 dolar 30 sentavu', L('tet', 'coffee', 100, 1.30)),
 ('none', 'kafe maran 25 kilu, metan barak. 1,00 de\'it', L('tet', 'coffee', 25, 1.00, grade='C')),
 ('none', 'ami nia kafé kilu 80 diak, folin 1.40', L('tet', 'coffee', 80, 1.40, grade='A')),
 ('none', 'Olá maun Dure, hau fan kafe 35kg normal', L('tet', 'coffee', 35, grade='B')),
 ('none', 'kafé 50 kg bokon uitoan, la importa folin', L('tet', 'coffee', 50, any_=True, grade='C')),
 ('none', 'hau atu fan kopi 20 kilu, harga 1.20', L('tet', 'coffee', 20, 1.20)),
 ('none', 'kafe empat puluh kilo diak', L('tet', 'coffee', 40, grade='A')),
 ('none', 'kafe quarenta quilo, minimu dolar 1.35', L('tet', 'coffee', 40, 1.35)),
 ('none', 'BONDIA HAU IHA KAFE 70KG MOOS 1.42', L('tet', 'coffee', 70, 1.42, grade='A')),
 ('none', 'kafe 60kilu, la kiak liu 1,25', L('tet', 'coffee', 60, 1.25)),
 ('none', "hau hakarak fa'an kafé kulit mutin kilograma 50, kualidade diak", L('tet', 'coffee', 50, grade='A')),
 ('none', 'kafe fuhuk balun, kilo 30, $1,05', L('tet', 'coffee', 30, 1.05, grade='C')),
 ('none', 'obrigadu barak Dure, hau sei haruka foto aban', L('tet')),
 # --- Tetum: replies to one question
 ('kg', 'kilu 70', L('tet', kg=70)),
 ('kg', '55', L(kg=55)),
 ('kg', 'kilu haatnulu', L('tet', kg=40)),
 ('ask', '1 dolar 45 sentavu', L('tet', ask=1.45)),
 ('ask', 'la importa', L('tet', any_=True)),
 ('ask', '1.39', L(ask=1.39)),
 ('ask', 'minimu 1,30', L('tet', ask=1.30)),
 ('decide', 'loos', L('tet', yn='yes')),
 ('decide', 'lae obrigadu', L('tet', yn='no')),
 ('decide', 'loos, hau fan', L('tet', yn='yes')),
 ('decide', 'lae, hein uluk', L('tet', yn='no')),
 # --- English
 ('none', 'coffee 40kg, clean, 1.40', L('en', 'coffee', 40, 1.40, grade='A')),
 ('none', 'Hi I have about 75 kg parchment, very good. 1.45 min', L('en', 'coffee', 75, 1.45, grade='A')),
 ('none', 'selling fifty kilos of coffee', L('en', 'coffee', 50)),
 ('none', 'want to sell rice 20kg', L('en', 'other', 20)),
 ('none', 'cofee 90 kilos a bit mouldy, any price', L('en', 'coffee', 90, any_=True, grade='C')),
 ('none', 'parchment 120kg not bad $1.28', L('en', 'coffee', 120, 1.28, grade='B')),
 ('none', 'morning, dry coffee 30 kilos for 1.35 a kilo', L('en', 'coffee', 30, 1.35)),
 ('kg', 'around 110', L('en', kg=110)),
 ('kg', 'forty kg', L('en', kg=40)),
 ('ask', '$1.44', L(ask=1.44)),
 ('ask', 'whatever is fine', L('en', any_=True)),
 ('ask', 'not less than 1.30', L('en', ask=1.30)),
 ('decide', 'ok go ahead', L('en', yn='yes')),
 ('decide', 'nope', L('en', yn='no')),
 ('decide', 'yes sell it', L('en', yn='yes')),
 # --- unsupported languages (Dure asks for Tetum or English)
 ('none', 'halo mau jual kopi 50 kg bagus', L('unknown')),
 ('none', 'bom dia, vendo 60 kg de café seco', L('unknown')),
 ('none', 'Selamat siang, kopi saya 40 kilo', L('unknown')),
 ('none', 'tenho café para vender', L('unknown')),
 ('kg', 'nina kahawa kilo sabini', L('unknown')),
 ('none', 'コーヒー50キロあります', L('unknown')),
]

if __name__ == '__main__':
    json.dump([{'expect': e, 'msg': m, 'label': l} for e, m, l in TESTS], open('test.json', 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(TESTS), 'tests', Counter(l['lang'] for _, _, l in TESTS))
