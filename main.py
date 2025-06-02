import requests
import pandas as pd
import time
from datetime import datetime
from flask import Flask
import threading

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1378808063900778506/mSM9C5JD5bNPyGvnf6J05SWEC8lPhhH-llSZJdLDZWNmS0i5CBD4G-b86hm5xF4mOuUy"
symbol = "BTCUSDT"
interval = "1m"
limit = 100

def get_candles():
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.astype({'open': float, 'high': float, 'low': float, 'close': float})
    return df

def is_hammer(candle):
    body = abs(candle['close'] - candle['open'])
    lower_wick = min(candle['open'], candle['close']) - candle['low']
    upper_wick = candle['high'] - max(candle['open'], candle['close'])
    return (lower_wick > 2 * body) and (upper_wick < body)

def send_alert(candle):
    msg = {
        "content": f"🔨 Hammer Candle Detected!\nTime: {candle['timestamp']}\nClose: ${candle['close']:.2f}"
    }
    requests.post(WEBHOOK_URL, json=msg)

def run_checker():
    while True:
        try:
            df = get_candles()
            last = df.iloc[-2]
            if is_hammer(last):
                send_alert(last)
                print(f"Hammer found at {last['timestamp']}")
            else:
                print(f"No hammer at {last['timestamp']}")
        except Exception as e:
            print("Error:", e)
        time.sleep(900)  # 15 min

@app.route("/")
def home():
    return "Bot is running!", 200

if __name__ == "__main__":
    # Start background thread BEFORE starting Flask app
    threading.Thread(target=run_checker, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
