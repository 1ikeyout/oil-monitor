import akshare as ak
import pandas as pd
import requests
import os
from datetime import datetime

# Configuration
SEND_KEY = os.environ.get('MY_SEND_KEY')
SYMBOL = "CL" # WTI Crude Oil Futures

def send_wechat(title, content):
    """Push messages via ServerChan"""
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
    """Strategy Logic: 5-day / 20-day SMA Crossover"""
    print(f"Execution Time: {datetime.now()}")
    try:
        # Fetch historical data
        df = ak.futures_foreign_hist(symbol=SYMBOL)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate Technical Indicators
        df['SMA5'] = df['close'].rolling(window=5).mean()
        df['SMA20'] = df['close'].rolling(window=20).mean()

        last = df.iloc[-1]   # Latest data
        prev = df.iloc[-2]   # Previous day data
        
        current_price = last['close']
        print(f"Price: {current_price} | SMA5: {last['SMA5']:.2f} | SMA20: {last['SMA20']:.2f}")

        # Signal Logic: Golden Cross to Buy, Death Cross to Sell
        if prev['SMA5'] <= prev['SMA20'] and last['SMA5'] > last['SMA20']:
            send_wechat("Oil Alert: BUY", f"Golden Cross! Price: ${current_price}")
        elif prev['SMA5'] >= prev['SMA20'] and last['SMA5'] < last['SMA20']:
            send_wechat("Oil Alert: SELL", f"Death Cross! Price: ${current_price}")
        else:
            print("Status: No Signal Change")
            
    except Exception as e:
        print(f"Runtime Error: {e}")

if __name__ == "__main__":
    check_strategy()
