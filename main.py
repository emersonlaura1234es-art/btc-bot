import requests
import time

TOKEN = "8901761801:AAEmwHD2hwZI0g6NR-picR-Gm0p5i151zOw"

auto_id = None
tp = None
sl = None
alerta = False
t_sinal = 0
t_alerta = 0
done = set()
off = None

def send(cid, txt):
    try:
        requests.post("https://api.telegram.org/bot"+TOKEN+"/sendMessage",
            json={"chat_id":cid,"text":txt,"parse_mode":"Markdown"},timeout=10)
    except:
        pass

def preco_btc():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",timeout=10)
        return float(r.json()["bitcoin"]["usd"])
    except:
        return None

def sinal():
    global tp, sl, alerta
    try:
        r = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1&interval=hourly",timeout=15)
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
        if c>=3:
            sig = "COMPRA"
            em = "green"
            tp = round(p*1.02,2)
            sl = round(p*0.99,2)
        elif v>=3:
            sig = "VENDA"
            em = "red"
            tp = round(p*0.98,2)
            sl = round(p*1.01,2)
        else:
            sig = "NEUTRO"
            em = "white"
            tp = round(p*1.02,2)
            sl = round(p*0.99,2)
        alerta = False
        txt = "SINAL BTC\n"+sig+"\nPreco: "+str(round(p,2))+"\nTP: "+str(tp)+"\nSL: "+str(sl)+"\nRSI: "+str(round(rsi,1))
        return txt
    except Exception as e:
        return "Erro: "+str(e)

def check(cid):
    global alerta
    if not tp or alerta:
        return
    p = preco_btc()
    if not p:
        return
    if p>=tp:
        send(cid,"TAKE PROFIT! Preco: "+str(p)+" Meta: "+str(tp))
        alerta = True
    elif p<=sl:
        send(cid,"STOP LOSS! Preco: "+str(p)+" Stop: "+str(sl))
        alerta = True

def updates():
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
        for u in updates():
            uid = u["update_id"]
            if uid in done:
                off = uid+1
                continue
            done.add(uid)
            off = uid+1
            m = u.get("message",{})
            cid = m.get("chat",{}).get("id")
            txt = m.get("text","")
            if txt=="/start":
                send(cid,"Bot BTC\n/sinal\n/auto")
            elif txt=="/sinal":
                send(cid,sinal())
            elif txt=="/auto":
                auto_id = cid
                send(cid,"Auto ativado 5min")
        now = time.time()
        if auto_id and now-t_sinal>300:
            send(auto_id,sinal())
            t_sinal = now
        if auto_id and now-t_alerta>30:
            check(auto_id)
            t_alerta = now
    except Exception as e:
        print(e)
    time.sleep(2)               
