import numpy as np
import pandas as pd


def _numeric(series, default=0):
    return pd.to_numeric(series, errors="coerce").fillna(default)


def _minmax(series):
    s = _numeric(series)
    lo = s.min()
    hi = s.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(0.0, index=s.index)
    return (s - lo) / (hi - lo)


def _clean_ticker_frame(df, ticker_col="ticker"):
    out = df.copy()
    out[ticker_col] = out[ticker_col].astype(str).str.strip().str.upper()
    out = out[out[ticker_col].ne("")]
    return out


def filter_fundamentals(fundamentals_df):
    """Loose, stable filter for the tradable universe before signal scoring."""
    if fundamentals_df is None or fundamentals_df.empty:
        return pd.DataFrame()

    df = _clean_ticker_frame(fundamentals_df)

    for col in [
        "open",
        "market_cap",
        "shares_float",
        "average_volume_30_days",
        "volume",
        "high",
        "low",
    ]:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = _numeric(df[col], default=np.nan)

    return df[
        (df["open"] >= 1.5)
        & (df["open"] <= 30)
        & (df["market_cap"] >= 20_000_000)
        & (df["market_cap"] <= 10_000_000_000)
        & (df["shares_float"] >= 1_000_000)
        & (df["average_volume_30_days"] >= 150_000)
    ].copy()


def score_stock_universe(fundamentals_df, stocktwits_df=None, news_df=None):
    """Return a ranked stock universe using fundamentals plus optional signal boosts."""
    fundamentals = filter_fundamentals(fundamentals_df)
    if fundamentals.empty:
        return fundamentals

    df = fundamentals.copy()

    df["volume"] = _numeric(df.get("volume", 0))
    df["average_volume_30_days"] = _numeric(df.get("average_volume_30_days", 0)).replace(0, np.nan)
    df["open"] = _numeric(df.get("open", 0)).replace(0, np.nan)
    df["high"] = _numeric(df.get("high", 0))
    df["low"] = _numeric(df.get("low", 0))
    df["shares_float"] = _numeric(df.get("shares_float", 0)).replace(0, np.nan)

    df["dollar_volume"] = df["open"] * df["volume"]
    df["rel_volume"] = (df["volume"] / df["average_volume_30_days"]).replace([np.inf, -np.inf], np.nan).fillna(0)
    df["range_pct"] = ((df["high"] - df["low"]) / df["open"]).replace([np.inf, -np.inf], np.nan).fillna(0)

    liquidity_score = _minmax(np.log1p(df["dollar_volume"].clip(lower=0)))
    activity_score = _minmax(np.log1p(df["rel_volume"].clip(lower=0, upper=20)))
    range_score = _minmax(df["range_pct"].clip(lower=0, upper=0.5))
    float_score = 1 - _minmax(np.log1p(df["shares_float"].fillna(df["shares_float"].max()).clip(lower=1)))
    price_score = (1 - ((df["open"] - 8).abs() / 22)).clip(lower=0, upper=1).fillna(0)

    df["fundamental_score"] = (
        35 * liquidity_score
        + 25 * activity_score
        + 20 * range_score
        + 10 * float_score
        + 10 * price_score
    )

    if stocktwits_df is not None and not stocktwits_df.empty:
        st = _clean_ticker_frame(stocktwits_df)
        st["sent_score"] = _numeric(st.get("sent_score", 0))
        st["message_volume"] = _numeric(st.get("message_volume", 0))
        st["watch_count"] = _numeric(st.get("watch_count", 0))
        st = st.groupby("ticker", as_index=False).agg(
            {
                "sent_score": "max",
                "message_volume": "max",
                "watch_count": "max",
            }
        )
        st["stocktwits_score"] = (
            55 * (st["sent_score"].clip(0, 100) / 100)
            + 30 * _minmax(np.log1p(st["message_volume"].clip(lower=0)))
            + 15 * _minmax(np.log1p(st["watch_count"].clip(lower=0)))
        )
        df = df.merge(
            st[["ticker", "sent_score", "message_volume", "watch_count", "stocktwits_score"]],
            on="ticker",
            how="left",
        )
        df["stocktwits_score"] = df["stocktwits_score"].fillna(0)
    else:
        df["stocktwits_score"] = 0.0

    if news_df is not None and not news_df.empty:
        news = _clean_ticker_frame(news_df)
        if "article_count" not in news.columns:
            news["article_count"] = 1
        news["article_count"] = _numeric(news["article_count"])
        news = news.groupby("ticker", as_index=False)["article_count"].sum()
        news["news_score"] = 100 * _minmax(np.log1p(news["article_count"].clip(lower=0)))
        df = df.merge(news[["ticker", "article_count", "news_score"]], on="ticker", how="left")
        df["news_score"] = df["news_score"].fillna(0)
        df["article_count"] = df["article_count"].fillna(0)
    else:
        df["news_score"] = 0.0

    df["signal_score"] = (
        0.55 * df["fundamental_score"]
        + 0.25 * df["stocktwits_score"]
        + 0.20 * df["news_score"]
    )

    return df.sort_values("signal_score", ascending=False).reset_index(drop=True)
