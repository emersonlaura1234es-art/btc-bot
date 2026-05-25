import requests
import time

TOKEN = "8901761801:AAFPj93E8z_uG4BBxCRP7HCjHLNhhPzP5jQ"

auto_id = None
tp_atual = None
sl_atual = None
alerta_ok = False
t_sinal = 0
t_alerta = 0
done = set()
off = None

def send(cid, txt):
    try:
        requests.post("https://api.telegram.org/bot"+TOKEN+"/sendMessage",
            json={"chat_id":cid,"text":txt},timeout=10)
    except:
        pass

def get_preco():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",timeout=10)
        data = r.json()
        return float(data["price"])
    except:
        return None

def gerar():
    global tp_atual, sl_atual, alerta_ok
    try:
        r = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=50",timeout=15)
        klines = r.json()
        ps = [float(k[4]) for k in klines]
        p = ps[-1]
        ds = [ps[i]-ps[i-1] for i in range(1,len(ps))]
        gains = [d for d in ds[-14:] if d>0]
        losses = [-d for d in ds[-14:] if d<0]
        g = sum(gains)/14 if gains else 0
        l = sum(losses)/14 if losses else 0.001
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
            tp_atual = round(p*1.02,2)
            sl_atual = round(p*0.99,2)
        elif v>=2:
            sig = "VENDA"
            tp_atual = round(p*0.98,2)
            sl_atual = round(p*1.01,2)
        else:
            sig = "NEUTRO"
            tp_atual = round(p*1.02,2)
            sl_atual = round(p*0.99,2)
        alerta_ok = False
        return "SINAL BTC\n"+sig+"\nPreco: "+str(round(p,2))+"\nTP: "+str(tp_atual)+"\nSL: "+str(sl_atual)+"\nRSI: "+str(round(rsi,1))
    except Exception as e:
        return "Erro: "+str(e)

def check_alerta(cid):
    global alerta_ok
    if not tp_atual or alerta_ok:
        return
    p = get_preco()
    if not p:
        return
    if p >= tp_atual:
        send(cid, "TAKE PROFIT! Preco: "+str(p)+" Meta: "+str(tp_atual))
        alerta_ok = True
    elif p <= sl_atual:
        send(cid, "STOP LOSS! Preco: "+str(p)+" Stop: "+str(sl_atual))
        alerta_ok = True

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
            elif txt == "/btc":
                send(cid, gerar())
            elif txt == "/auto":
                auto_id = cid
                send(cid,"Auto ativado! BTC a cada 5min")
        now = time.time()
        if auto_id and now-t_sinal>300:
            send(auto_id, gerar())
            t_sinal = now
        if auto_id and now-t_alerta>30:
            check_alerta(auto_id)
            t_alerta = now
    except Exception as e:
        print(e)
    time.sleep(2)
