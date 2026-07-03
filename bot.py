import requests
import yfinance as yf

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

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