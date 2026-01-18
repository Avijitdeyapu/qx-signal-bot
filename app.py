import os
from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas_ta as ta

app = Flask(__name__)

def get_signal(pair):
    try:
        df = yf.download(pair, period='1d', interval='5m')
        if df.empty: return {"error": "No Data"}
        df['RSI'] = ta.rsi(df['Close'], length=14)
        bbands = ta.bbands(df['Close'], length=20, std=2)
        df = df.join(bbands)
        last = df.iloc[-1]
        price = last['Close']
        rsi = last['RSI']
        lower = last['BBL_20_2.0']
        upper = last['BBU_20_2.0']
        signal, color = "WAIT", "white"
        if rsi < 35 and price <= lower:
            signal, color = "CALL (UP) ⬆️", "#2ecc71"
        elif rsi > 65 and price >= upper:
            signal, color = "PUT (DOWN) ⬇️", "#e74c3c"
        return {"pair": pair, "price": round(price, 5), "rsi": round(rsi, 2), "signal": signal, "color": color}
    except: return {"error": "Error"}

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
