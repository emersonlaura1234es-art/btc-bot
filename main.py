import requests
import time

TOKEN = "8901761801:AAEmwHD2hwZI0g6NR-picR-Gm0p5i151zOw"

ultimo_tp = None
ultimo_sl = None
ultimo_sinal = None
alerta_enviado = False

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def get_preco():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        return r.json()["bitcoin"]["usd"]
    except:
        return None

def gerar_sinal():
    global ultimo_tp, ultimo_sl, ultimo_sinal, alerta_enviado
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=2&interval=hourly"
        r = requests.get(url, timeout=10)
        prices = [p[1] for p in r.json()["prices"]]
        preco = prices[-1]

        deltas = [prices[i]-prices[i-1] for i in range(1, len(prices))]
        gains = [d for d in deltas[-14:] if d > 0]
        losses = [-d for d in deltas[-14:] if d < 0]
        avg_g = sum(gains)/14 if gains else 0
        avg_l = sum(losses)/14 if losses else 0.001
        rsi = 100 - (100/(1+(avg_g/avg_l)))

        ma7 = sum(prices[-7:])/7
        ma20 = sum(prices[-20:])/20

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
            tp = preco * 1.02
            sl = preco * 0.99
        elif venda >= 3:
            sinal = "🔴 *VENDA*"
            forca = "FORTE" if venda >= 4 else "MODERADA"
            tp = preco * 0.98
            sl = preco * 1.01
        else:
            sinal = "⚪ *NEUTRO*"
            forca = "AGUARDAR"
            tp = preco * 1.02
            sl = preco * 0.99

        ultimo_tp = tp
        ultimo_sl = sl
        ultimo_sinal = sinal
        alerta_enviado = False

        return f"📊 *SINAL BTC/USDT*\n━━━━━━━━━━━━━━\n{sinal} — {forca}\n━━━━━━━━━━━━━━\n💰 Preço: ${preco:,.2f}\n🎯 Take Profit: ${tp:,.2f}\n🛑 Stop Loss: ${sl:,.2f}\n📈 RSI: {rsi:.1f}\n📊 Tendência: {'Alta' if ma7 > ma20 else 'Baixa'}\n━━━━━━━━━━━━━━\n⚠️ _Use como apoio, não como garantia._"
    except Exception as e:
        return f"❌ Erro ao buscar dados: {str(e)}"

def checar_alertas(chat_id):
    global alerta_enviado
    if not ultimo_tp or not ultimo_sl or alerta_enviado:
        return
    preco = get_preco()
    if not preco:
        return
    if preco >= ultimo_tp:
        send_message(chat_id, f"🎯 *TAKE PROFIT ATINGIDO!*\n\n✅ Preço chegou em ${preco:,.2f}\n🎯 Meta era ${ultimo_tp:,.2f}\n\n💰 *Hora de realizar o lucro!*")
        alerta_enviado = True
    elif preco <= ultimo_sl:
        send_message(chat_id, f"🛑 *STOP LOSS ATINGIDO!*\n\n❌ Preço caiu para ${preco:,.2f}\n🛑 Stop era ${ultimo_sl:,.2f}\n\n⚠️ *Considere sair da posição!*")
        alerta_enviado = True

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
last_alerta_time = 0
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
            send_message(chat_id, "👋 Olá! Bot de sinais BTC ativo!\n\nComandos:\n/sinal — Ver sinal agora\n/auto — Sinais automáticos a cada 5 minutos")
        elif text == "/sinal":
            send_message(chat_id, gerar_sinal())
        elif text == "/auto":
            send_message(chat_id, "✅ Sinais automáticos ativados! A cada 5 minutos.")
            auto_chat_id = chat_id

    if auto_chat_id and (time.time() - last_signal_time) > 300:
        send_message(auto_chat_id, gerar_sinal())
        last_signal_time = time.time()
or
    if auto_chat_id and (time.time() - last_alerta_time) > 30:
        checar_alertas(auto_chat_id)
        last_alerta_time = time.time()

    time.sleep(2)
