import akshare as ak
import pandas as pd
import requests
import os
from datetime import datetime

SEND_KEY = os.environ.get('MY_SEND_KEY')
SYMBOL = "CL"

def send_wechat(title, content):
    if not SEND_KEY:
        print("Error: MY_SEND_KEY not found")
        return
    
    key = SEND_KEY.strip()
    url = f"https://sctapi.ftqq.com/{key}.send"
    data = {"title": title, "desp": content}
    
    try:
        res = requests.post(url, data=data, timeout=10)
        print(f"Push Status: {res.json()}")
    except Exception as e:
        print(f"Push Failed: {e}")

def check_strategy():
    print(f"Execution Time: {datetime.now()}")
    try:
        df = ak.futures_foreign_hist(symbol=SYMBOL)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        df['SMA5'] = df['close'].rolling(window=5).mean()
        df['SMA20'] = df['close'].rolling(window=20).mean()

        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        print(f"Price: {last['close']} | SMA5: {last['SMA5']:.2f} | SMA20: {last['SMA20']:.2f}")

        if prev['SMA5'] <= prev['SMA20'] and last['SMA5'] > last['SMA20']:
            send_wechat("Oil Alert: BUY", f"Golden Cross at ${last['close']}")
        elif prev['SMA5'] >= prev['SMA20'] and last['SMA5'] < last['SMA20']:
            send_wechat("Oil Alert: SELL", f"Death Cross at ${last['close']}")
        else:
            print("Status: No Signal")
            
    except Exception as e:
        print(f"Runtime Error: {e}")

if __name__ == "__main__":
    send_wechat("Monitor Active", "Service started successfully.")
    check_strategy()
