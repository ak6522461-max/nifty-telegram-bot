import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

BOT_TOKEN ="8635826832:AAG6UZ6nNq9unKmT-yf7J-lu2lHiWoI7PAE"
CHAT_ID = "7282928970"

symbol = "^NSEI"

data = yf.Ticker(symbol)
hist = data.history(period="5d", interval="5m")

if len(hist) < 30:
    exit()

now = datetime.now()

# Market Hours
if now.weekday() >= 5:
    exit()

if not ((now.hour > 9 or (now.hour == 9 and now.minute >= 15)) and
        (now.hour < 15 or (now.hour == 15 and now.minute <= 30))):
    exit()

# EMA
hist["EMA9"] = hist["Close"].ewm(span=9, adjust=False).mean()
hist["EMA21"] = hist["Close"].ewm(span=21, adjust=False).mean()

# RSI
delta = hist["Close"].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss
hist["RSI"] = 100 - (100 / (1 + rs))
price = round(hist["Close"].iloc[-1], 2)
ema9 = hist["EMA9"].iloc[-1]
ema21 = hist["EMA21"].iloc[-1]
rsi = hist["RSI"].iloc[-1]

if ema9 > ema21 and rsi > 55:
    signal = "🟢 BUY CE"
    target1 = round(price + 50, 2)
    target2 = round(price + 100, 2)
    stoploss = round(price - 50, 2)

elif ema9 < ema21 and rsi < 45:
    signal = "🔴 BUY PE"
    target1 = round(price - 50, 2)
    target2 = round(price - 100, 2)
    stoploss = round(price + 50, 2)

else:
    signal = "⚪ NO TRADE"
    target1 = "-"
    target2 = "-"
    stoploss = "-"

message = f"""
📊 NIFTY SIGNAL

Price: {price}

Signal: {signal}

🎯 Target 1: {target1}
🎯 Target 2: {target2}
🛑 Stop Loss: {stoploss}
"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": message
})

print(response.text)