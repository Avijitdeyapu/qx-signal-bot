import os
from flask import Flask, render_template, jsonify, request
from tradingview_ta import TA_Handler, Interval

app = Flask(__name__)

# টাইমফ্রেম ম্যাপিং
INTERVALS = {
    "1m": Interval.INTERVAL_1_MINUTE,
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "30m": Interval.INTERVAL_30_MINUTES
}

def get_analysis(symbol, screener, exchange, interval_key):
    # ১০, ১৫, ২০ মিনিটের জন্য ১৫ মিনিটের ডেটা ব্যবহার করা হচ্ছে (সবচেয়ে নির্ভুল)
    if interval_key in ["10m", "15m", "20m"]:
        target_interval = Interval.INTERVAL_15_MINUTES
    else:
        target_interval = INTERVALS.get(interval_key, Interval.INTERVAL_1_MINUTE)

    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange=exchange,
            screener=screener,
            interval=target_interval
        )
        analysis = handler.get_analysis()
        summary = analysis.summary
        
        recommendation = summary['RECOMMENDATION']
        color = "#8895a7"
        signal = "NEUTRAL"

        if "STRONG_BUY" in recommendation:
            signal, color = "STRONG CALL ⬆️", "#00ff00"
        elif "BUY" in recommendation:
            signal, color = "CALL ⬆️", "#2ecc71"
        elif "STRONG_SELL" in recommendation:
            signal, color = "STRONG PUT ⬇️", "#ff0000"
        elif "SELL" in recommendation:
            signal, color = "PUT ⬇️", "#e74c3c"
        
        return {
            "pair": symbol,
            "signal": signal,
            "color": color,
            "price": round(analysis.indicators['close'], 5)
        }
    except:
        return {"pair": symbol, "signal": "ERROR", "color": "orange", "price": "N/A"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/signals')
def api():
    t_frame = request.args.get('timeframe', '1m')
    pairs = [
        {"symbol": "EURUSD", "screener": "forex", "exchange": "FX_IDC"},
        {"symbol": "GBPUSD", "screener": "forex", "exchange": "FX_IDC"},
        {"symbol": "USDJPY", "screener": "forex", "exchange": "FX_IDC"},
        {"symbol": "BTCUSDT", "screener": "crypto", "exchange": "BINANCE"},
        {"symbol": "ETHUSDT", "screener": "crypto", "exchange": "BINANCE"}
    ]
    
    results = [get_analysis(p['symbol'], p['screener'], p['exchange'], t_frame) for p in pairs]
    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
