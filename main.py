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
        url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
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
            return "Dados insuficientes"
        preco = prices[-1]
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d for d in deltas[-14:] if d > 0]
        losses = [-d for d in deltas[-14:] if d < 0]
        avg_g = sum(gains) / 14 if gains else 0
        avg_l = sum(losses) / 14 if losses else 0.001
        rs = avg_g / avg_l
        rsi = 100 - (100 / (1 + rs))
        ma7 = sum(prices[-7:]) / 7
        ma20 = sum(prices[-20:]) / 20
        compra = 0
        venda = 0
        if rsi < 40:
            compra += 2
        elif rsi < 50:
            compra += 1
        if rsi > 60:
            venda += 2
        elif rsi > 50:
            venda += 1
        if ma7 > ma20:
            compra += 2
        else:
            venda += 2
        if compra >= 3:
            sinal = "COMPRA"
            emoji = "🟢"
            forca = "FORTE" if compra >= 4 else "MODERADA"
            tp = round(preco * 1.02, 2)
            sl = round(preco * 0.99, 2)
        elif venda >= 3:
            sinal = "VENDA"
            emoji = "🔴"
            forca = "FORTE" if venda >= 4 else "MODERADA"
            tp = round(preco * 0.98, 2)
            sl = round(preco * 1.01, 2)
        else:
            sinal = "NEUTRO"
            emoji = "⚪"
            forca = "AGUARDAR"
            tp = round(preco * 1.02, 2)
            sl = round(preco * 0.99, 2)
        ultimo_tp = tp
        ultimo_sl = sl
        alerta_enviado = False
        tendencia = "Alta" if ma7 > ma20 else "Baixa"
        msg = "📊 *SINAL BTC/USDT*\n"
        msg += "━━━━━━━━━━━━━━\n"
        msg += emoji + " *" + sinal + "* — " + forca + "\n"
        msg += "━━━━━━━━━━━━━━\n"
        msg += "💰 Preco: $" + str(round(preco, 2)) + "\n"
        msg += "🎯 Take Profit: $" + str(tp) + "\n"
        msg += "🛑 Stop Loss: $" + str(sl) + "\n"
        msg += "📈 RSI: " + str(round(rsi, 1)) + "\n"
        msg += "📊 Tendencia: " + tendencia + "\n"
        msg += "━━━━━━━━━━━━━━\n"
        msg += "⚠️ _Use como apoio, nao como garantia._"
        return msg
    except Exception as e:
        return "Erro: " + str(e)

def
