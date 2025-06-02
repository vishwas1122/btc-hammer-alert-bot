from flask import Flask
import threading
import time
import datetime
import sys
import traceback

app = Flask(__name__)

def background_task():
    try:
        print(f"[{datetime.datetime.now()}] Background task started...", flush=True)
        while True:
            print(f"[{datetime.datetime.now()}] Background task running...", flush=True)
            time.sleep(60)  # 60 seconds
    except Exception as e:
        print(f"Error in background task: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()

def start_thread():
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()
    print(f"[{datetime.datetime.now()}] Thread started.", flush=True)

start_thread()

@app.route('/')
def home():
    return "Server is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
