"""Synthetic training data for Dure's on-device intent reader (phones and tablets).

The reader picks the topic of a farmer's off-script question; the reply itself is built from live market data.
Eight topics, the same ones Qwen picks from on computers:
  sell (now or wait) · why (price is low/high/flat) · forecast (next week) · buyers · weather/road · quality/grade · pool/auction · other
Questions are composed from hand-written templates and slot fillers in English, Tetum, Indonesian and Portuguese, with
the noise farmers' SMS really have (no punctuation, missing letters, mixed languages, greetings in front).
Writes train.jsonl (text, label). The hand-written test set (test.json) is never generated from these templates."""
import json, random, re
R = random.Random(7)

GREET = ['', '', '', '', 'bondia ', 'bondia! ', 'botarde ', 'hi ', 'hello ', 'halo ', 'selamat pagi ', 'bom dia ', 'maun ', 'mana ', 'pak ', 'excuse me ', 'dure, ', 'ok ', 'sorry ']
TAIL = ['', '', '', '?', '?', '??', ' ?', '...', ' pls', ' please', ' obrigada', ' obrigadu', ' thanks', ' ka lae?', ' bele?', ' ya?']
CROP_EN = ['coffee', 'my coffee', 'my beans', 'the coffee', 'my cherries', 'my harvest', 'my lot', 'my 40 kg']
CROP_TET = ['kafe', "hau-nia kafe", 'kafé', 'kafe fuan', 'hau nia kafe', 'kopi']
WHEN_EN = ['today', 'now', 'this week', 'right now', 'this morning']
WHEN_TET = ['ohin', 'agora', "semana ne'e", 'oras ne\'e', 'ohin dadeer']

T = {
 'sell': [
  'is it smarter to keep my beans a few more days', 'should i keep my beans', 'keep or sell', 'can i keep {c} until next week', 'is it better to store {c}', 'should i wait for a higher price', 'will i lose if i wait', 'what if i sell next week instead', 'rai kafe semana ida tan diak ka', 'hau hein semana oin bele ka', 'simpan dulu atau jual', 'guardar o café ou vender',
  'should i sell {c} {w} or wait', 'is {w} a good day to sell', 'is it a good time to sell {c}', 'sell {w} or next week',
  'is it smarter to keep {c} a few more days', 'should i hold {c} or sell it', 'better to sell {w} or wait for a better price',
  'do you think i should sell {w}', 'wait or sell', 'is now the right moment to sell {c}', 'would you sell {c} {w}',
  'is it worth waiting before i sell', 'can i get more if i wait', 'should i join the pool {w} or next week', 'is it wise to sell {w}',
  'hold or sell', 'should i put {c} in the pool {w}', 'is waiting a week better', 'what would you do sell or wait',
  'diak atu fa\'an {wt} ka lae', 'hau tenke fa\'an {wt} ka hein', 'fa\'an {wt} ka semana oin', 'hein uluk ka fa\'an agora',
  'diak liu fa\'an {wt} ka', 'hau fa\'an {ct} {wt} diak ka lae', 'hau rai {ct} loron balun tan diak ka', 'fa\'an ka hein',
  'ita hanoin hau fa\'an {wt}', 'oras ne\'e diak ba fa\'an ka', 'hau hein semana oin ka fa\'an ohin',
  'sebaiknya jual {wid} atau tunggu', 'apakah hari ini bagus untuk menjual', 'jual sekarang atau minggu depan', 'lebih baik tunggu atau jual',
  'devo vender hoje ou esperar', 'é bom vender agora', 'vender agora ou esperar', 'sell agora ka hein', 'fa\'an today or wait'],
 'why': [
  'how come prices went up', 'how come the price jumped', 'what pushed prices up', 'what pushed the price down', 'why did it go up so much', 'why are prices flat', 'what is behind the jump', 'what is behind the drop', 'why no change in price', 'porque o preço subiu', 'porque o preço caiu', 'saida mak halo folin sae', 'tansa folin la muda',
  'whats going on with the price', 'what is going on with prices {w}', 'why did grade a fall', 'why did grade c drop', 'why did the price for my grade go down', 'harga kenapa begitu', 'o que aconteceu com o preço', 'o preço do café',
  'why is the price so low {w}', 'why is the price high {w}', 'why did the price drop', 'why did prices go up', 'what is behind the price {w}',
  'prices jumped this week what is behind that', 'prices fell this week what is behind that', 'prices barely moved this week what is behind that',
  'how come the price is lower than last week', 'what made the price go down', 'why is grade a cheaper than last week', 'why so cheap {w}',
  'why is it the same price as last week', 'explain the price {w}', 'what changed in the price', 'reason for the low price',
  'how is the coffee market {w}', 'what is happening with the market', 'how is the market looking {w}', 'is the market good {w}',
  'tansa folin tun', 'tansa folin sae', 'tansa folin kafe a\'at {wt}', 'tansa folin hanesan semana kotuk', 'saida mak halo folin tun',
  'folin tun tanba saida', 'merkadu kafe oinsá {wt}', 'merkadu oinsá', 'oinsá folin {wt}', 'tansa folin la sae',
  'kenapa harga murah', 'kenapa harga turun minggu ini', 'kenapa harga naik', 'pasar kopi bagaimana minggu ini',
  'porque o preço caiu', 'porque o preço está baixo', 'como está o mercado'],
 'forecast': [
  'o preço vai baixar', 'o preço vai subir', 'will it go down next week', 'will prices keep rising', 'is the price going to fall', 'what will happen to prices', 'folin sei tun ka', 'harga akan naik', 'harga akan turun',
  'any forecast for {c}', 'price forecast', 'what is the forecast for prices', 'predict the price', 'prediksi harga', 'previsão do preço', 'folin previzaun',
  'will the price go up next week', 'what will the price be tomorrow', 'is the price going to rise', 'do you expect prices to go up',
  'price next week', 'will it be cheaper next week', 'will prices fall', 'how much next week', 'any idea about next week\'s price',
  'is the price going to be better later', 'prices in two weeks', 'will grade a be higher next week', 'what about next month',
  'folin sei sae semana oin', 'semana oin folin hira', 'aban folin hira', 'folin sei tun ka', 'semana oin folin sei diak liu ka',
  'folin fulan oin oinsá', 'harga minggu depan naik', 'besok harga berapa', 'o preço vai subir na próxima semana', 'preço semana que vem'],
 'buyers': [
  'how many traders are bidding', 'how many traders came', 'who is bidding', 'which trader pays more', 'is the exporter coming', 'why are there so few buyers this week', 'which of the buyers pays the most', 'quem compra', 'quantos compradores',
  'how many buyers are there', 'who is buying {w}', 'which exporters are in the market', 'are there many buyers {w}',
  'why are there so few buyers', 'which buyer pays the most', 'who are the buyers', 'is the roaster buying {w}', 'any new buyers',
  'which of the buyers pays best', 'how many exporters came', 'are buyers coming {w}', 'who will buy {c}',
  'sosa-na\'in hira mak iha', 'sosa-na\'in hira {wt}', 'see mak sosa', 'sosa-na\'in barak ka lae', 'exportador hira mai',
  'sosa-na\'in ida ne\'ebé selu boot liu', 'siapa pembelinya', 'berapa pembeli', 'quantos compradores', 'quem compra'],
 'weather': [
  'is it dry {w}', 'is it raining {w}', 'will it be dry tomorrow', 'is the sun out', 'can i dry my beans {w}', 'loron manas ohin ka', 'udan ka lae', 'cerah hari ini',
  'hujan tidak {wid}', 'cuaca hari ini', 'hujan besok', 'apakah jalan aman', 'chove hoje', 'o tempo hoje',
  'is it going to rain', 'is the road open', 'is the gleno road flooded', 'is rain coming this week', 'is the rain stopping',
  'is the road ok for the truck', 'can the truck get through', 'how is the weather {w}', 'is it raining in letefoho',
  'is the rain stopping before pickup', 'is the bridge ok', 'will the truck make it in this rain', 'any landslides on the road',
  'udan ka lae {wt}', 'dalan loke ka', 'dalan gleno taka ka', 'tempu oinsá {wt}', 'udan boot ka', 'udan sei para ka', 'dalan diak ka lae',
  'karreta bele liu ka', 'apakah hujan', 'jalan banjir', 'jalan terbuka', 'vai chover', 'a estrada está aberta'],
 'quality': [
  'how can i get a better grade', 'why did {c} get grade c', 'how do i avoid mouldy beans', 'how should i dry {c}',
  'what makes grade a', 'my beans are black what do i do', 'how to sort out bad beans', 'insects in {c} what to do',
  'how long should i dry the beans', 'what counts as a broken bean', 'how to keep {c} from going mouldy', 'tips for better quality',
  'is my coffee good enough for grade a', 'why was my photo graded b',
  'oinsá atu hetan grau a', 'oinsá atu halo kafe diak liu', 'tansa hau-nia kafe grau c', 'oinsá habai kafe', 'fuan metan oinsá',
  'kualidade diak liu oinsá', 'bagaimana kualitas kopi saya', 'cara mengeringkan kopi', 'como melhorar a qualidade', 'como secar o café'],
 'pool': [
  'berapa petani yang sudah ikut', 'berapa kopi terkumpul', 'o lote está cheio', 'quantos agricultores no lote', 'o leilão fecha quando',
  'how much coffee is in the pool', 'when does the auction close', 'when is the truck coming', 'is the pool full yet',
  'how many farmers joined', 'how many kg so far', 'when does bidding start', 'what time does the auction end', 'how does the pool work',
  'is the lot full', 'how much is missing to 2000 kg', 'when do the bids open', 'who joined the pool {w}',
  'pool iha kg hira ona', 'lelaun remata tuku hira', 'pool nakonu ona ka', 'agrikultór hira tama ona', 'lelaun hahú bainhira',
  'kafe kilu hira iha pool', 'lelang tutup jam berapa', 'berapa kg di pool', 'quando fecha o leilão', 'quantos kg no lote'],
 'other': [
  "what's up", 'whats up', 'bom dia, como vai', 'como vai', 'como está', 'hau moras', 'hau kolen', 'hau sente moras', 'my head hurts', 'good night', 'bonoite', 'hau iha uma', 'where is the church', 'sorry wrong number', 'test', 'hello?', 'are you there', 'ita iha ka',
  'hi there', 'hey', 'thanks so much', 'thank you very much', 'is it a holiday tomorrow', 'when is the holiday', 'i want to buy rice', 'i need fertilizer', 'where can i buy seeds', 'what day is it', 'my bus is late', 'can i call you', 'nice to meet you', 'see you', 'lol', 'loron feriadu', 'hau hakarak sosa fós', 'saya mau beli beras', 'quero comprar arroz', 'obrigado', 'até logo', 'adeus',
  'hello how are you', 'what is your name', 'who are you', 'thank you', 'thanks a lot', 'ok', 'good morning', 'can you help me with my phone',
  'my phone is broken', 'i love you', 'how old are you', 'tell me a joke', 'what is dure', 'are you a person', 'happy christmas',
  'my child is sick', 'where are you from', 'can you send me credit', 'who is the president', 'what time is it',
  'obrigadu', 'obrigada barak', 'ita naran saida', 'ita se', 'diak ka lae', 'hau la komprende', 'hau-nia telefone aat', 'ajuda hau',
  'terima kasih', 'siapa kamu', 'apa kabar', 'bom dia tudo bem', 'quem é você', 'feliz natal', 'hau hakarak sosa arroz', 'football tonight'],
}

# slot-built templates: more ways to ask the same thing (vocabulary, not sentences, from the dev misses)
BUYER = ['buyers', 'the roaster', 'the exporter', 'exporters', 'the cooperative', 'the café group', 'traders', 'companies', 'merchants', 'the trader from gleno', 'buyers from dili', 'people buying']
FUT = ['next week', 'tomorrow', 'later this month', 'after the rain', 'in two weeks', 'soon', 'next month']
EXTRA = {
 'sell': ['would selling {w} be a mistake', 'is this the week to let {c} go', 'better to sell before the rain', 'should i let {c} go {w}', 'do i lose money if i sell {w}', 'is {w} a bad time to sell',
          'should i take today\'s price', 'is it worth holding {c} until {f}', 'sell or keep {c} until {f}', 'vale a pena esperar', 'jual minggu ini rugi tidak', 'hau sei fa\'an ka lae'],
 'why': ['what drove prices up', 'what drove prices down', 'why so expensive {w}', 'why so cheap {w}', 'anything unusual in the market', 'what is special about the price {w}', 'why are prices different {w}',
         'what happened to the market {w}', 'why is grade a so high', 'porque o preço está alto', 'kenapa harga kopi tinggi', 'saida mak akontese ho folin'],
 'forecast': ['where are prices heading', 'where is the price going', '{f} higher or lower', 'will it be higher or lower {f}', 'do you expect a rise', 'do you expect a drop', 'what will prices do {f}',
              'price {f}', 'how much will coffee be {f}', 'is the price going up or down {f}', 'any prediction for {f}', 'o preço vai mudar {f}', 'minggu depan harga berapa', 'semana oin folin sei oinsá'],
 'buyers': ['is {b} in {w}', 'is {b} coming {w}', 'how many {b} want coffee', 'how many {b} came', 'did {b} come {w}', 'which {b} are here', 'are {b} bidding {w}', 'who wants my coffee',
            'how many companies want coffee', 'which buyers came from dili', 'ada berapa pembeli', 'quem vai comprar o meu café', "sosa-na'in sira husi ne'ebé"],
 'weather': ['any sun {f}', 'will it rain {f}', 'is it wet {w}', 'can trucks reach letefoho', 'is the bridge flooded', 'is the road muddy', 'will the road dry out {f}', 'tempu aban oinsá', 'apakah akan hujan', 'vai chover amanhã'],
 'quality': ['how do i stop mould', 'what makes grade a', 'are broken beans a problem', 'do black beans lower the grade', 'how long should i dry {c}', 'how do i sort {c}', 'oinsá habai kafe di\'ak', 'cara jemur kopi', 'como melhorar a qualidade'],
 'pool': ['how full is the lot', 'how many farmers joined', 'how many farms are in', 'what time does bidding end', 'when does the auction end', 'is the lot big enough', 'pool kompletu ona ka', 'berapa kg sudah terkumpul', 'quando fecha o leilão'],
 'other': ['good morning dure', 'good afternoon', 'good evening', 'selamat siang', 'selamat sore', 'selamat malam', 'boa tarde', 'boa noite', 'botarde dure', 'who made you', 'who built you',
           'hau hakarak koalia ho ema', 'can i talk to a person', 'pode me ajudar com o telefone', 'my cow is sick', 'my pig is sick', 'where is the clinic', 'school fees', 'how is your day', 'what is the news', 'happy easter'],
}
for k, v in EXTRA.items(): T[k] = T[k] + v

def fill(t):
    return (t.replace('{c}', R.choice(CROP_EN)).replace('{w}', R.choice(WHEN_EN)).replace('{ct}', R.choice(CROP_TET))
             .replace('{wt}', R.choice(WHEN_TET)).replace('{wid}', R.choice(['hari ini', 'sekarang', 'minggu ini'])).replace('{b}', R.choice(BUYER)).replace('{f}', R.choice(FUT)))

def noise(s):
    r = R.random()
    if r < .12:   # drop a vowel
        i = [k for k, ch in enumerate(s) if ch in 'aeiou']
        if i: k = R.choice(i); s = s[:k] + s[k+1:]
    elif r < .2:   # swap two letters
        k = R.randrange(1, max(2, len(s) - 1)); s = s[:k-1] + s[k] + s[k-1] + s[k+1:]
    elif r < .26:  # double a letter
        k = R.randrange(len(s)); s = s[:k] + s[k] + s[k:]
    if R.random() < .3: s = s.replace("'", '')
    if R.random() < .15: s = s.replace(' i ', ' I ')
    if R.random() < .2: s = s.upper() if R.random() < .2 else s.capitalize()
    return s

def make(per=560):
    out = []
    for lab, ts in T.items():
        seen = set()
        tries = 0
        while len(seen) < per and tries < per * 30:
            tries += 1
            s = noise((R.choice(GREET) + fill(R.choice(ts)) + R.choice(TAIL)).strip())
            if s not in seen: seen.add(s); out.append({'text': s, 'label': lab})
    R.shuffle(out)
    return out

if __name__ == '__main__':
    d = make()
    with open('train.jsonl', 'w', encoding='utf-8') as f:
        for x in d: f.write(json.dumps(x, ensure_ascii=False) + '\n')
    from collections import Counter
    print(len(d), Counter(x['label'] for x in d))
