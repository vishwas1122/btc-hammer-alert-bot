from flask import Flask
import threading
import time
import requests
import pandas as pd
import datetime

app = Flask(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1378808063900778506/mSM9C5JD5bNPyGvnf6J05SWEC8lPhhH-llSZJdLDZWNmS0i5CBD4G-b86hm5xF4mOuUy"

def send_discord_alert(message):
    data = {
        "content": message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    print(f"Sent alert: {response.status_code}")

def fetch_candles():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 2
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    return df

def is_hammer(open_price, high, low, close):
    body = abs(close - open_price)
    lower_wick = open_price - low if close > open_price else close - low
    upper_wick = high - close if close > open_price else high - open_price
    return lower_wick > body * 2 and upper_wick < body

def monitor():
    while True:
        print(f"[{datetime.datetime.now()}] Checking for hammer...")
        df = fetch_candles()
        latest = df.iloc[-1]
        if is_hammer(latest["open"], latest["high"], latest["low"], latest["close"]):
            message = f"🚨 BTC 1m Hammer Detected at {datetime.datetime.now().strftime('%H:%M:%S')}!"
            send_discord_alert(message)
        time.sleep(60)

@app.route('/')
def home():
    return "BTC Hammer Alert Bot is Running!"

def send_test_alert():
    send_discord_alert("🔔 **Test Alert:** BTC Hammer candle detected (sample message).")

if __name__ == '__main__':
    send_test_alert()  # ✅ Test message on startup
    threading.Thread(target=monitor).start()
    app.run(host='0.0.0.0', port=8080)
