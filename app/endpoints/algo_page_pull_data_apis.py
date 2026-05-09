













@app.route("/api/profile_data")
def api_profile_data():

    return {
        "success": True,
        "data": {
            "username": "AlphaTrader",
            "email": "alpha@hedgefund.ai",
            "account_type": "Pro",
            "risk_profile": "Aggressive",
            "last_login": "2026-02-28 21:44"
        }
    }






@app.route("/api/trade_history")
def api_trade_history():

    import pandas as pd
    import random
    from datetime import datetime, timedelta
    from flask import request, jsonify

    range_param = request.args.get("range", "all")

    tickers = [
        "NVDA", "AAPL", "TSLA", "META", "AMZN",
        "MSFT", "AMD", "GOOGL", "COIN", "SMCI"
    ]

    sides = ["BUY", "SELL"]

    # -------------------------------------------------
    # Generate 1 year of trades
    # -------------------------------------------------
    base_time = datetime.now() - timedelta(days=365)

    trades = []

    Y = 0
    while Y < 200:  # generate 200 total trades

        random_minutes = random.randint(0, 365 * 24 * 60)
        trade_time = base_time + timedelta(minutes=random_minutes)

        trade = {
            "date": trade_time,
            "ticker": random.choice(tickers),
            "side": random.choice(sides),
            "qty": random.randint(5, 200),
            "price": round(random.uniform(50, 900), 2)
        }

        trades.append(trade)
        Y += 1

    trades_df = pd.DataFrame(trades)

    # -------------------------------------------------
    # Apply Range Filter
    # -------------------------------------------------
    now = datetime.now()

    if range_param == "1d":
        cutoff = now - timedelta(days=1)
        trades_df = trades_df[trades_df["date"] >= cutoff]

    elif range_param == "1w":
        cutoff = now - timedelta(days=7)
        trades_df = trades_df[trades_df["date"] >= cutoff]

    elif range_param == "1m":
        cutoff = now - timedelta(days=30)
        trades_df = trades_df[trades_df["date"] >= cutoff]

    elif range_param == "1y":
        cutoff = now - timedelta(days=365)
        trades_df = trades_df[trades_df["date"] >= cutoff]

    # all → no filtering

    trades_df = trades_df.sort_values("date", ascending=False)

    trades_df["date"] = trades_df["date"].dt.strftime("%Y-%m-%d %H:%M")

    return jsonify({
        "success": True,
        "trades": trades_df.to_dict(orient="records")
    })







@app.route("/api/performance_timeseries")
def api_performance_timeseries():

    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    from flask import request, session, jsonify

    range_param = request.args.get("range", "all")
    algo_name = session.get("algo_selection", "Algo")

    now = datetime.now()

    ############################################################
    # RESOLUTION LOGIC
    ############################################################

    if range_param == "1d":
        start_time = now - timedelta(days=1)
        freq = "5min"      # 288 points
    elif range_param == "1w":
        start_time = now - timedelta(days=7)
        freq = "1H"        # 168 points
    elif range_param == "1m":
        start_time = now - timedelta(days=30)
        freq = "1D"
    elif range_param == "1y":
        start_time = now - timedelta(days=365)
        freq = "1D"
    else:
        start_time = now - timedelta(days=365)
        freq = "1D"

    ############################################################
    # CREATE DATE RANGE
    ############################################################

    date_range = pd.date_range(start=start_time, end=now, freq=freq)

    algo_vals = []
    nasdaq_vals = []
    sp_vals = []

    algo = 100
    nasdaq = 100
    sp = 100

    Y = 0
    while Y < len(date_range):

        # smaller volatility for shorter intervals
        if freq == "5min":
            algo += np.random.normal(0.02, 0.15)
            nasdaq += np.random.normal(0.01, 0.10)
            sp += np.random.normal(0.008, 0.08)
        elif freq == "1H":
            algo += np.random.normal(0.05, 0.4)
            nasdaq += np.random.normal(0.03, 0.3)
            sp += np.random.normal(0.02, 0.25)
        else:
            algo += np.random.normal(0.25, 1.2)
            nasdaq += np.random.normal(0.15, 0.9)
            sp += np.random.normal(0.12, 0.7)

        algo_vals.append(round(algo, 2))
        nasdaq_vals.append(round(nasdaq, 2))
        sp_vals.append(round(sp, 2))

        Y += 1

    df = pd.DataFrame({
        "date": date_range,
        "algo": algo_vals,
        "nasdaq": nasdaq_vals,
        "sp500": sp_vals
    })

    ############################################################
    # FORMAT DATES
    ############################################################

    if freq in ["5min", "1H"]:
        df["date"] = df["date"].dt.strftime("%Y-%m-%d %H:%M")
    else:
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    return jsonify({
        "success": True,
        "dates": df["date"].tolist(),
        "algo": df["algo"].tolist(),
        "nasdaq": df["nasdaq"].tolist(),
        "sp500": df["sp500"].tolist(),
        "algo_name": f"{algo_name} Strategy"
    })





@app.route("/api/stock_universe")
def api_stock_universe():

    from flask import request, jsonify

    range_param = request.args.get("range", "all")

    ############################################################
    # Time Filter
    ############################################################

    if range_param == "1d":
        time_filter = "WHERE added_time >= NOW() - INTERVAL 1 DAY"

    elif range_param == "1w":
        time_filter = "WHERE added_time >= NOW() - INTERVAL 7 DAY"

    elif range_param == "1m":
        time_filter = "WHERE added_time >= NOW() - INTERVAL 30 DAY"

    elif range_param == "1y":
        time_filter = "WHERE added_time >= NOW() - INTERVAL 365 DAY"

    else:
        time_filter = ""

    ############################################################
    # Query
    ############################################################

    query = f"""
        SELECT ticker, co_name, added_time
        FROM ticker_universe__filtered
        {time_filter}
        ORDER BY added_time DESC
    """

    df = run_sql(query).to_df()

    ############################################################
    # SAFE EMPTY HANDLING
    ############################################################

    if df is None or df.empty:
        return jsonify({
            "success": True,
            "count": 0,
            "rows": []
        })

    rows = df[["ticker", "co_name"]].to_dict(orient="records")

    return jsonify({
        "success": True,
        "count": len(rows),
        "rows": rows
    })










@app.route("/api/trade_restrictions")
def api_trade_restrictions():

    today = date.today()

    fake_data = [
        {"ticker": "AAPL", "restricted_until": str(today + timedelta(days=1))},
        {"ticker": "NVDA", "restricted_until": str(today + timedelta(days=2))},
        {"ticker": "TSLA", "restricted_until": str(today + timedelta(days=1))},
        {"ticker": "AMD",  "restricted_until": str(today + timedelta(days=2))},
        {"ticker": "META", "restricted_until": str(today + timedelta(days=1))},
        {"ticker": "MSFT", "restricted_until": str(today + timedelta(days=2))},
        {"ticker": "AMZN", "restricted_until": str(today + timedelta(days=1))},
        {"ticker": "GOOG", "restricted_until": str(today + timedelta(days=2))},
        {"ticker": "SMCI", "restricted_until": str(today + timedelta(days=1))},
        {"ticker": "PLTR", "restricted_until": str(today + timedelta(days=2))}
    ]

    return {
        "success": True,
        "rows": fake_data
    }






















@app.route("/api/get_scraper_inputs", methods=["GET"])
def get_scraper_inputs():

    algo = session["algo_selection"]

    df = run_sql("""
        SELECT
            scraper_stocktwits,
            scraper_wsj,
            scraper_tradingview,
            scraper_benzinga,
            scraper_yahoo,
            scraper_etf_universe
        FROM admin__algo__scraper_inputs
        WHERE algo = %s
    """, (algo,)).to_df()

    if df.empty:
        return {
            "scraper_stocktwits": 0,
            "scraper_wsj": 0,
            "scraper_tradingview": 0,
            "scraper_benzinga": 0,
            "scraper_yahoo": 0,
            "scraper_etf_universe": 0
        }

    return {
        "scraper_stocktwits": int(df["scraper_stocktwits"].iloc[0]),
        "scraper_wsj": int(df["scraper_wsj"].iloc[0]),
        "scraper_tradingview": int(df["scraper_tradingview"].iloc[0]),
        "scraper_benzinga": int(df["scraper_benzinga"].iloc[0]),
        "scraper_yahoo": int(df["scraper_yahoo"].iloc[0]),
        "scraper_etf_universe": int(df["scraper_etf_universe"].iloc[0])
    }









@app.route("/api/get_trade_window", methods=["GET"])
def get_trade_window():

    algo_name = session["algo_selection"]

    df = run_sql("""
        SELECT start_time, end_time
        FROM admin__algo__trade_window
        WHERE algo_name = %s
    """, (algo_name,)).to_df()

    if df.empty:
        return {
            "start_time": None,
            "end_time": None
        }

    def format_time(value):
        if value is None:
            return None
        if hasattr(value, "strftime"):
            return value.strftime("%H:%M")
        return str(value)[:5]

    return {
        "start_time": format_time(df["start_time"].iloc[0]),
        "end_time": format_time(df["end_time"].iloc[0])
    }







@app.route("/api/get_run_schedule", methods=["GET"])
def get_run_schedule():

    algo_name = session.get("algo_selection", "Alpha")

    df = run_sql("""
        SELECT
            run_forever,
            run_selected_days,
            start_date,
            end_date
        FROM admin__algo__schedule
        WHERE algo_name = %s
    """, (algo_name,)).to_df()

    if df.empty:
        return {
            "run_forever": 0,
            "run_selected_days": 0,
            "start_date": None,
            "end_date": None
        }

    return {
        "run_forever": int(df["run_forever"].iloc[0]),
        "run_selected_days": int(df["run_selected_days"].iloc[0]),
        "start_date": str(df["start_date"].iloc[0]) if df["start_date"].iloc[0] else None,
        "end_date": str(df["end_date"].iloc[0]) if df["end_date"].iloc[0] else None
    }









@app.route("/api/get_algo_status", methods=["GET"])
def get_algo_status():

    algo_name = session.get("algo_selection", "Alpha")

    status_df = run_sql("""
        SELECT status
        FROM admin__algo_status
        WHERE algo_name = %s
    """, (algo_name,)).to_df()

    if not status_df.empty:
        status = status_df["status"].iloc[0]
    else:
        status = "off"

    return status   # ← just returns "on" or "off" or "test"






























