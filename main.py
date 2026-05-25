import requests
import time

TOKEN = "8901761801:AAEmwHD2hwZI0g6NR-picR-Gm0p5i151zOw"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def gerar_sinal():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=2&interval=hourly"
        r = requests.get(url, timeout=10)
        prices = [p[1] for p in r.json()["prices"]]
        preco = prices[-1]

        # RSI simples
        deltas = [prices[i]-prices[i-1] for i in range(1, len(prices))]
        gains = [d for d in deltas[-14:] if d > 0]
        losses = [-d for d in deltas[-14:] if d < 0]
        avg_g = sum(gains)/14 if gains else 0
        avg_l = sum(losses)/14 if losses else 0.001
        rsi = 100 - (100/(1+(avg_g/avg_l)))

        # Médias móveis
        ma7 = sum(prices[-7:])/7
        ma20 = sum(prices[-20:])/20

        # Sinal
        compra = 0
        venda = 0
        if rsi < 40: compra += 2
        elif rsi < 50: compra += 1
        if rsi > 60: venda += 2
        elif rsi > 50: venda += 1
        if ma7 > ma20: compra += 2
        else: venda += 2

        if compra >= 3:
            sinal = "🟢 *COMPRA*"
            forca = "FORTE" if compra >= 4 else "MODERADA"
        elif venda >= 3:
            sinal = "🔴 *VENDA*"
            forca = "FORTE" if venda >= 4 else "MODERADA"
        else:
            sinal = "⚪ *NEUTRO*"
            forca = "AGUARDAR"

        return f"📊 *SINAL BTC/USDT*\n━━━━━━━━━━━━━━\n{sinal} — {forca}\n━━━━━━━━━━━━━━\n💰 Preço: ${preco:,.2f}\n📈 RSI: {rsi:.1f}\n📊 MA7 vs MA20: {'Alta' if ma7 > ma20 else 'Baixa'}\n━━━━━━━━━━━━━━\n⚠️ _Use como apoio, não como garantia._"
    except Exception as e:
        return f"❌ Erro ao buscar dados: {str(e)}"

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        r = requests.get(url, params={"timeout": 10, "offset": offset}, timeout=15)
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
            send_message(chat_id, gerar_sinal())
        elif text == "/auto":
            send_message(chat_id, "✅ Sinais automáticos ativados!")
            auto_chat_id = chat_id
    if auto_chat_id and (time.time() - last_signal_time) > 300:
        send_message(auto_chat_id, gerar_sinal())
        last_signal_time = time.time()
    time.sleep(2)
