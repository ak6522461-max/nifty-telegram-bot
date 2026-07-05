import requests
import yfinance as yf

BOT_TOKEN = "8635826832:AAG6UZ6nNq9unKmT-yf7J-lu2lHiWoI7PAE"
CHAT_ID = "7282928970"

symbol = "^NSEI"

data = yf.Ticker(symbol)
hist = data.history(period="2d", interval="5m")

if len(hist) > 20:
    close = hist["Close"]

    ema9 = close.ewm(span=9).mean()
    ema21 = close.ewm(span=21).mean()

    price = round(close.iloc[-1], 2)

    if ema9.iloc[-1] > ema21.iloc[-1]:
        signal = "🟢 BUY"
        target1 = round(price + 50, 2)
        target2 = round(price + 100, 2)
        stoploss = round(price - 50, 2)
    else:
        signal = "🔴 SELL"
        target1 = round(price - 50, 2)
        target2 = round(price - 100, 2)
        stoploss = round(price + 50, 2)

    message = f"""
📊 NIFTY SIGNAL

Price: {price}

Signal: {signal}

🎯 Target 1: {target1}
🎯 Target 2: {target2}
🛑 Stop Loss: {stoploss}
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })