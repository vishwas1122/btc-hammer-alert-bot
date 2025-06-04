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
            print("✅ Discord message sent successfully.")
        else:
            print(f"❌ Failed to send message: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Exception sending message: {e}")

def fetch_latest_candles(symbol="BTCUSDT", interval='5m', limit=3):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def is_hammer_candle(candle):
    open_price = float(candle[1])
    high_price = float(candle[2])
    low_price = float(candle[3])
    close_price = float(candle[4])

    body = abs(close_price - open_price)
    lower_wick = min(open_price, close_price) - low_price
    upper_wick = high_price - max(open_price, close_price)

    print(f"Body: {body:.2f}, Lower wick: {lower_wick:.2f}, Upper wick: {upper_wick:.2f}")

    if body == 0:
        return False
    if lower_wick > 2 * body and upper_wick < 0.1 * body:
        return True
    return False

def monitor():
    last_checked_candle_time = None
    while True:
        try:
            candles = fetch_latest_candles()
            completed_candle = candles[-2]  # use the previous completed candle
            open_time = completed_candle[0]

            if open_time != last_checked_candle_time:
                last_checked_candle_time = open_time
                timestamp = datetime.datetime.fromtimestamp(open_time / 1000).strftime('%Y-%m-%d %H:%M:%S')

                if is_hammer_candle(completed_candle):
                    message = f"🚨 Hammer Candle detected on BTC/USDT at {timestamp} (5m candle)"
                    send_discord_message(message)
                else:
                    print(f"[{datetime.datetime.now()}] ❌ No hammer candle at {timestamp}")
            time.sleep(30)
        except Exception as e:
            print(f"❌ Error in monitor loop: {e}")
            time.sleep(30)

@app.route('/')
def home():
    return "BTC Hammer Candle Alert Bot is running!"

if __name__ == '__main__':
    threading.Thread(target=monitor).start()
    app.run(host='0.0.0.0', port=8080)
