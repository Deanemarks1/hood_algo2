
def run_fetch_google_news(ticker_list, period): 
	ticker_list = ticker_list



	all_stocks_df = pd.read_csv("robinhood_universe.csv")


	ticker_to_name = dict(zip(
		all_stocks_df['symbol'],
		all_stocks_df['simple_name']
	))

	co_name_list = [ticker_to_name.get(t) for t in stock_universe_list]

	#co_name_list = df_input['co_name'].to_list()


	
	print(f"\n\n🧲 Fetching {len(ticker_list)} Google News RRS..")


	df_list = []

	#################################################
	# LOOP THROUGH TICKERS
	#################################################

	Y = 0
	total = len(ticker_list)
	
	while Y < total:
	
		ticker = ticker_list[Y]
		co_name = co_name_list[Y]
	
		try:
			df = fetch_google_news(ticker,co_name,  period)
	
			if df is not None and not df.empty:
				df_list.append(df)
	
		except Exception:
			pass
	
		# 🔎 Print every 5
		if (Y + 1) % 5 == 0 or (Y + 1) == total:
			print(f"🔄 {Y + 1} of {total}")
	
		time.sleep(.5)
		Y += 1

	#################################################
	# COMBINE DATAFRAMES
	#################################################

	if len(df_list) == 0:
		print("Finished — 0 inserted")
		return

	combined_df = pd.concat(df_list, ignore_index=True)


	#################################################
	# VERIFY REQUIRED COLUMNS EXIST
	#################################################

	required_cols = [
		'ticker',
		'published_utc',
		'headline',
		'google_link'
	]

	Y = 0
	while Y < len(required_cols):
		if required_cols[Y] not in combined_df.columns:
			print("Finished — 0 inserted")
			return
		Y += 1


	#################################################
	# ADD REQUIRED INSERT COLUMNS
	#################################################

	combined_df['article_scraped'] = 'no'
	combined_df['article_content'] = ''


	#################################################
	# PREPARE INSERT
	#################################################

	insert_query = """
	INSERT IGNORE INTO news
	(ticker, published_utc, headline, google_link, article_scraped)
	VALUES (%s, %s, %s, %s, %s)
	"""

	values = list(
		combined_df[
			[
				'ticker',
				'published_utc',
				'headline',
				'google_link',
				'article_scraped'
			]
		].itertuples(index=False, name=None)
	)

	if len(values) == 0:
		print("Finished — 0 inserted")
		return


	#################################################
	# EXECUTE INSERT
	#################################################

	run_sql(insert_query, values)

	print(f"Fetch Complete → 📥 {len(values)} new articles loaded into news table\n")

	return(combined_df)

