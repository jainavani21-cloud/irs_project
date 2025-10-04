"""
thingspeak_upload.py
Simple script to upload dummy (random) temperature & humidity to ThingSpeak
Channel ID: 3100147
Write API Key: ALNFYRUESG441UUA

Requirements:
    pip install requests
Run:
    python thingspeak_upload.py
Stop:
    Ctrl+C
"""

import requests
import random
import time
import sys
from datetime import datetime

# ---------- USER CONFIG ----------
API_KEY = "ALNFYRUESG441UUA"    # <-- your Write API Key
URL = "https://api.thingspeak.com/update"
UPLOAD_INTERVAL = 20            # seconds (ThingSpeak min is 15s; using 20s for safety)
CHANNEL_ID = 3100147
# ---------------------------------

def upload_once(temp, humidity):
    payload = {
        "api_key": API_KEY,
        "field1": temp,
        "field2": humidity
    }
    try:
        r = requests.get(URL, params=payload, timeout=10)
        # ThingSpeak returns the entry id (integer) on success (usually > 0)
        if r.status_code == 200:
            # r.text typically contains the entry id or "0" if failed within TS
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  Uploaded: Temp={temp}, Humidity={humidity}  → Response: {r.text.strip()}")
            return True
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  HTTP Error {r.status_code} while uploading.")
            return False
    except requests.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  Request failed: {e}")
        return False

def main():
    print("ThingSpeak dummy uploader starting...")
    print(f"Channel ID: {CHANNEL_ID}  |  Interval: {UPLOAD_INTERVAL}s")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            # generate dummy values
            temp = random.randint(20, 35)         # temperature (°C)
            humidity = random.randint(40, 80)     # humidity (%)

            success = upload_once(temp, humidity)

            # simple retry if failed: wait shorter then continue loop
            if not success:
                # small retry/wait logic
                for retry in range(3):
                    wait = 5
                    print(f"Retry {retry+1}/3 after {wait}s...")
                    time.sleep(wait)
                    temp = random.randint(20, 35)
                    humidity = random.randint(40, 80)
                    if upload_once(temp, humidity):
                        break

            time.sleep(UPLOAD_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped by user. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()
