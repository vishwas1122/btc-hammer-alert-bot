import requests
import time
import threading
from flask import Flask
import datetime

app = Flask(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1378808063900778506/mSM9C5JD5bNPyGvnf6J05SWEC8lPhhH-llSZJdLDZWNmS0i5CBD4G-b86hm5xF4mOuUy"

def send_discord_message(message):
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("Discord message sent successfully.")
        else:
            print(f"Failed to send message to Discord: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Exception sending Discord message: {e}")

def fetch_latest_candles(symbol="BTCUSDT", interval='5m', limit=2):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data

def is_hammer_candle(candle):
    """
    candle = [
        Open time,
        Open,
        High,
        Low,
        Close,
        Volume,
        Close time,
        ...
    ]
    Logic for hammer candle:
    - small real body near top of the candle
    - long lower wick (at least twice the body)
    - little or no upper wick
    """
    open_price = float(candle[1])
    high_price = float(candle[2])
    low_price = float(candle[3])
    close_price = float(candle[4])

    body = abs(close_price - open_price)
    lower_wick = min(open_price, close_price) - low_price
    upper_wick = high_price - max(open_price, close_price)

    if body == 0:
        return False

    if lower_wick > 2 * body and upper_wick < 0.1 * body:
        # hammer pattern detected
        return True
    return False

def monitor():
    last_checked_candle_time = None
    while True:
        try:
            candles = fetch_latest_candles()
            latest_candle = candles[-1]
            open_time = latest_candle[0]

            # Check candle only once per new candle
            if open_time != last_checked_candle_time:
                last_checked_candle_time = open_time

                if is_hammer_candle(latest_candle):
                    timestamp = datetime.datetime.fromtimestamp(open_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    message = f"🚨 Hammer Candle detected on BTC/USDT at {timestamp} (5m candle)"
                    send_discord_message(message)
                else:
                    print(f"[{datetime.datetime.now()}] No hammer candle detected.")

            time.sleep(30)  # check every 30 seconds to catch new candle quickly
        except Exception as e:
            print(f"Error in monitor loop: {e}")
            time.sleep(30)

@app.route('/')
def home():
    return "BTC Hammer Candle Alert Bot is running!"

if __name__ == '__main__':
    threading.Thread(target=monitor).start()
    app.run(host='0.0.0.0', port=8080)
