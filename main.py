import requests
import pandas as pd
import numpy as np
import time

TOKEN = "8901761801:AAEmwHD2hwZI0g6NR-picR-Gm0p5i151zOw"
CHAT_ID = None

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

def get_btc_prices():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100"
    r = requests.get(url)
    closes = [float(k[4]) for k in r.json()]
    return closes

def calc_rsi(prices, period=14):
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_macd(prices):
    prices = pd.Series(prices)
    ema12 = prices.ewm(span=12).mean()
    ema26 = prices.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd.iloc[-1], signal.iloc[-1]

def gerar_sinal():
    prices = get_btc_prices()
    rsi = calc_rsi(prices)
    macd, signal = calc_macd(prices)
    preco = prices[-1]
    pontos_compra = 0
    pontos_venda = 0
    if rsi < 35: pontos_compra += 2
    elif rsi < 45: pontos_compra += 1
    if rsi > 65: pontos_venda += 2
    elif rsi > 55: pontos_venda += 1
    if macd > signal: pontos_compra += 2
    else: pontos_venda += 2
    ma20 = np.mean(prices[-20:])
    ma50 = np.mean(prices[-50:])
    if ma20 > ma50: pontos_compra += 1
    else: pontos_venda += 1
    if pontos_compra >= 4:
        sinal = "🟢 *COMPRA*"
        forca = "FORTE" if pontos_compra >= 5 else "MODERADA"
    elif pontos_venda >= 4:
        sinal = "🔴 *VENDA*"
        forca = "FORTE" if pontos_venda >= 5 else "MODERADA"
    else:
        sinal = "⚪ *NEUTRO*"
        forca = "AGUARDAR"
    msg = f"📊 *SINAL BTC/USDT*\n━━━━━━━━━━━━━━\n{sinal} — {forca}\n━━━━━━━━━━━━━━\n💰 Preço: ${preco:,.2f}\n📈 RSI: {rsi:.1f}\n📉 MACD: {'Alta' if macd > signal else 'Baixa'}\n📊 Tendência: {'Alta' if ma20 > ma50 else 'Baixa'}\n━━━━━━━━━━━━━━\n⚠️ _Use como apoio, não como garantia._"
    return msg

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 10, "offset": offset}
    try:
        r = requests.get(url, params=params, timeout=15)
        return r.json().get("result", [])
    except:
        return []

print("Bot iniciado...")
offset = None
last_signal_time = 0
auto_chat_id = None
processed = set()

while True:
    updates = get_updates(offset)
    for update in updates:
        uid = update["update_id"]
        if uid in processed:
            offset = uid + 1
            continue
        processed.add(uid)
        offset = uid + 1
        msg = update.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")
        if text == "/start":
            send_message(chat_id, "👋 Olá! Bot de sinais BTC ativo!\n\nComandos:\n/sinal — Ver sinal agora\n/auto — Sinais automáticos a cada hora")
        elif text == "/sinal":
            send_message(chat_id, "🔍 Analisando mercado...")
            send_message(chat_id, gerar_sinal())
        elif text == "/auto":
            send_message(chat_id, "✅ Sinais automáticos ativados!")
            auto_chat_id = chat_id
    if auto_chat_id and (time.time() - last_signal_time) > 3600:
        send_message(auto_chat_id, gerar_sinal())
        last_signal_time = time.time()
    time.sleep(2)
