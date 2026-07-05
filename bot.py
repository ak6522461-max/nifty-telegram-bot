import requests
import yfinance as yf

BOT_TOKEN = "8635826832:AAG6UZ6nNq9unKmT-yf7J-lu2lHiWoI7PAE"
CHAT_ID = "7282928970"

symbol = "^NSEI"

data = yf.Ticker(symbol)
hist = data.history(period="2d", interval="5m")

if len(hist) > 0:
    price = round(hist["Close"].iloc[-1], 2)
    message = f"📈 NIFTY Live Price: {price}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })