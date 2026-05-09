#Fundamental Filter (DO NOT OVERFILTER HERE)
########################################################################################################

#Pre-Calculate Metrics
df = robinhood_fundamentals_df.copy()
df['average_volume_30_days'] = df['average_volume_30_days'].replace(0, 1)
df['open'] = df['open'].replace(0, 1)
df['rel_volume'] = df['volume'] / df['average_volume_30_days']
df['range_pct'] = (df['high'] - df['low']) / df['open']


fundamentals_filter_df = df[

    # =========================
    # LIQUIDITY
    # =========================
    (df['volume'] >= 200_000) &
    (df['average_volume_30_days'] >= 200_000) &

    # =========================
    # RELATIVE VOLUME (looser)
    # =========================
    (df['rel_volume'] >= 0.8) &   # 🔥 was 1.3

    # =========================
    # PRICE RANGE
    # =========================
    (df['open'] >= 1.5) &
    (df['open'] <= 100) &

    # =========================
    # SIZE
    # =========================
    (df['market_cap'] >= 20_000_000) &

    # =========================
    # FLOAT
    # =========================
    (df['shares_float'] >= 1_000_000) &

    # =========================
    # MOVEMENT (only thing we can trust here)
    # =========================
    (df['range_pct'] >= 0.02)   # 2% move
]



#Filter tickers update load page
filtered_tickers = fundamentals_filter_df['ticker'].dropna().unique().tolist()
update_loading_page(driver, f"Done - {len(filtered_tickers)} stocks passed Fundamental filter")
time.sleep(1)

#####################################################################################################################
