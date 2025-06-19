import requests
import time
from datetime import datetime

# === CONFIG ===
API_KEY = "482a2fd5f74a4fd2b72badeb0be46e96"
TELEGRAM_TOKEN = "8154585077:AAHaAcQeKa2HH01vH7wa0pInNP7N3OpOS2g"
TELEGRAM_CHAT_ID = "7919142705"
SYMBOLS = {
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "XAU/USD": "XAU/USD"
}
INTERVALS = ["1min", "5min"]

# === FUNCTIONS ===
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print("Telegram Error:", response.text)
    except Exception as e:
        print("Telegram Exception:", e)

def fetch_candles(symbol, interval):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={API_KEY}&outputsize=2"
    try:
        response = requests.get(url)
        data = response.json()
        if "values" not in data:
            print(f"Fetch error ({interval}):", data.get("message", "No data"))
            return None
        return data["values"]
    except Exception as e:
        print("Request failed:", e)
        return None

def detect_candle_pattern(candles):
    try:
        c1 = candles[1]
        c2 = candles[0]
        open1, close1 = float(c1['open']), float(c1['close'])
        open2, close2 = float(c2['open']), float(c2['close'])

        if open1 > close1 and open2 > close2 and close2 < open1 and open2 > close1:
            return "Bearish Engulfing"
        if open1 < close1 and open2 > close2 and close2 > open1 and open2 < close1:
            return "Bullish Engulfing"
        if open1 < close1 and open2 < close2 and open2 < close1:
            return "Three White Soldiers"
        if open1 > close1 and open2 > close2 and open2 > close1:
            return "Three Black Crows"
        return None
    except Exception as e:
        print("Pattern detection error:", e)
        return None

# === MAIN LOOP ===
print("FXMBot is running...\n")
while True:
    for symbol in SYMBOLS:
        patterns = []
        for interval in INTERVALS:
            candles = fetch_candles(SYMBOLS[symbol], interval)
            if candles:
                pattern = detect_candle_pattern(candles)
                patterns.append(pattern)
            else:
                patterns.append(None)

        if patterns[0] and patterns[0] == patterns[1]:
            msg = f"🔔 [{symbol}] Signal: {patterns[0]}\n{datetime.now().strftime('%H:%M:%S')}"
            print(msg)
            send_telegram(msg)
        else:
            msg = f"❌ [{symbol}] No signal at {datetime.now().strftime('%H:%M:%S')}"
            print(msg)
            send_telegram(msg)

    time.sleep(45)
