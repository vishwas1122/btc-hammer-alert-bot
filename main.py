from flask import Flask
import threading
import time
import datetime

app = Flask(__name__)

def background_task():
    while True:
        print(f"[{datetime.datetime.now()}] Background task running...")
        time.sleep(60)  # 60 seconds

thread = threading.Thread(target=background_task)
thread.daemon = True
thread.start()

@app.route('/')
def home():
    return "Server is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
