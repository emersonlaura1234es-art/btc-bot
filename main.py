import requests
import time

TOKEN = "8901761801:AAEmwHD2hwZI0g6NR-picR-Gm0p5i151zOw"

auto_chat_id = None
ultimo_tp = None
ultimo_sl = None
alerta_enviado = False
last_signal_time = 0
last_alerta_time = 0
processed = set()
offset = None

def send_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def get_preco():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        return float(r.json()["bitcoin"]["usd"])
    except:
        return None

def gerar_sinal():
    global ultimo_tp, ultimo_sl, alerta_enviado
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1&interval=hourly"
        r = requests.get(url, timeout=15)
        data = r.json()
        prices = [float(p[1]) for p in data["prices"]]
        if len(prices) < 20:
            return "❌ Dados insuficientes"
        preco = prices[-1]
        deltas = [prices[i]-prices[i-1] for i in range(1, len(prices))]
        gains = [d for d in deltas[-14:] if d > 0]
        losses = [-d for d in deltas[-14:] if d < 0]
        avg_g = sum(gains)/14 if gains else 0
        avg_l = sum(losses)/14 if losses else 0.001
        rsi = 100 - (100/(1+(avg_g/
