import time
import requests
import pandas as pd
from flask import Flask
from threading import Thread
from datetime import datetime

app = Flask(__name__)

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1378808063900778506/mSM9C5JD5bNPyGvnf6J05SWEC8lPhhH-llSZJdLDZWNmS0i5CBD4G-b86hm5xF4mOuUy'

def fetch_candles():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",  # 1-minute candle
        "limit": 2
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    return df

def is_hammer(open_, high, low, close):
    body = abs(close - open_)
    upper_shadow = high - max(open_, close)
    lower_shadow = min(open_, close) - low
    return (
        body <= (high - low) * 0.3 and  # small body
        lower_shadow >= body * 2 and    # long lower wick
        upper_shadow <= body            # small upper wick
    )

def send_alert(candle):
    msg = f"""**BTC Hammer Alert 🛠️**
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Open: {candle['open']}
High: {candle['high']}
Low: {candle['low']}
Close: {candle['close']}
"""
    requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})

def background_task():
    last_alert_time = None
    while True:
        try:
            print(f"[{datetime.now()}] Checking for hammer...")
            df = fetch_candles()
            last_candle = df.iloc[-2]

            if is_hammer(last_candle["open"], last_candle["high"], last_candle["low"], last_candle["close"]):
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                if last_alert_time != current_time:  # avoid spamming
                    print("✅ Hammer detected! Sending alert.")
                    send_alert(last_candle)
                    last_alert_time = current_time
                else:
                    print("⚠️ Hammer already alerted for this minute.")
            else:
                print("No hammer found.")
        except Exception as e:
            print("Error:", e)

        time.sleep(60)  # check every minute

@app.route('/')
def home():
    return "BTC Hammer Alert Bot is Running!"

def start_background_thread():
    thread = Thread(target=background_task)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_background_thread()
    app.run(host='0.0.0.0', port=8080)
