import requests
import time

TOKEN = "8901761801:AAEmwHD2hwZI0g6NR-picR-Gm0p5i151zOw"

auto_id = None
alertas = {}
t_sinal = 0
t_alerta = 0
done = set()
off = None

MOEDAS = {
    "/btc": "bitcoin",
    "/eth": "ethereum",
    "/sol": "solana",
    "/bnb": "binancecoin",
    "/xrp": "ripple",
    "/ada": "cardano"
}

def send(cid, txt):
    try:
        requests.post("https://api.telegram.org/bot"+TOKEN+"/sendMessage",
            json={"chat_id":cid,"text":txt},timeout=10)
    except:
        pass

def get_preco(coin):
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids="+coin+"&vs_currencies=usd",timeout=10)
        return float(r.json()[coin]["usd"])
    except:
        return None

def gerar(coin, nome):
    try:
        r = requests.get("https://api.coingecko.com/api/v3/coins/"+coin+"/market_chart?vs_currency=usd&days=1&interval=hourly",timeout=15)
        ps = [float(x[1]) for x in r.json()["prices"]]
        p = ps[-1]
        ds = [ps[i]-ps[i-1] for i in range(1,len(ps))]
        g = sum([d for d in ds[-14:] if d>0])/14
        l = sum([-d for d in ds[-14:] if d<0])/14 or 0.001
        rsi = 100-(100/(1+(g/l)))
        m7 = sum(ps[-7:])/7
        m20 = sum(ps[-20:])/20
        c = 0
        v = 0
        if rsi<40: c+=2
        elif rsi<50: c+=1
        if rsi>60: v+=2
        elif rsi>50: v+=1
        if m7>m20: c+=2
        else: v+=2
        if c>=2:
            sig = "COMPRA"
            tp = round(p*1.02,2)
            sl = round(p*0.99,2)
        elif v>=2:
            sig = "VENDA"
            tp = round(p*0.98,2)
            sl = round(p*1.01,2)
        else:
            sig = "NEUTRO"
            tp = round(p*1.02,2)
            sl = round(p*0.99,2)
        alertas[coin] = {"tp":tp,"sl":sl,"ok":False}
        return "SINAL "+nome.upper()+"\n"+sig+"\nPreco: "+str(round(p,2))+"\nTP: "+str(tp)+"\nSL: "+str(sl)+"\nRSI: "+str(round(rsi,1))
    except Exception as e:
        return "Erro "+nome+": "+str(e)

def check_alertas(cid):
    for coin, data in alertas.items():
        if data["ok"]:
            continue
        p = get_preco(coin)
        if not p:
            continue
        if p >= data["tp"]:
            send(cid, "TAKE PROFIT "+coin.upper()+"! Preco: "+str(p)+" Meta: "+str(data["tp"]))
            alertas[coin]["ok"] = True
        elif p <= data["sl"]:
            send(cid, "STOP LOSS "+coin.upper()+"! Preco: "+str(p)+" Stop: "+str(data["sl"]))
            alertas[coin]["ok"] = True

def get_updates():
    global off
    try:
        r = requests.get("https://api.telegram.org/bot"+TOKEN+"/getUpdates",
            params={"timeout":10,"offset":off},timeout=15)
        return r.json().get("result",[])
    except:
        return []

print("ok")
while True:
    try:
        for u in get_updates():
            uid = u["update_id"]
            if uid in done:
                off = uid+1
                continue
            done.add(uid)
            off = uid+1
            m = u.get("message",{})
            cid = m.get("chat",{}).get("id")
            txt = m.get("text","")
            if txt == "/start":
                send(cid,"Bot de Sinais!\n/btc /eth /sol /bnb /xrp /ada\n/auto - Todos automatico 5min")
            elif txt in MOEDAS:
                send(cid, gerar(MOEDAS[txt], txt[1:]))
            elif txt == "/auto":
                auto_id = cid
                send(cid,"Auto ativado! Todas moedas a cada 5min")
        now = time.time()
        if auto_id and now-t_sinal>300:
            for cmd, coin in MOEDAS.items():
                send(auto_id, gerar(coin, cmd[1:]))
                time.sleep(1)
            t_sinal = now
        if auto_id and now-t_alerta>30:
            check_alertas(auto_id)
            t_alerta = now
    except Exception as e:
        print(e)
    time.sleep(3)
