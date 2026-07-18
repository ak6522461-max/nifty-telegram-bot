import requests
import os
import pandas as pd
import yfinance as yf
from datetime import datetime

# ==========================
# TELEGRAM SETTINGS
# ==========================
BOT_TOKEN ="8635826832:AAG6UZ6nNq9unKmT-yf7J-lu2lHiWoI7PAE"
CHAT_ID = "7282928970"
LAST_SIGNAL_FILE = "last_signal.txt"

# ==========================
# MARKET DATA
# ==========================
symbol = "^NSEI"

data = yf.Ticker(symbol)
hist = data.history(period="5d", interval="5m")

if len(hist) < 30:
    print("Not enough data")
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

if hist["Volume"].sum() > 0:
    hist["VWAP"] = (
        (hist["TP"] * hist["Volume"]).cumsum()
        / hist["Volume"].cumsum()
    )
else:
    hist["VWAP"] = hist["Close"]

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
# ADX
# ==========================
plus_dm = hist["High"].diff()
minus_dm = -hist["Low"].diff()

plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

tr = pd.concat([
    hist["High"] - hist["Low"],
    (hist["High"] - hist["Close"].shift()).abs(),
    (hist["Low"] - hist["Close"].shift()).abs()
], axis=1).max(axis=1)

atr = tr.rolling(14).mean()

plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
minus_di = 100 * (minus_dm.rolling(14).mean() / atr)

dx = ((plus_di - minus_di).abs() / (plus_di + minus_di)) * 100
hist["ADX"] = dx.rolling(14).mean()

# ==========================
# ATR
# ==========================
hist["TR"] = tr
hist["ATR"] = atr
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

adx = hist["ADX"].iloc[-1]
atr = hist["ATR"].iloc[-1]

volume = hist["Volume"].iloc[-1]
avg_volume = hist["Volume"].rolling(20).mean().iloc[-1]

# ==========================
# CONFIDENCE SCORE
# ==========================
confidence = 50

if ema9 > ema21:
    confidence += 10

if rsi > 60:
    confidence += 10

if price > vwap:
    confidence += 10

if macd > signal_line:
    confidence += 10

if adx > 20:
    confidence += 10

# ==========================
# SIGNAL LOGIC
# ==========================
if (
    ema9 > ema21
    and rsi > 60
    and price > vwap
    and macd > signal_line
    and adx > 20
):
    signal = "🟢 BUY CE"
    target1 = round(price + atr, 2)
    target2 = round(price + atr * 2, 2)
    stoploss = round(price - atr, 2)

elif (
    ema9 < ema21
    and rsi < 40
    and price < vwap
    and macd < signal_line
    and adx > 20
):
    signal = "🔴 BUY PE"
    target1 = round(price - atr, 2)
    target2 = round(price - atr * 2, 2)
    stoploss = round(price + atr, 2)

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
# DUPLICATE SIGNAL CHECK
# ==========================
last_signal = ""

if os.path.exists(LAST_SIGNAL_FILE):
    with open(LAST_SIGNAL_FILE, "r") as f:
        last_signal = f.read().strip()

if signal == last_signal:
    print("Duplicate Signal - Not Sending")
    exit()

if signal != "⚪ NO TRADE":
    with open(LAST_SIGNAL_FILE, "w") as f:
        f.write(signal)
        # ==========================
# TELEGRAM MESSAGE
# ==========================
message = f"""
📊 NIFTY SIGNAL

💰 Spot Price: {price:.2f}

📢 Signal: {signal}
🔥 Confidence: {confidence}%

🎯 Option: {option}

🎯 Target 1: {target1}
🎯 Target 2: {target2}
🛑 Stop Loss: {stoploss}

📈 EMA9 : {ema9:.2f}
📉 EMA21: {ema21:.2f}
📊 RSI  : {rsi:.2f}
📍 VWAP : {vwap:.2f}
📈 MACD : {macd:.2f}
📈 ADX  : {adx:.2f}
📊 ATR  : {atr:.2f}
📊 Volume: {int(volume)}

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