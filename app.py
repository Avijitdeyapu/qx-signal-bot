import os
from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas_ta as ta

app = Flask(__name__)

def get_signal(pair):
    try:
        # ডেটা আনার চেষ্টা
        df = yf.download(pair, period='2d', interval='5m', progress=False)
        
        if df is None or len(df) < 20:
            return {"pair": pair, "signal": "DATA ERROR", "color": "yellow", "price": "N/A", "rsi": "N/A"}

        # RSI ক্যালকুলেশন
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # Bollinger Bands
        bbands = ta.bbands(df['Close'], length=20, std=2)
        if bbands is not None:
            df = df.join(bbands)

        last = df.iloc[-1]
        price = last['Close']
        rsi = last['RSI']
        
        # ডিফল্ট ভ্যালু
        signal, color = "WAIT", "white"
        
        # সিগন্যাল লজিক
        if rsi < 35:
            signal, color = "CALL (UP) ⬆️", "#2ecc71"
        elif rsi > 65:
            signal, color = "PUT (DOWN) ⬇️", "#e74c3c"
            
        return {
            "pair": pair,
            "price": round(float(price), 5),
            "rsi": round(float(rsi), 2) if rsi else "N/A",
            "signal": signal,
            "color": color
        }
    except Exception as e:
        return {"pair": pair, "signal": "SERVER BUSY", "color": "orange", "price": "Check Log", "rsi": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/signal')
def api():
    res = get_signal("EURUSD=X")
    return jsonify(res)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
