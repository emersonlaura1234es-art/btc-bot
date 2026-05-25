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
        elif rsi>50
