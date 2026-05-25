import requests
import time

TOKEN = "8901761801:AAFPj93E8z_uG4BBxCRP7HCjHLNhhPzP5jQ"

auto_id = None
alertas = {}
t_sinal = 0
t_alerta = 0
done = set()
off = None

MOEDAS = {
    "/btc": "BTCUSDT"
}

def send(cid, txt):
    try:
        requests.post("https://api.telegram.org/bot"+TOKEN+"/sendMessage",
            json={"chat_id":cid,"text":txt},timeout=10)
    except:
        pass

def get_preco(symbol):
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol="+symbol,timeout=10)
        return float(r.json()["price"])
    except:
        return None

def gerar(symbol, nome):
    try:
        r = requests.get("https://api.binance.com/api/v3/klines?symbol="+symbol+"&interval=1h&limit=50",timeout=15)
        ps = [float(x[4]) for x in r.json()]
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
        alertas[symbol] = {"tp":tp,"sl":sl,"ok":False}
        return "SINAL "+nome+"\n"+sig+"\nPreco: "+str(round(p,2))+"\nTP: "+str(tp)+"\nSL: "+str(sl)+"\nRSI: "+str(round(rsi,1))
    except Exception as e:
        return "Erro "+nome+": "+str(e)

def check_alertas(cid):
    for symbol, data in alertas.items():
        if data["ok"]:
            continue
        p = get_preco(symbol)
        if not p:
            continue
        if p >= data["tp"]:
            send(cid, "TAKE PROFIT "+symbol+"! Preco: "+str(p)+" Meta: "+str(data["tp"]))
            alertas[symbol]["ok"] = True
        elif p <= data["sl"]:
            send(cid, "STOP LOSS "+symbol+"! Preco: "+str(p)+" Stop: "+str(data["sl"]))
            alertas[symbol]["ok"] = True

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
                send(cid,"Bot BTC\n/btc - Sinal agora\n/auto - Automatico 5min")
            elif txt in MOEDAS:
                send(cid, gerar(MOEDAS[txt], txt[1:].upper()))
            elif txt == "/auto":
                auto_id = cid
                send(cid,"Auto ativado! BTC a cada 5min")
        now = time.time()
        if auto_id and now-t_sinal>300:
            for cmd, symbol in MOEDAS.items():
                send(auto_id, gerar(symbol, cmd[1:].upper()))
            t_sinal = now
        if auto_id and now-t_alerta>30:
            check_alertas(auto_id)
            t_alerta = now
    except Exception as e:
        print(e)
    time.sleep(2)
