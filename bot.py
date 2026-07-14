import requests
import yfinance as yf
from datetime import datetime

# ==========================
# TELEGRAM SETTINGS
# ==========================
BOT_TOKEN = "8635826832:AAG6UZ6nNq9unKmT-yf7J-lu2lHiWoI7PAE"
CHAT_ID = "7282928970"

# ==========================
# MARKET DATA
# ==========================
symbol = "^NSEI"

data = yf.Ticker(symbol)
hist = data.history(period="5d", interval="5m")

if len(hist) < 30:
    exit()

# ==========================
# MARKET HOURS
# ==========================
now = datetime.now()

if now.weekday() >= 5:
    print("Market Closed")
    exit()


# ==========================
# VWAP
# ==========================
hist["TP"] = (hist["High"] + hist["Low"] + hist["Close"]) / 3
hist["VWAP"] = (
    (hist["TP"] * hist["Volume"]).cumsum()
    / hist["Volume"].cumsum()
)

# ==========================
# EMA
# ==========================
hist["EMA9"] = hist["Close"].ewm(span=9, adjust=False).mean()
hist["EMA21"] = hist["Close"].ewm(span=21, adjust=False).mean()

# ==========================
# RSI
# ==========================
delta = hist["Close"].diff()

gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

hist["RSI"] = 100 - (100 / (1 + rs))
# ==========================
# MACD
# ==========================
hist["EMA12"] = hist["Close"].ewm(span=12, adjust=False).mean()
hist["EMA26"] = hist["Close"].ewm(span=26, adjust=False).mean()

hist["MACD"] = hist["EMA12"] - hist["EMA26"]
hist["Signal_Line"] = hist["MACD"].ewm(span=9, adjust=False).mean()

# ==========================
# LATEST VALUES
# ==========================
price = round(hist["Close"].iloc[-1], 2)

ema9 = hist["EMA9"].iloc[-1]
ema21 = hist["EMA21"].iloc[-1]

rsi = hist["RSI"].iloc[-1]
vwap = hist["VWAP"].iloc[-1]

macd = hist["MACD"].iloc[-1]
signal_line = hist["Signal_Line"].iloc[-1]
volume = hist["Volume"].iloc[-1]
avg_volume = hist["Volume"].rolling(20).mean().iloc[-1]
# ==========================
# SIGNAL LOGIC
# ==========================
if ema9 > ema21 and rsi > 55 and price > vwap and macd > signal_line and volume > avg_volume:
    signal = "🟢 BUY CE"
    target1 = round(price + 50, 2)
    target2 = round(price + 100, 2)
    stoploss = round(price - 50, 2)

elif ema9 < ema21 and rsi < 45 and price < vwap and macd < signal_line and volume > avg_volume:
    signal = "🔴 BUY PE"
    target1 = round(price - 50, 2)
    target2 = round(price - 100, 2)
    stoploss = round(price + 50, 2)

else:
    signal = "⚪ NO TRADE"
    target1 = "-"
    target2 = "-"
    stoploss = "-"

# ==========================
# OPTION STRIKE
# ==========================
strike = round(price / 50) * 50

if signal == "🟢 BUY CE":
    option = f"{strike} CE"
elif signal == "🔴 BUY PE":
    option = f"{strike} PE"
else:
    option = "-"

# ==========================
# TELEGRAM MESSAGE
# ==========================
message = f"""
📊 NIFTY SIGNAL

💰 Spot Price: {price:.2f}

📢 Signal: {signal}

🎯 Option: {option}

🎯 Target 1: {target1}
🎯 Target 2: {target2}
🛑 Stop Loss: {stoploss}

📈 EMA9 : {ema9:.2f}
📉 EMA21: {ema21:.2f}
📊 RSI  : {rsi:.2f}
📊 Volume: {int(volume)}
📍 VWAP : {vwap:.2f}
📈 MACD : {macd:.2f}

🕒 {datetime.now().strftime('%d-%m-%Y %I:%M %p')}
"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.text)