import os
from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas_ta as ta
import pandas as pd

app = Flask(__name__)

# যে পেয়ারগুলোর সিগন্যাল আপনি চান
PAIRS = {
    'EUR/USD': 'EURUSD=X',
    'GBP/USD': 'GBPUSD=X',
    'USD/JPY': 'USDJPY=X',
    'BITCOIN': 'BTC-USD',
    'ETHEREUM': 'ETH-USD'
}

def fetch_signal(display_name, symbol):
    try:
        # ডেটা ফেচ করা
        df = yf.download(symbol, period='2d', interval='5m', progress=False)
        
        if df.empty or len(df) < 20:
            return {"pair": display_name, "signal": "NO DATA", "color": "grey", "price": "N/A"}

        # RSI ক্যালকুলেশন
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        last_row = df.iloc[-1]
        price = last_row['Close']
        rsi = last_row['RSI']

        signal, color = "WAIT", "white"
        if rsi < 35:
            signal, color = "CALL (UP) ⬆️", "#2ecc71"
        elif rsi > 65:
            signal, color = "PUT (DOWN) ⬇️", "#e74c3c"

        return {
            "pair": display_name,
            "price": round(float(price), 5) if price > 1 else round(float(price), 2),
            "rsi": round(float(rsi), 1) if not pd.isna(rsi) else "N/A",
            "signal": signal,
            "color": color
        }
    except:
        return {"pair": display_name, "signal": "ERROR", "color": "orange", "price": "N/A"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/signals')
def api():
    results = []
    for display_name, symbol in PAIRS.items():
        results.append(fetch_signal(display_name, symbol))
    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
