import akshare as ak
import pandas as pd
import requests
import os
from datetime import datetime

# Global Config
SEND_KEY = os.environ.get('MY_SEND_KEY')
SYMBOL = "CL"  # WTI Crude Oil Futures

def send_wechat(title, content):
    if not SEND_KEY:
        print("Error: MY_SEND_KEY not found in environment.")
        return
    
    url = f"https://sctapi.ftqq.com/{SEND_KEY.strip()}.send"
    data = {"title": title, "desp": content}
    
    try:
        res = requests.post(url, data=data, timeout=15)
        print(f"Push Status: {res.json()}")
    except Exception as e:
        print(f"Push Failed: {e}")

def check_strategy():
    print(f"Execution Time: {datetime.now()}")
    try:
        # Fetching international oil data
        df = ak.futures_foreign_hist(symbol=SYMBOL)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Sensitive Indicators Calculation
        # SMA formula: $SMA_k = \frac{1}{k} \sum_{i=0}^{k-1} P_{t-i}$
        df['SMA3'] = df['close'].rolling(window=3).mean()
        df['SMA5'] = df['close'].rolling(window=5).mean()
        df['SMA10'] = df['close'].rolling(window=10).mean()

        last = df.iloc[-1]
        prev = df.iloc[-2]
        curr_p = last['close']
        
        print(f"Current Price: {curr_p} | SMA3: {last['SMA3']:.2f} | SMA10: {last['SMA10']:.2f}")

        # Signal 1: Fast Crossover (3-day vs 10-day)
        if prev['SMA3'] <= prev['SMA10'] and last['SMA3'] > last['SMA10']:
            send_wechat("Oil: Fast BUY", f"3/10 Golden Cross at ${curr_p}")
        elif prev['SMA3'] >= prev['SMA10'] and last['SMA3'] < last['SMA10']:
            send_wechat("Oil: Fast SELL", f"3/10 Death Cross at ${curr_p}")
        
        # Signal 2: Price Breakout (Price crossing 5-day SMA)
        elif prev['close'] <= prev['SMA5'] and last['close'] > last['SMA5']:
            send_wechat("Oil: Breakout UP", f"Price broke above SMA5 at ${curr_p}")
        elif prev['close'] >= prev['SMA5'] and last['close'] < last['SMA5']:
            send_wechat("Oil: Breakout DOWN", f"Price broke below SMA5 at ${curr_p}")
            
        else:
            print("Status: Monitoring - No sensitive signals detected.")
            
    except Exception as e:
        print(f"Runtime Error: {e}")

if __name__ == "__main__":
    check_strategy()
