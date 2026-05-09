#################################
# CORE
#################################
import time
import random
import re
from datetime import datetime
from io import StringIO

#################################
# DATA
#################################
import pandas as pd
import numpy as np

#################################
# REQUESTS / API
#################################
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

#################################
# SELENIUM
#################################
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#################################
# PARSING
#################################
from bs4 import BeautifulSoup

session = requests.Session()



import requests as r



from bs4 import BeautifulSoup
import time
import random
import re






print('functions read in ')



def update_loading_page(driver, status_text):

    driver.execute_script("""
        var el = document.getElementById('status_text');

        if (el){

            var newText = arguments[0];  // ✅ capture BEFORE timeout

            el.style.opacity = 0;

            setTimeout(function(){

                el.innerText = newText;  // ✅ use stored value
                el.style.opacity = 1;

            }, 120);
        }
    """, status_text)
#Scrapers
##############################################################################################################




#Api Scrapers
#-------------------------------------------------------------------------
#extended_hours_fractional_tradability



def scrape_robinhood_crypto():
    
    
    import requests
    import pandas as pd
    
    session = requests.Session()
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })
    
    url = "https://nummus.robinhood.com/currency_pairs/"
    
    results = []
    next_url = url
    
    while next_url:
    
        r = session.get(next_url)
    
        if r.status_code != 200:
            print("BAD RESPONSE:", r.status_code)
            break
    
        data = r.json()
    
        Y = 0
        while Y < len(data['results']):
            results.append(data['results'][Y])
            Y += 1
    
        next_url = data['next']
    
    df_crypto = pd.DataFrame(results)
    
    
    
    df_crypto['base_code'] = df_crypto['asset_currency'].apply(lambda x: x.get('code') if isinstance(x, dict) else None)
    df_crypto['base_name'] = df_crypto['asset_currency'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
    
    
    crypto_list = []
    
    Y = 0
    while Y < len(df_crypto):
    
        try:
            tradable = df_crypto.iloc[Y]['tradability']
            display_only = df_crypto.iloc[Y]['display_only']
            symbol = df_crypto.iloc[Y]['symbol']
    
            if tradable == 'tradable' and display_only == False:
                crypto_list.append(symbol)
    
        except:
            pass
    
        Y += 1




    return df_crypto, crypto_list






def scrape_robinhood_universe(num_workers):

	import requests
	import pandas as pd
	from concurrent.futures import ThreadPoolExecutor

	base_url = "https://api.robinhood.com/instruments/?state=active&tradability=tradable&type=stock"

	session = requests.Session()

	all_data = []

	def fetch(url):
		try:
			res = session.get(url, timeout=10).json()
			return res
		except:
			return None

	url = base_url

	with ThreadPoolExecutor(max_workers=num_workers) as executor:

		futures = []

		while url:
			futures.append(executor.submit(fetch, url))

			# ⚠️ get next url WITHOUT waiting for thread
			try:
				res = session.get(url, timeout=10).json()
				url = res["next"]
			except:
				url = None

		for f in futures:
			res = f.result()
			if res and "results" in res:
				all_data.extend(res["results"])

	df = pd.DataFrame(all_data)

	df.to_csv('robinhood_universe.csv', index=False)

	return #df







def build_robinhood_universe(csv_path="robinhood_universe.csv"):

	"""
	Builds filtered stock + ETF universes from Robinhood data
	Returns:
		stock_universe_df, etf_universe_df
	"""

	# =========================
	# LOAD BASE FILE
	# =========================
	df = pd.read_csv(csv_path)


	# =========================
	# STOCKS (FRACTIONAL ONLY)
	# =========================
	df_stocks = df[
		(df["state"] == "active") &
		(df["tradability"] == "tradable") &
		(df["type"] == "stock") &
		(df["fractional_tradability"] == "tradable")
	].copy()


	# =========================
	# ETFS (FRACTIONAL ONLY)
	# =========================
	df_etf = df[
		(df["state"] == "active") &
		(df["tradability"] == "tradable") &
		(df["type"] == "etp") &
		(df["tax_security_type"] == "etf") &
		(df["fractional_tradability"] == "tradable")
	].copy()


	return df_stocks, df_etf

#-------------------------------------------------------------------------







#selenium scrapers
#-------------------------------------------------------------------------

def scrape_trading_view(driver):
	
	
	
	#driver = create_browser(headless=False, load_strategy="none")
	#driver = create_browser(headless=headless, load_strategy="none")
	
	
	
	
	
	# ------------------------------------------------------------
	# OPEN PAGE
	# ------------------------------------------------------------
	url = "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"
	driver.get(url)
	
	# Overlay (your branding)
	with open('templates/powered_by.py') as f:
		exec(f.read())

	
	
	
	time.sleep(2)
	
	
	
	
	soup = BeautifulSoup(driver.page_source, "html.parser")
	
	# ------------------------------------------------------------
	# EXTRACT TABLE
	# ------------------------------------------------------------
	#tables = pd.read_html(str(soup))
	tables = pd.read_html(StringIO(str(soup)))
	if len(tables) == 0:
		raise ValueError("No tables found on  page.")
	
	
	df = tables[1]
	
	
	
	
	
	
	
	
	############################################################
	# FULL CLEAN + RENAME + ORDERED OUTPUT
	############################################################
	

	
	# ----------------------------------------------------------
	# Normalize column names
	# ----------------------------------------------------------
	
	if isinstance(df.columns, pd.MultiIndex):
		df.columns = df.columns.get_level_values(0)
	
	df.columns = (
		df.columns
			.astype(str)
			.str.replace('\xa0', ' ', regex=False)
			.str.replace('\u202f', '', regex=False)
			.str.strip()
	)
	
	# ----------------------------------------------------------
	# Universal numeric cleaner
	# ----------------------------------------------------------
	
	def clean_numeric(x):
	
		if pd.isna(x):
			return np.nan
	
		x = str(x)
	
		x = (
			x.replace('−', '-')      # unicode minus
			 .replace('\xa0', '')
			 .replace('\u202f', '')
			 .replace(',', '')
			 .replace('USD', '')
			 .replace('%', '')
			 .strip()
		)
	
		if x in ['—', '-', '']:
			return np.nan
	
		multiplier = 1
		if x.endswith('M'):
			multiplier = 1_000_000
			x = x[:-1]
		elif x.endswith('B'):
			multiplier = 1_000_000_000
			x = x[:-1]
		elif x.endswith('K'):
			multiplier = 1_000
			x = x[:-1]
	
		try:
			return float(x) * multiplier
		except:
			return np.nan
	
	
	############################################################
	# BUILD CLEAN DF
	############################################################
	
	df_clean = pd.DataFrame()
	
	# --- Core required columns first ---
	
	# 🔥 FIXED PARSING (ONLY CHANGE)
	df_clean["ticker"] = df["Symbol"].str.extract(r'^([A-Z\.]+?)(?=[A-Z][a-z])')
	df_clean["co_name"] = df["Symbol"].str.replace(r'^([A-Z\.]+?)(?=[A-Z][a-z])', '', regex=True).str.strip()


	df_clean["Last"] = df["Price"].apply(clean_numeric)
	
	# If you actually have a raw Change column, use it.
	if "Change" in df.columns:
		df_clean["Chg"] = df["Change"].apply(clean_numeric)
	else:
		df_clean["Chg"] = np.nan
	
	df_clean["pct_chg"] = df["Change %"].apply(clean_numeric)
	
	df_clean["datetime"] = pd.Timestamp.utcnow()
	
	# --- Remaining cleaned fields ---
	
	df_clean["volume"] = df["Volume"].apply(clean_numeric)
	df_clean["rel_volume"] = df["Rel Volume"].apply(clean_numeric)
	df_clean["market_cap"] = df["Market cap"].apply(clean_numeric)
	df_clean["pe"] = df["P/E"].apply(clean_numeric)
	df_clean["eps"] = df["EPS dilTTM"].apply(clean_numeric)
	df_clean["eps_growth_pct"] = df["EPS dil growthTTM YoY"].apply(clean_numeric)
	df_clean["div_yield_pct"] = df["Div yield %TTM"].apply(clean_numeric)
	
	df_clean["sector"] = df["Sector"]
	df_clean["analyst_rating"] = df["Analyst Rating"]
	
	############################################################
	# FINAL COLUMN ORDER
	############################################################
	
	df_clean = df_clean[
		[
			"ticker",
			"co_name",
			"Last",
			"Chg",
			"pct_chg",
			"datetime",
			"volume",
			"rel_volume",
			"market_cap",
			"pe",
			"eps",
			"eps_growth_pct",
			"div_yield_pct",
			"sector",
			"analyst_rating"
		]
	]
	
	
	
	
	
	############################################################
	# PREP FOR SAFE MYSQL INSERT
	############################################################
	
	# Remove timezone
	df_clean["datetime"] = pd.to_datetime(df_clean["datetime"]).dt.tz_localize(None)
	
	# Add scrape_time (current timestamp)
	df_clean["scrape_time"] = pd.Timestamp.now()
	
	# Convert everything to plain Python objects
	df_clean = df_clean.astype(object)
	
	# Force np.nan -> None
	df_clean = df_clean.where(pd.notnull(df_clean), None)
	
	
	############################################################
	# SAFE PARAMETERIZED INSERT
	############################################################
	
	insert_query = """
	INSERT INTO scraper__trading_view
	(
		ticker,
		co_name,
		Last,
		Chg,
		pct_chg,
		datetime,
		volume,
		rel_volume,
		market_cap,
		pe,
		eps,
		eps_growth_pct,
		div_yield_pct,
		sector,
		analyst_rating,
		scrape_time
	)
	VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
	"""
	
	values = [tuple(row) for row in df_clean.to_numpy()]
	
	run_sql(insert_query, values)
	
	print("🤖⛏️ Bot Scraped trading_view ")
	
	
	#driver.quit()



	return df_clean



def scrape_wsj(driver):

	
	
	#driver = create_browser(headless=False, load_strategy="none")
	#driver = create_browser(headless=headless, load_strategy="none")
	
	
	
	
	# ------------------------------------------------------------
	# OPEN PAGE
	# ------------------------------------------------------------
	url = "https://www.wsj.com/market-data/stocks/us/movers"
	driver.get(url)
	

	# Overlay (your branding)
	with open('templates/powered_by.py') as f:
		exec(f.read())




	# Wait until main content table section loads
	wait = WebDriverWait(driver, 15, poll_frequency=1, ignored_exceptions=[TimeoutException, NoSuchElementException])
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
	
	
	# Parse page
	soup = BeautifulSoup(driver.page_source, "html.parser")
	
	# ------------------------------------------------------------
	# EXTRACT TABLE
	# ------------------------------------------------------------
	#tables = pd.read_html(str(soup))
	tables = pd.read_html(StringIO(str(soup)))
	
	
	if len(tables) == 0:
		raise ValueError("No tables found on WSJ movers page.")
	
	df = tables[0]
	
	# ------------------------------------------------------------
	# CLEAN & PARSE
	# ------------------------------------------------------------
	
	# Clean company names
	co_name_list = df["Unnamed: 0"].to_list()
	
	Y = 0
	while Y < len(co_name_list):
		name = co_name_list[Y].split("(")[0].rstrip()
		if name.endswith("."):
			name = name[:-1]
		co_name_list[Y] = name
		Y += 1
	
	
	# Parse tickers
	ticker_list = []
	
	Y = 0
	raw_list = df["Unnamed: 0"].to_list()
	
	while Y < len(raw_list):
		parts = raw_list[Y].split("(")
		if len(parts) > 1:
			ticker = parts[-1].replace(")", "")
		else:
			ticker = "N/A"
		ticker_list.append(ticker)
		Y += 1
	
	
	# Numeric conversions
	df["Last"] = pd.to_numeric(df["Last"], errors="coerce")
	df["Chg"] = pd.to_numeric(df["Chg"], errors="coerce")
	df["% Chg"] = pd.to_numeric(df["% Chg"], errors="coerce")
	
	df = df.rename(columns={"% Chg": "pct_chg"})
	
	# ------------------------------------------------------------
	# BUILD FINAL DATAFRAME
	# ------------------------------------------------------------
	
	final_df = pd.DataFrame()
	
	final_df["ticker"] = ticker_list
	final_df["co_name"] = co_name_list
	final_df["Last"] = df["Last"]
	final_df["Chg"] = df["Chg"]
	final_df["pct_chg"] = df["pct_chg"]
	
	# ------------------------------------------------------------
	# ADD TIME
	# ------------------------------------------------------------
	
	current_time = datetime.now()
	final_df["datetime"] = datetime.now()
	# ------------------------------------------------------------
	# OUTPUT
	# ------------------------------------------------------------
	
	
	
	
	
	insert_query = """
	
	
	INSERT INTO scraper__wsj_gainers
	(ticker, co_name, Last, Chg, pct_chg, datetime)
	VALUES (%s, %s, %s, %s, %s, %s)
	"""
	
	values = list(final_df.itertuples(index=False, name=None))
	
	run_sql(insert_query, values)
	
	print('🤖⛏️ Bot Scraped wsj')
	print('')
	
	
	#driver.quit()
	
	


	return final_df


def scrape_stocktwitts_trending(driver):


	#driver = create_driver_profile_1(headless=headless)



	df_list = []

	url_list = [
		'https://stocktwits.com/sentiment/trending',
		'https://stocktwits.com/sentiment/most-active',
		'https://stocktwits.com/sentiment/watchers',
		'https://stocktwits.com/sentiment/most-bullish',
		'https://stocktwits.com/sentiment/top-gainers'
	]


	#################################
	# NUMBER CONVERTER
	#################################
	def convert_to_number(val):

		if val in [None, "", "---"]:
			return np.nan

		val = str(val).strip()
		val = val.replace("$", "").replace(",", "").replace("%", "")

		multiplier = 1

		if val.endswith("K"):
			multiplier = 1_000
			val = val[:-1]

		elif val.endswith("M"):
			multiplier = 1_000_000
			val = val[:-1]

		elif val.endswith("B"):
			multiplier = 1_000_000_000
			val = val[:-1]

		elif val.endswith("T"):
			multiplier = 1_000_000_000_000
			val = val[:-1]

		try:
			return float(val) * multiplier
		except:
			return np.nan


	#################################
	# MAIN LOOP
	#################################

	Y = 0
	while Y < len(url_list):

		driver.get(url_list[Y])


		# Overlay (your branding)
		with open('templates/powered_by.py') as f:
			exec(f.read())




		WebDriverWait(driver, 10).until(
			EC.presence_of_all_elements_located(
				(By.CLASS_NAME, "TickerTable_bodyCell__SZDgb")
			)
		)

		soup = BeautifulSoup(driver.page_source, "html.parser")

		cells = soup.select('div[class*="TickerTable_bodyCell__SZDgb"]')


		#################################
		# CLEAN RAW TEXT
		#################################
		data = []

		i = 0
		while i < len(cells):

			text = cells[i].text.strip()

			if text != "" and "Upgrade to Edge" not in text:
				data.append(text)

			i += 1


		#################################
		# BUILD ROWS
		#################################
		rows = []
		row = []

		i = 0
		while i < len(data):

			val = data[i]

			if val.isdigit():

				if len(row) >= 7:
					rows.append(row)

				row = [val]

			else:
				row.append(val)

			i += 1

		if len(row) >= 7:
			rows.append(row)


		#################################
		# NORMALIZE
		#################################
		clean_rows = []

		i = 0
		while i < len(rows):

			r = rows[i]

			if len(r) >= 8:
				clean_rows.append(r[:8])

			i += 1


		df = pd.DataFrame(clean_rows, columns=[
			"rank",
			"name",
			"price",
			"change",
			"volume",
			"high_52w",
			"low_52w",
			"market_cap"
		])


		#################################
		# FIX TICKER + COMPANY
		#################################
		ticker_list = []
		company_list = []

		i = 0
		while i < len(df):

			text = str(df.loc[i, "name"])

			match = re.match(r"^([A-Z]{1,5})", text)

			if match:
				ticker = match.group(1)
				company = text[len(ticker):].strip()
			else:
				ticker = None
				company = text

			ticker_list.append(ticker)
			company_list.append(company)

			i += 1


		df["ticker"] = ticker_list
		df["company"] = company_list
		df = df.drop(columns=["name"])


		#################################
		# CLEAN NUMBERS
		#################################
		cols = ["price", "change", "volume", "high_52w", "low_52w", "market_cap"]

		i = 0
		while i < len(cols):

			df[cols[i]] = df[cols[i]].apply(convert_to_number)

			i += 1


		#################################
		# SOURCE
		#################################
		df["source"] = url_list[Y]
		df["source_clean"] = df["source"].apply(lambda x: x.split("/")[-1])


		#################################
		# TYPE FIX
		#################################
		df["rank"] = pd.to_numeric(df["rank"], errors="coerce")


		df_list.append(df)

		Y += 1


	#################################
	# FINAL DF
	#################################
	final_df = pd.concat(df_list, ignore_index=True)


	#################################
	# BULK INSERT
	#################################
	values_list = []

	Y = 0
	while Y < len(final_df):

		row = final_df.iloc[Y]

		values_list.append(f"""(
			{str(row["rank"]).replace("nan","NULL")},
			{str(row["price"]).replace("nan","NULL")},
			{str(row["change"]).replace("nan","NULL")},

			{str(row["volume"]).replace("nan","NULL")},
			{str(row["high_52w"]).replace("nan","NULL")},
			{str(row["low_52w"]).replace("nan","NULL")},
			{str(row["market_cap"]).replace("nan","NULL")},

			'{str(row["ticker"])}',
			'{str(row["company"]).replace("'", "''")}',

			'{str(row["source"])}',
			'{str(row["source_clean"])}'
		)""")

		Y += 1


	values_sql = ",\n".join(values_list)


	run_sql(f"""
	INSERT INTO scraper__stock_twitts_trending (
		rank_num,
		price,
		chg,
		volume,
		high_52w,
		low_52w,
		market_cap,
		ticker,
		company,
		source,
		source_clean
	)
	VALUES
	{values_sql};
	""")


	print('🤖⛏️ Bot Scraped stocktwits trending')

	#driver.quit()

	return final_df

#-------------------------------------------------------------------------



#############################################################################################################







































#Fetchers
##############################################################################################################






def fetch_robinhood_fundamentals(ticker_list, chunk_size):

	print('scraping robinhood fundamentals')

	if not ticker_list:
		return pd.DataFrame()

	########################################################
	# CLEAN TICKER LIST
	########################################################

	clean_list = []
	Y = 0
	while Y < len(ticker_list):

		val = ticker_list[Y]

		if pd.notna(val):
			val = str(val).strip().upper()
			if val != "":
				clean_list.append(val)

		Y += 1

	if len(clean_list) == 0:
		return pd.DataFrame()

	print(f'🧲 Fetching {len(clean_list)} fundamentals')

	########################################################
	# API SETUP
	########################################################

	session = requests.Session()

	df_list = []
	snapshot_time = datetime.now()

	########################################################
	# LOOP THROUGH CHUNKS
	########################################################

	Y = 0
	while Y < len(clean_list):

		chunk = clean_list[Y:Y+chunk_size]

		if len(chunk) == 0:
			Y += chunk_size
			continue

		symbols = ",".join(chunk)

		url = "https://api.robinhood.com/fundamentals/"
		params = {"symbols": symbols}

		try:
			res = session.get(url, params=params, timeout=10)
			res.raise_for_status()
			json_data = res.json()
		except Exception as e:
			print(f"❌ request failed: {e}")
			Y += chunk_size
			continue

		if "results" not in json_data:
			Y += chunk_size
			continue

		data = json_data["results"]

		rows = []

		Z = 0
		while Z < len(data):

			fund = data[Z]

			if fund is not None:

				ticker_val = fund.get("symbol")

				if ticker_val is None:
					if Z < len(chunk):
						ticker_val = chunk[Z]
					else:
						ticker_val = None

				rows.append({

					"ticker": ticker_val,

					"time": snapshot_time,
					"scraped_at": snapshot_time,

					"open": fund.get("open"),
					"high": fund.get("high"),
					"low": fund.get("low"),
					"volume": fund.get("volume"),

					"average_volume_2_weeks": fund.get("average_volume_2_weeks"),
					"average_volume": fund.get("average_volume"),
					"average_volume_30_days": fund.get("average_volume_30_days"),

					"high_52_weeks": fund.get("high_52_weeks"),
					"high_52_weeks_date": fund.get("high_52_weeks_date"),

					"low_52_weeks": fund.get("low_52_weeks"),
					"low_52_weeks_date": fund.get("low_52_weeks_date"),

					"dividend_yield": fund.get("dividend_yield"),
					"shares_float": fund.get("float"),
					"market_cap": fund.get("market_cap"),
					"pb_ratio": fund.get("pb_ratio"),
					"pe_ratio": fund.get("pe_ratio"),
					"shares_outstanding": fund.get("shares_outstanding"),

					"industry": fund.get("industry"),
					"num_employees": fund.get("num_employees"),
					"year_founded": fund.get("year_founded"),

					"payable_date": fund.get("payable_date"),
					"ex_dividend_date": fund.get("ex_dividend_date")
				})

			Z += 1

		if len(rows) > 0:
			df_chunk = pd.DataFrame(rows)
			df_list.append(df_chunk)

		time.sleep(0.2)
		Y += chunk_size

	if len(df_list) == 0:
		return pd.DataFrame()

	########################################################
	# COMBINE + ORDER
	########################################################

	df = pd.concat(df_list, ignore_index=True)

	# 🔥 PROTECT AGAINST DUPLICATE COLUMNS
	df = df.loc[:, ~df.columns.duplicated()]

	order_map = {}
	Y = 0
	while Y < len(clean_list):
		order_map[clean_list[Y]] = Y
		Y += 1

	df["order"] = df["ticker"].map(order_map)
	df = df.sort_values("order").drop(columns="order").reset_index(drop=True)

	########################################################
	# NUMERIC CONVERSION
	########################################################

	numeric_cols = [
		"open","high","low","volume",
		"average_volume_2_weeks","average_volume","average_volume_30_days",
		"high_52_weeks","low_52_weeks",
		"dividend_yield","shares_float","market_cap",
		"pb_ratio","pe_ratio","shares_outstanding",
		"num_employees","year_founded"
	]

	Y = 0
	while Y < len(numeric_cols):
		if numeric_cols[Y] in df.columns:
			df[numeric_cols[Y]] = pd.to_numeric(df[numeric_cols[Y]], errors="coerce")
		Y += 1

	########################################################
	# DATE CONVERSION
	########################################################

	date_cols = [
		"high_52_weeks_date",
		"low_52_weeks_date",
		"payable_date",
		"ex_dividend_date"
	]

	Y = 0
	while Y < len(date_cols):
		if date_cols[Y] in df.columns:
			df[date_cols[Y]] = pd.to_datetime(df[date_cols[Y]], errors="coerce")
		Y += 1

	df = df.replace({np.nan: None})

	print(f"✅ done: {len(df)} rows")

	############################################
	# HELPERS (🔥 FIXED)
	############################################

	def safe_scalar(val):
		try:
			if isinstance(val, (pd.Series, list, np.ndarray)):
				val = val.iloc[0] if hasattr(val, "iloc") else val[0]
		except:
			pass
		return val

	def sql_val(val):

		val = safe_scalar(val)

		try:
			if pd.isna(val):
				return "NULL"
		except:
			return "NULL"

		return str(val)

	def sql_str(val):

		val = safe_scalar(val)

		try:
			if pd.isna(val):
				return "NULL"
		except:
			return "NULL"

		safe_val = str(val).replace("'", "''")
		return f"'{safe_val}'"

	############################################
	# BUILD VALUES
	############################################

	values_list = []

	Y = 0
	while Y < len(df):

		row = df.iloc[Y]

		values_list.append(f"""(
			{sql_str(row["ticker"])},

			{sql_str(row["time"])},
			{sql_str(row["scraped_at"])},

			{sql_val(row["open"])},
			{sql_val(row["high"])},
			{sql_val(row["low"])},

			{sql_val(row["volume"])},
			{sql_val(row["average_volume_2_weeks"])},
			{sql_val(row["average_volume"])},

			{sql_val(row["average_volume_30_days"])},

			{sql_val(row["high_52_weeks"])},
			{sql_str(row["high_52_weeks_date"])},
			{sql_val(row["low_52_weeks"])},
			{sql_str(row["low_52_weeks_date"])},

			{sql_val(row["dividend_yield"])},

			{sql_val(row["shares_float"])},
			{sql_val(row["market_cap"])},
			{sql_val(row["pb_ratio"])},
			{sql_val(row["pe_ratio"])},
			{sql_val(row["shares_outstanding"])},

			{sql_str(row["industry"])},
			{sql_val(row["num_employees"])},
			{sql_val(row["year_founded"])},

			{sql_str(row["payable_date"])},
			{sql_str(row["ex_dividend_date"])}

		)""")

		Y += 1

	############################################
	# COMBINE VALUES
	############################################

	values_sql = ",\n".join(values_list)

	############################################
	# EXECUTE INSERT
	############################################

	run_sql(f"""
	INSERT INTO robinhood_fundamentals (
		ticker,
		time,
		scraped_at,
		open,
		high,
		low,
		volume,
		average_volume_2_weeks,
		average_volume,
		average_volume_30_days,
		high_52_weeks,
		high_52_weeks_date,
		low_52_weeks,
		low_52_weeks_date,
		dividend_yield,
		shares_float,
		market_cap,
		pb_ratio,
		pe_ratio,
		shares_outstanding,
		industry,
		num_employees,
		year_founded,
		payable_date,
		ex_dividend_date
	)
	VALUES
	{values_sql};
	""")

	return df









def fetch_robinhood_prices(ticker_list, chunk_size):

	import pandas as pd
	import time
	import requests

	print('scraping robinhood prices')

	if not ticker_list:
		print("No tickers provided")
		return pd.DataFrame()

	# 🔥 MISSING BEFORE (fix)
	session = requests.Session()

	df_list = []

	Y = 0
	while Y < len(ticker_list):

		chunk = ticker_list[Y:Y+chunk_size]

		# -------------------------
		# CLEAN THE CHUNK
		# -------------------------
		clean_chunk = []
		X = 0
		while X < len(chunk):

			val = chunk[X]

			if pd.notna(val):
				val_str = str(val).strip().upper()

				if val_str != "" and val_str != "NAN":
					clean_chunk.append(val_str)

			X += 1

		# skip if nothing valid
		if not clean_chunk:
			Y += chunk_size
			continue





		symbols = ",".join(clean_chunk)

		url = "https://api.robinhood.com/quotes/"
		params = {"symbols": symbols}

		try:
			r = session.get(url, params=params, timeout=10)
			r.raise_for_status()
		except Exception as e:
			print("Request failed:", e)
			Y += chunk_size
			continue

		json_data = r.json()

		if "results" not in json_data:
			Y += chunk_size
			continue

		data = json_data["results"]

		rows = []

		# 🔥 SINGLE TIMESTAMP FOR THIS BATCH
		current_time = pd.Timestamp.now().floor("s")

		Z = 0
		while Z < len(data):

			item = data[Z]

			if item is not None:

				last_price = item.get("last_trade_price")
				updated_at = item.get("updated_at")

				if last_price:

					# optional: keep market timestamp too
					market_time = None
					if updated_at:
						try:
							market_time = pd.to_datetime(updated_at, utc=True).tz_localize(None)
						except:
							market_time = None

					rows.append({
						"ticker": item.get("symbol"),
						"price": float(last_price),

						# ✅ YOUR REAL SCRAPE TIME
						"time": current_time,

						# ✅ OPTIONAL (keep if you want)
						"market_time": market_time
					})

			Z += 1

		if rows:
			df_chunk = pd.DataFrame(rows)
			df_list.append(df_chunk)

		time.sleep(0.2)
		Y += chunk_size

	if not df_list:
		print("No valid price data returned")
		return pd.DataFrame()

	df = pd.concat(df_list, ignore_index=True)

	# -------------------------
	# FIX ORDER (MATCH INPUT)
	# -------------------------
	clean_master = []
	X = 0
	while X < len(ticker_list):

		val = ticker_list[X]

		if pd.notna(val):
			val_str = str(val).strip().upper()

			if val_str != "" and val_str != "NAN":
				clean_master.append(val_str)

		X += 1

	order_map = {}
	X = 0
	while X < len(clean_master):
		order_map[clean_master[X]] = X
		X += 1

	df["order"] = df["ticker"].map(order_map)
	df = df.sort_values("order").drop(columns="order").reset_index(drop=True)

	print(f"Finished. {len(df)} prices retrieved.")

	############################################
	# Helpers
	############################################

	def sql_val(val):
		if pd.isna(val):
			return "NULL"
		return str(val)

	def sql_str(val):
		if pd.isna(val):
			return "NULL"
		safe_val = str(val).replace("'", "''")
		return f"'{safe_val}'"

	############################################
	# BUILD VALUES
	############################################

	values_list = []

	Y = 0
	while Y < len(df):

		row = df.iloc[Y]

		values_list.append(f"""(
			{sql_str(row["ticker"])},
			{sql_val(row["price"])},
			{sql_str(row["time"])},
			{sql_str(row["market_time"])}
		)""")

		Y += 1

	############################################
	# COMBINE
	############################################

	values_sql = ",\n".join(values_list)

	############################################
	# INSERT
	############################################

	run_sql(f"""
	INSERT INTO robinhood_prices (
		ticker,
		price,
		time,
		market_time
	)
	VALUES
	{values_sql};
	""")

	return df



def fetch_robinhood_quotes(ticker_list, chunk_size):

	print("fetching robinhood quotes")

	if not ticker_list:
		print("No tickers provided")
		return pd.DataFrame()

	# 🔥 session (important)
	session = requests.Session()

	headers = {
		"User-Agent": "Mozilla/5.0",
		"Accept": "application/json"
	}

	session.headers.update(headers)

	all_results = []

	Y = 0
	while Y < len(ticker_list):

		chunk = ticker_list[Y:Y + chunk_size]

		# force string
		safe_chunk = []
		X = 0
		while X < len(chunk):

			try:
				val = str(chunk[X]).strip().upper()
				if val != "":
					safe_chunk.append(val)
			except:
				pass

			X += 1

		if not safe_chunk:
			Y += chunk_size
			continue

		symbols = ",".join(safe_chunk)
		url = f"https://api.robinhood.com/quotes/?symbols={symbols}"

		try:
			resp = session.get(url, timeout=10)

			# ❌ bad status
			if resp.status_code != 200:
				print(f"Bad status {resp.status_code} on chunk {chunk}")
				Y += chunk_size
				continue

			# ❌ bad json
			try:
				response = resp.json()
			except:
				print(f"JSON decode failed on chunk {chunk}")
				Y += chunk_size
				continue

			# ❌ not dict
			if not isinstance(response, dict):
				print(f"Non-dict response on chunk {chunk}")
				Y += chunk_size
				continue

			results = response.get('results', [])

			if results:
				all_results.extend(results)

		except Exception as e:
			print(f"error on chunk {chunk}: {e}")

		Y += chunk_size


	# ---------- clean None ----------
	clean_results = []
	X = 0
	while X < len(all_results):

		if all_results[X] is not None:
			clean_results.append(all_results[X])

		X += 1


	df = pd.DataFrame(clean_results)

	if df.empty:
		print("No data returned")
		return df


	# ---------- numeric ----------
	float_cols = [
		'last_trade_price',
		'bid_price',
		'ask_price',
		'previous_close'
	]

	Y = 0
	while Y < len(float_cols):

		col = float_cols[Y]

		if col in df.columns:
			df[col] = pd.to_numeric(df[col], errors='coerce')

		Y += 1


	# ---------- derived ----------
	if 'ask_price' in df.columns and 'bid_price' in df.columns:
		df['spread'] = df['ask_price'] - df['bid_price']
		df['mid_price'] = (df['bid_price'] + df['ask_price']) / 2

	if 'last_trade_price' in df.columns and 'previous_close' in df.columns:
		df['pct_change'] = (
			(df['last_trade_price'] - df['previous_close']) /
			df['previous_close']
		)


	# ---------- timestamps ----------
	if 'updated_at' in df.columns:
		df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')


	# ---------- column order ----------
	keep_cols = [
		'symbol',
		'last_trade_price',
		'bid_price',
		'ask_price',
		'bid_size',
		'ask_size',
		'mid_price',
		'spread',
		'pct_change',
		'previous_close',
		'last_extended_hours_trade_price',
		'updated_at'
	]

	existing_cols = []
	X = 0
	while X < len(keep_cols):

		if keep_cols[X] in df.columns:
			existing_cols.append(keep_cols[X])

		X += 1

	df = df[existing_cols]

	print(f"Finished. {len(df)} rows")


	############################################
	# Helpers
	############################################

	def sql_val(val):
		if pd.isna(val):
			return "NULL"
		return str(val)

	def sql_str(val):
		if pd.isna(val):
			return "NULL"
		safe_val = str(val).replace("'", "''")
		return f"'{safe_val}'"


	############################################
	# BUILD VALUES
	############################################

	values_list = []

	Y = 0
	while Y < len(df):

		row = df.iloc[Y]

		values_list.append(f"""(
			{sql_str(row["symbol"])},

			{sql_val(row["last_trade_price"])},
			{sql_val(row["bid_price"])},
			{sql_val(row["ask_price"])},

			{sql_val(row["bid_size"])},
			{sql_val(row["ask_size"])},

			{sql_val(row["mid_price"])},
			{sql_val(row["spread"])},

			{sql_val(row["pct_change"])},

			{sql_val(row["previous_close"])},
			{sql_val(row["last_extended_hours_trade_price"])},

			{sql_str(row["updated_at"])},

			{sql_str(pd.Timestamp.now().floor("s"))}
		)""")

		Y += 1


	############################################
	# COMBINE
	############################################

	values_sql = ",\n".join(values_list)


	############################################
	# INSERT
	############################################

	run_sql(f"""
	INSERT INTO robinhood_quotes (
		symbol,
		last_trade_price,
		bid_price,
		ask_price,
		bid_size,
		ask_size,
		mid_price,
		spread,
		pct_change,
		previous_close,
		last_extended_hours_trade_price,
		updated_at,
		time
	)
	VALUES
	{values_sql};
	""")

	return df




def fetch_robinhood_historicals(ticker_list, interval="5minute", span="week",chunk_size=50):



	#################################################
	# ✅ VALIDATE INPUTS (IMPORTANT)
	#################################################

	valid_intervals = ["5minute", "10minute", "hour", "day"]
	valid_spans = ["day", "week", "month", "year", "5year"]

	if interval not in valid_intervals:
		print(f"Invalid interval: {interval}")
		return pd.DataFrame()

	if span not in valid_spans:
		print(f"Invalid span: {span}")
		return pd.DataFrame()

	print(f"fetching historicals → interval={interval} span={span}")

	if not ticker_list:
		print("No tickers provided")
		return pd.DataFrame()

	all_results = []

	#################################################
	# LOOP CHUNKS
	#################################################

	Y = 0
	while Y < len(ticker_list):

		chunk = ticker_list[Y:Y + chunk_size]

		safe_chunk = []
		X = 0
		while X < len(chunk):
			try:
				safe_chunk.append(str(chunk[X]))
			except:
				pass
			X += 1

		symbols = ",".join(safe_chunk)

		url = f"https://api.robinhood.com/quotes/historicals/?symbols={symbols}&interval={interval}&span={span}"

		try:
			response = r.get(url, timeout=10).json()

			if "results" not in response:
				Y += chunk_size
				continue

			results = response["results"]

			X = 0
			while X < len(results):

				symbol_data = results[X]

				if symbol_data is None:
					X += 1
					continue

				ticker = symbol_data.get("symbol")
				historicals = symbol_data.get("historicals", [])

				if not historicals:
					X += 1
					continue

				df = pd.DataFrame(historicals)

				numeric_cols = [
					'open_price',
					'close_price',
					'high_price',
					'low_price',
					'volume'
				]

				Z = 0
				while Z < len(numeric_cols):
					col = numeric_cols[Z]
					if col in df.columns:
						df[col] = pd.to_numeric(df[col], errors='coerce')
					Z += 1

				df['begins_at'] = pd.to_datetime(df['begins_at'], errors='coerce')

				try:
					df['time'] = df['begins_at'].dt.tz_convert('US/Eastern')
				except:
					df['time'] = df['begins_at']

				df = df.rename(columns={
					"open_price": "open",
					"close_price": "close",
					"high_price": "high",
					"low_price": "low"
				})

				df['pct_change'] = df['close'].pct_change() * 100
				df['body'] = df['close'] - df['open']
				df['range'] = df['high'] - df['low']

				df['vol_ma20'] = df['volume'].rolling(20).mean()
				df['volume_spike'] = df['volume'] / df['vol_ma20']

				df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

				df['ticker'] = ticker

				keep_cols = [
					'time','ticker','open','high','low','close','volume',
					'pct_change','body','range','volume_spike','vwap',
					'session','interpolated'
				]

				final_cols = []
				Z = 0
				while Z < len(keep_cols):
					if keep_cols[Z] in df.columns:
						final_cols.append(keep_cols[Z])
					Z += 1

				df = df[final_cols]

				all_results.append(df)

				X += 1

		except Exception as e:
			print(f"error on chunk {chunk}: {e}")

		Y += chunk_size

	if len(all_results) == 0:
		print("No data returned")
		return pd.DataFrame()

	combined_df = pd.concat(all_results, ignore_index=True)

	print(f"Finished. {len(combined_df)} rows")

	return combined_df






def fetch_robinhood_options(ticker_input):

	import requests
	import pandas as pd

	############################################################
	# SESSION (reuse)
	############################################################

	session = requests.Session()
	session.headers.update({
		"User-Agent": "Mozilla/5.0"
	})

	############################################################
	# 1️⃣ GET INSTRUMENT → CHAIN ID
	############################################################

	try:
		instrument_url = f"https://api.robinhood.com/instruments/?symbol={ticker_input}"

		r = session.get(instrument_url, timeout=10)
		r.raise_for_status()

		instrument_json = r.json()

		if "results" not in instrument_json or not instrument_json["results"]:
			print(f"No instrument found for {ticker_input}")
			return None

		instrument_df = pd.DataFrame(instrument_json["results"])

		chain_id = instrument_df["tradable_chain_id"].iloc[0]

	except Exception:
		print(f"Failed to get chain_id for {ticker_input}")
		return None


	############################################################
	# 2️⃣ GET OPTIONS (HANDLE PAGINATION 🔥)
	############################################################

	try:
		options_url = f"https://api.robinhood.com/options/instruments/?chain_id={chain_id}"

		all_results = []

		while options_url:

			r2 = session.get(options_url, timeout=10)

			if r2.status_code != 200:
				print(f"{ticker_input} → options endpoint failed")
				return None

			data = r2.json()

			if "results" in data:
				all_results.extend(data["results"])

			options_url = data.get("next")  # 🔥 pagination

		if len(all_results) == 0:
			print(f"{ticker_input} → no options returned")
			return None

		options_df = pd.DataFrame(all_results)

	except Exception:
		print(f"{ticker_input} → error pulling options")
		return None


	############################################################
	# 3️⃣ CLEAN + SORT
	############################################################

	if "expiration_date" in options_df.columns:

		options_df["expiration_date"] = pd.to_datetime(
			options_df["expiration_date"],
			errors="coerce"
		)

		options_df = options_df.sort_values(
			by="expiration_date",
			ascending=True
		).reset_index(drop=True)

	options_df["ticker"] = ticker_input


	############################################################
	# RETURN
	############################################################

	return options_df




























#FETCH GOOGLE NEWS 
#----------------------------------------------------------------------------------------------


#----------API-VERSION------------#

def fetch_google_news(ticker, co_name, time_window="1d"):

	import requests
	import pandas as pd
	import time
	import random

	# --------------------------------------------------------
	# CLEAN INPUTS
	# --------------------------------------------------------
	ticker = str(ticker).strip().upper()
	co_name = str(co_name).strip()

	if ticker == "":
		return pd.DataFrame()

	# --------------------------------------------------------
	# BUILD URL
	# --------------------------------------------------------
	url = (
		f"https://news.google.com/rss/search?"
		f"q={ticker}+stock+{co_name}+when:{time_window}"
	)

	headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
		"Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"
	}

	# --------------------------------------------------------
	# RETRY LOGIC
	# --------------------------------------------------------
	attempts = 0
	max_attempts = 3

	while attempts < max_attempts:

		try:
			r = requests.get(url, headers=headers, timeout=10)

			# ----------------------------------------------
			# STATUS CHECK
			# ----------------------------------------------
			if r.status_code != 200:
				attempts += 1
				time.sleep(random.uniform(1, 3))
				continue

			# ----------------------------------------------
			# BLOCK DETECTION (Google anti-bot)
			# ----------------------------------------------
			if "Sorry" in r.text or "<html" in r.text.lower():
				attempts += 1
				time.sleep(random.uniform(2, 5))
				continue

			break

		except Exception:
			attempts += 1
			time.sleep(random.uniform(1, 3))

	# --------------------------------------------------------
	# FAILED AFTER RETRIES
	# --------------------------------------------------------
	if attempts == max_attempts:
		return pd.DataFrame()

	# --------------------------------------------------------
	# SAFE XML PARSE
	# --------------------------------------------------------
	try:
		df = pd.read_xml(r.content, xpath="//item")
	except Exception:
		return pd.DataFrame()

	if df is None or df.empty:
		return pd.DataFrame()

	# --------------------------------------------------------
	# CLEAN / RENAME
	# --------------------------------------------------------
	df = df.rename(columns={
		"title": "headline",
		"link": "google_link",
		"pubDate": "published_utc"
	})

	# --------------------------------------------------------
	# SAFE DATETIME PARSE (CRITICAL)
	# --------------------------------------------------------
	df["published_utc"] = pd.to_datetime(
		df["published_utc"],
		errors="coerce",
		utc=True
	)

	df["ticker"] = ticker

	# --------------------------------------------------------
	# EXTRACT PUBLISHER
	# --------------------------------------------------------
	if "source" in df.columns:

		df["publisher_name"] = df["source"].apply(
			lambda x: x.get("title") if isinstance(x, dict) else None
		)

		df["publisher_url"] = df["source"].apply(
			lambda x: x.get("url") if isinstance(x, dict) else None
		)

	else:
		df["publisher_name"] = None
		df["publisher_url"] = None

	# fallback from title
	def extract_from_title(title):
		if isinstance(title, str) and " - " in title:
			return title.split(" - ")[-1]
		return None

	df["publisher_name"] = df["publisher_name"].fillna(
		df["headline"].apply(extract_from_title)
	)

	# --------------------------------------------------------
	# FINAL FORMAT
	# --------------------------------------------------------
	df = df[[
		"ticker",
		"published_utc",
		"headline",
		"publisher_name",
		"publisher_url",
		"google_link"
	]]

	return df



def run_fetch_google_news(ticker_list, period="1d", workers=2, hours_filter=6):

	import pandas as pd
	import time
	import random
	from concurrent.futures import ThreadPoolExecutor, as_completed

	print(f"\n🧲 Fetching {len(ticker_list)} Google News RSS...")

	# --------------------------------------------------------
	# LOAD UNIVERSE
	# --------------------------------------------------------
	all_stocks_df = pd.read_csv("robinhood_universe.csv")

	ticker_to_name = dict(zip(
		all_stocks_df['symbol'].astype(str).str.strip().str.upper(),
		all_stocks_df['simple_name'].astype(str)
	))

	df_list = []

	# --------------------------------------------------------
	# WORKER FUNCTION
	# --------------------------------------------------------
	def worker(ticker):

		if not ticker:
			return None

		ticker_clean = str(ticker).strip().upper()
		co_name = ticker_to_name.get(ticker_clean, "")

		time.sleep(random.uniform(0.2, 0.6))

		try:
			df = fetch_google_news(
				ticker=ticker_clean,
				co_name=co_name,
				time_window=period
			)

			if df is not None and not df.empty:
				return df

		except Exception:
			return None

		return None

	# --------------------------------------------------------
	# PARALLEL EXECUTION
	# --------------------------------------------------------
	with ThreadPoolExecutor(max_workers=workers) as executor:

		futures = [executor.submit(worker, t) for t in ticker_list]

		Y = 0
		total = len(futures)

		for future in as_completed(futures):

			result = future.result()

			if result is not None:
				df_list.append(result)

			Y += 1

			if Y % 50 == 0 or Y == total:
				update_loading_page(driver, f"Fetching Google News (API Version) {Y} / {total} ")
				print(f"🔄 {Y} / {total}")

	# --------------------------------------------------------
	# COMBINE RESULTS
	# --------------------------------------------------------
	if len(df_list) == 0:
		print("❌ Finished — 0 rows returned")
		return pd.DataFrame()

	combined_df = pd.concat(df_list, ignore_index=True)

	# --------------------------------------------------------
	# HARD CLEAN
	# --------------------------------------------------------
	combined_df = combined_df.fillna("")

	# --------------------------------------------------------
	# REMOVE DUPES
	# --------------------------------------------------------
	before_dedupe = len(combined_df)

	combined_df = combined_df.drop_duplicates(
		subset=["google_link"]
	).reset_index(drop=True)

	print(f"🧹 Deduped: {before_dedupe} → {len(combined_df)}")

	# --------------------------------------------------------
	# 🔥 HARD TIME FILTER (STRICT ENFORCEMENT)
	# --------------------------------------------------------
	combined_df["published_utc"] = pd.to_datetime(
		combined_df["published_utc"],
		errors="coerce",
		utc=True
	)

	now_utc = pd.Timestamp.utcnow()

	cutoff = now_utc - pd.Timedelta(hours=hours_filter)

	before_filter = len(combined_df)

	combined_df = combined_df[
		(combined_df["published_utc"].notna()) &
		(combined_df["published_utc"] <= now_utc) &   # no future junk
		(combined_df["published_utc"] >= cutoff)
	].reset_index(drop=True)

	after_filter = len(combined_df)

	print(f"🧹 Time Filter: {before_filter} → {after_filter}")
	print(f"🕒 Cutoff: {cutoff}")

	if len(combined_df) == 0:
		print("⚠️ No valid recent news after filtering")
		return pd.DataFrame()

	print(f"✅ Final rows: {len(combined_df)}")

	# --------------------------------------------------------
	# BUILD VALUES (SAFE INSERT)
	# --------------------------------------------------------
	values = []

	Y = 0
	while Y < len(combined_df):

		row = combined_df.iloc[Y]

		values.append((
			str(row["ticker"]),
			str(row["headline"]),
			str(row["publisher_name"]),
			str(row["published_utc"]),
			str(row["google_link"])
		))

		Y += 1

	# --------------------------------------------------------
	# SQL
	# --------------------------------------------------------
	sql = """
	INSERT IGNORE INTO google_news_links
	(ticker, headline, publisher_name, published_utc, google_link)
	VALUES (%s, %s, %s, %s, %s)
	"""

	# --------------------------------------------------------
	# EXECUTE
	# --------------------------------------------------------
	try:
		run_sql(sql, values)
		print(f"💾 Inserted (or skipped duplicates): {len(values)} rows")
	except Exception as e:
		print(f"❌ Insert failed: {e}")

	return combined_df


#----------API-VERSION------------#









#----------SELENIUM-VERSION------------#


def fetch_google_news_selenium(driver, ticker, co_name, time_window='1d'):

	from bs4 import BeautifulSoup
	import pandas as pd
	import time

	# -------------------------
	# CLEAN INPUT
	# -------------------------
	ticker = str(ticker).strip().upper()
	co_name = str(co_name).strip()

	query = f"{ticker} stock {co_name} when:{time_window}"
	url = f"https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US:en"

	# -------------------------
	# CREATE DRIVER (your requirement)
	# -------------------------
	

	driver.get(url)


	# Overlay (your branding)
	with open('templates/powered_by.py') as f:
		exec(f.read())





	# -------------------------
	# FAST SCROLL
	# -------------------------
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

	time.sleep(0.5)

	# -------------------------
	# PARSE PAGE
	# -------------------------
	soup = BeautifulSoup(driver.page_source, "html.parser")

	# -------------------------
	# HEADLINES
	# -------------------------
	headlines = soup.find_all("a", class_="JtKRv")

	headline_texts = []
	Y = 0
	while Y < len(headlines):
		headline_texts.append(headlines[Y].text.strip())
		Y += 1

	# -------------------------
	# LINKS
	# -------------------------
	links = soup.find_all("a", class_="WwrzSb")

	urls = []
	Y = 0
	while Y < len(links):

		if links[Y].get("href"):
			urls.append("https://news.google.com" + links[Y]['href'].split("?")[0][1:])
		else:
			urls.append(None)

		Y += 1

	# -------------------------
	# SOURCES
	# -------------------------
	sources = soup.find_all("div", class_="vr1PYe")

	Y = 0
	while Y < len(sources):
		sources[Y] = sources[Y].text.strip()
		Y += 1

	# -------------------------
	# TIME (ISO)
	# -------------------------
	times = soup.find_all("time")

	time_iso = []
	Y = 0
	while Y < len(times):

		if times[Y].has_attr("datetime"):
			time_iso.append(times[Y]["datetime"])
		else:
			time_iso.append(None)

		Y += 1

	# -------------------------
	# BUILD DF
	# -------------------------
	rows = []

	min_len = min(len(headline_texts), len(sources), len(time_iso), len(urls))

	Y = 0
	while Y < min_len:

		rows.append({
			"ticker": ticker,
			"headline": headline_texts[Y],
			"source": sources[Y],
			"published_utc": time_iso[Y],
			"google_link": urls[Y]
		})

		Y += 1

	df = pd.DataFrame(rows)

	# -------------------------
	# CLEAN TIME
	# -------------------------
	if not df.empty:
		df["published_utc"] = pd.to_datetime(df["published_utc"], errors="coerce", utc=True)

	# -------------------------
	# CLOSE DRIVER
	# -------------------------

	return df




def run_fetch_google_news_selenium(ticker_list, time_window, hours_filter, driver):

	import pandas as pd
	import time
	import random

	# --------------------------------------------------------
	# DRIVER MANAGEMENT
	# --------------------------------------------------------
	driver_created_here = False

	if driver is None:
		print("🚀 Creating Selenium driver...")
		driver = create_driver_profile_1(headless=False)
		driver_created_here = True
	else:
		print("♻️ Using existing driver...")

	# --------------------------------------------------------
	# LOAD UNIVERSE
	# --------------------------------------------------------
	all_stocks_df = pd.read_csv("robinhood_universe.csv")

	ticker_to_name = dict(zip(
		all_stocks_df['symbol'].astype(str).str.strip().str.upper(),
		all_stocks_df['simple_name'].astype(str)
	))

	# --------------------------------------------------------
	# LOOP TICKERS
	# --------------------------------------------------------
	df_list = []

	Y = 0
	while Y < len(ticker_list):

		ticker = ticker_list[Y]

		if not ticker:
			Y += 1
			continue

		ticker_clean = str(ticker).strip().upper()
		co_name = ticker_to_name.get(ticker_clean, "")

		print(f"📰 Fetching: {ticker_clean}")

		try:

			df = fetch_google_news_selenium(
				driver=driver,
				ticker=ticker_clean,
				co_name=co_name,
				time_window=time_window
			)

			if df is not None and not df.empty:
				df_list.append(df)

		except Exception as e:
			print(f"❌ Error fetching {ticker_clean}: {e}")

		time.sleep(random.uniform(0.8, 1.5))

		Y += 1

	# --------------------------------------------------------
	# CLOSE DRIVER (ONLY IF CREATED HERE)
	# --------------------------------------------------------
	if driver_created_here:
		print("🛑 Closing driver...")
		driver.quit()

	# --------------------------------------------------------
	# COMBINE
	# --------------------------------------------------------
	if len(df_list) == 0:
		print("❌ No data collected")
		return pd.DataFrame()

	combined_df = pd.concat(df_list, ignore_index=True)

	# --------------------------------------------------------
	# DEDUPE
	# --------------------------------------------------------
	before_dedupe = len(combined_df)

	combined_df = combined_df.drop_duplicates(
		subset=["google_link"]
	).reset_index(drop=True)

	print(f"🧹 Deduped: {before_dedupe} → {len(combined_df)}")

	# --------------------------------------------------------
	# RENAME
	# --------------------------------------------------------
	if "source" in combined_df.columns:
		combined_df.rename(columns={"source": "publisher_name"}, inplace=True)

	# --------------------------------------------------------
	# HARD TIME FILTER
	# --------------------------------------------------------
	combined_df["published_utc"] = pd.to_datetime(
		combined_df["published_utc"],
		errors="coerce",
		utc=True
	)

	now_utc = pd.Timestamp.utcnow()
	cutoff = now_utc - pd.Timedelta(hours=hours_filter)

	before_filter = len(combined_df)

	combined_df = combined_df[
		(combined_df["published_utc"].notna()) &
		(combined_df["published_utc"] <= now_utc) &
		(combined_df["published_utc"] >= cutoff)
	].reset_index(drop=True)

	print(f"🧹 Time Filter: {before_filter} → {len(combined_df)}")

	if len(combined_df) == 0:
		print("⚠️ No recent news")
		return combined_df

	# --------------------------------------------------------
	# CLEAN
	# --------------------------------------------------------
	combined_df = combined_df.fillna("")

	# --------------------------------------------------------
	# BUILD VALUES (SAFE)
	# --------------------------------------------------------
	values = []

	Y = 0
	while Y < len(combined_df):

		row = combined_df.iloc[Y]

		values.append((
			str(row["ticker"]),
			str(row["headline"]),
			str(row["publisher_name"]),
			str(row["published_utc"]),
			str(row["google_link"])
		))

		Y += 1

	# --------------------------------------------------------
	# SQL
	# --------------------------------------------------------
	sql = """
	INSERT IGNORE INTO google_news_links
	(ticker, headline, publisher_name, published_utc, google_link)
	VALUES (%s, %s, %s, %s, %s)
	"""

	# --------------------------------------------------------
	# EXECUTE
	# --------------------------------------------------------
	try:
		run_sql(sql, values)
		print(f"💾 Inserted: {len(values)} rows")
	except Exception as e:
		print(f"❌ Insert error: {e}")

	return combined_df




#----------SELENIUM-VERSION------------#







def get_news_counts(hours=6):

	sql = f"""
		SELECT 
			ticker,
			COUNT(*) AS article_count,
			MAX(published_utc) AS latest_article_time
		FROM google_news_links
		WHERE published_utc >= NOW() - INTERVAL {hours} HOUR
		GROUP BY ticker
		ORDER BY article_count DESC
	"""

	df = run_sql(sql).to_df()

	return df


#-----------------------------------------------------------------------






























#FETCH STOCK TWITS
#----------------------------------------------------------------------------------------------





#----------API-VERSION------------#


def api_fetch_stocktwits_sentiment(ticker_list, max_workers=5, batch_size=200):

    import requests
    import time
    import random
    import pandas as pd
    from concurrent.futures import ThreadPoolExecutor, as_completed

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    session.headers.update(headers)

    # =========================
    # FETCH SINGLE TICKER (ROBUST)
    # =========================
    def fetch_ticker(ticker):

        url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"

        attempt = 0
        max_attempts = 3

        while attempt < max_attempts:

            try:
                r = session.get(url, timeout=5)

                # SUCCESS
                if r.status_code == 200:
                    data = r.json()
                    messages = data.get("messages", [])

                    rows = []

                    i = 0
                    while i < len(messages):

                        m = messages[i]

                        sentiment_obj = m.get("entities", {}).get("sentiment")

                        if sentiment_obj:
                            sentiment = sentiment_obj.get("basic")
                        else:
                            sentiment = None

                        rows.append({
                            "ticker": ticker,
                            "id": m.get("id"),
                            "created_at": m.get("created_at"),
                            "user": m.get("user", {}).get("username"),
                            "likes": m.get("likes", {}).get("total"),
                            "sentiment": sentiment,
                            "body": m.get("body")
                        })

                        i += 1

                    # jitter
                    time.sleep(random.uniform(0.6, 1.2))

                    return rows

                # RATE LIMITED
                elif r.status_code == 429:
                    print(f"⛔ 429 rate limit → {ticker} retrying...")
                    time.sleep(2 + random.uniform(0.5, 1.5))

                # OTHER FAIL
                else:
                    print(f"⚠️ {ticker} status {r.status_code}")
                    time.sleep(1)

            except Exception as e:
                print(f"❌ ERROR {ticker} → {str(e)}")
                time.sleep(1)

            attempt += 1

        print(f"🚫 DROP {ticker}")
        return []

    # =========================
    # BATCH PROCESSING (CRITICAL)
    # =========================
    all_rows = []

    i = 0
    batch_num = 1

    while i < len(ticker_list):

        batch = ticker_list[i:i + batch_size]

        print(f"\n🚀 BATCH {batch_num} | tickers {i} → {i + len(batch)}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:

            futures = []

            Y = 0
            while Y < len(batch):
                futures.append(executor.submit(fetch_ticker, batch[Y]))
                Y += 1

            for future in as_completed(futures):
                result = future.result()
                if result:
                    all_rows.extend(result)

        # cooldown between batches
        print("🧊 cooling down...")
        time.sleep(5)

        i += batch_size
        batch_num += 1

    # =========================
    # DATAFRAME BUILD
    # =========================
    df = pd.DataFrame(all_rows)

    if len(df) > 0:
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["scraped_at"] = pd.Timestamp.now()

    print(f"\n✅ DONE → {len(df)} rows")

    return df


def analize_stocktwits_sentiment(df_msgs):
	
	
	import numpy as np
	
	df = df_msgs.copy()
	
	# =========================
	# BASIC CLEAN
	# =========================
	df["likes"] = df["likes"].fillna(0)
	
	# sentiment → numeric
	df["sentiment_score"] = df["sentiment"].map({
		"Bullish": 1,
		"Bearish": -1
	}).fillna(0)
	
	
	# =========================
	# GROUP BY TICKER
	# =========================
	analysis = df.groupby("ticker").agg({
		"id": "count",                    # message volume
		"user": pd.Series.nunique,       # unique users
		"likes": "sum",                  # total likes
		"sentiment_score": "sum"         # net sentiment
	}).reset_index()
	
	analysis.columns = [
		"ticker",
		"message_volume",
		"unique_users",
		"total_likes",
		"net_sentiment"
	]
	
	
	# =========================
	# DERIVED METRICS
	# =========================
	
	# avg sentiment per message
	analysis["avg_sentiment"] = analysis["net_sentiment"] / analysis["message_volume"]
	
	# participation ratio
	analysis["participation_ratio"] = analysis["unique_users"] / analysis["message_volume"]
	
	# likes per message
	analysis["likes_per_message"] = analysis["total_likes"] / analysis["message_volume"]
	
	# sentiment % (0–100 style)
	analysis["bullish_percent"] = (
		(analysis["avg_sentiment"] + 1) / 2
	) * 100
	
	
	# =========================
	# OPTIONAL SCORE (🔥 useful)
	# =========================
	analysis["signal_score"] = (
		analysis["bullish_percent"] *
		analysis["participation_ratio"] *
		np.log1p(analysis["message_volume"])
	)
	
	
	analysis = analysis.sort_values("signal_score", ascending=False)
	
	return analysis


#----------API-VERSION------------#









#----------SELENIUM-VERSION------------#

def selenium_fetch_stocktwits_sentiment(ticker_list, driver):

    results = []

    Y = 0
    while Y < len(ticker_list):

        ticker = ticker_list[Y]

        watcher_count = None
        sent_score = None
        message_volume = None
        participation_ratio = None

        try:
            try:
                driver.get(f"https://stocktwits.com/symbol/{ticker}/sentiment")
            except:
                raise Exception("timeout")

            # Overlay
            with open('templates/powered_by.py') as f:
                exec(f.read())

            time.sleep(.25 + random.random())

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # =========================
            # WATCHERS
            # =========================
            try:
                watcher_el = soup.find(
                    "span",
                    class_=lambda x: x and "SymbolWatchers_watchers" in x
                )

                if watcher_el:
                    text = watcher_el.get_text(" ", strip=True)

                    match = re.search(r"\d{1,3}(?:,\d{3})*", text)

                    if match:
                        watcher_count = int(match.group().replace(",", ""))

            except:
                pass

            # =========================
            # SENTIMENT
            # =========================
            try:
                elements = soup.find_all(
                    "div",
                    class_=lambda x: x and "gauge_gagueNumber" in x
                )

                scores = []

                i = 0
                while i < len(elements):

                    text = elements[i].text.strip()

                    if text.isdigit():
                        scores.append(int(text))

                    i += 1

                if len(scores) >= 2:
                    sent_score = scores[0]
                    message_volume = scores[1]

            except:
                pass

            participation_ratio = message_volume

        except:
            pass

        results.append({
            "ticker": ticker,
            "watch_count": watcher_count,
            "sent_score": sent_score,
            "message_volume": message_volume,
            "participation_ratio": participation_ratio
        })

        Y += 1

    # =========================
    # CREATE DF
    # =========================
    stocktwitts_sentiment_results_df = pd.DataFrame(results)

    # 🔥 CRITICAL FIX: normalize NaN → None
    stocktwitts_sentiment_results_df = stocktwitts_sentiment_results_df.where(
        pd.notnull(stocktwitts_sentiment_results_df), None
    )

    # =========================
    # SQL INSERT
    # =========================
    Y = 0
    values = []

    while Y < len(stocktwitts_sentiment_results_df):

        row = stocktwitts_sentiment_results_df.iloc[Y]

        ticker = str(row['ticker']).replace("'", "''")

        # 🔥 SAFE conversion
        def safe_int(val):
            if val is None or pd.isna(val):
                return "NULL"
            try:
                return int(val)
            except:
                return "NULL"

        watch_count = safe_int(row['watch_count'])
        sent_score = safe_int(row['sent_score'])
        message_volume = safe_int(row['message_volume'])
        participation_ratio = safe_int(row['participation_ratio'])

        values.append(f"""(
            '{ticker}',
            {watch_count},
            {sent_score},
            {message_volume},
            {participation_ratio},
            NOW()
        )""")

        Y += 1

    # =========================
    # INSERT
    # =========================
    if len(values) > 0:

        sql = f"""
        INSERT INTO stocktwits_selenium
        (
            ticker,
            watch_count,
            sent_score,
            message_volume,
            participation_ratio,
            scraped_at
        )
        VALUES
        {",".join(values)}

        ON DUPLICATE KEY UPDATE
            watch_count = VALUES(watch_count),
            sent_score = VALUES(sent_score),
            message_volume = VALUES(message_volume),
            participation_ratio = VALUES(participation_ratio),
            scraped_at = NOW()
        """

        run_sql(sql)

    return stocktwitts_sentiment_results_df



#----------SELENIUM-VERSION------------#







#----------------------------------------------------------------------------------------------
















##############################################################################################################































#Marginal analysis fx
##############################################################################################################



def marginal_analysis_stocktwitts_selenium():


	# -----------------------------------
	# Insert / Upsert marginal analysis
	# -----------------------------------
	run_sql("""

	INSERT INTO marginal_analysis_stocktwitts_selenium
	(
		ticker,
		current_ts,
		prev_ts,
		delta_watch_count,
		delta_sent_score,
		delta_message_volume,
		delta_participation_ratio
	)

	SELECT
		t1.ticker,

		t1.scraped_at AS current_ts,
		t2.scraped_at AS prev_ts,

		t1.watch_count - t2.watch_count,
		t1.sent_score - t2.sent_score,
		t1.message_volume - t2.message_volume,
		t1.participation_ratio - t2.participation_ratio

	FROM stocktwits_selenium t1

	JOIN stocktwits_selenium t2
		ON t1.ticker = t2.ticker
		AND t2.scraped_at = (
			SELECT MAX(scraped_at)
			FROM stocktwits_selenium
			WHERE ticker = t1.ticker
			AND scraped_at < t1.scraped_at
		)

	ON DUPLICATE KEY UPDATE
		delta_watch_count = VALUES(delta_watch_count),
		delta_sent_score = VALUES(delta_sent_score),
		delta_message_volume = VALUES(delta_message_volume),
		delta_participation_ratio = VALUES(delta_participation_ratio),
		prev_ts = VALUES(prev_ts);

	""")

	# -----------------------------------
	# Optional: return latest snapshot
	# -----------------------------------
	return run_sql("""

	SELECT *
	FROM marginal_analysis_stocktwitts_selenium
	ORDER BY current_ts DESC

	""")






##############################################################################################################













#Filters

#################################################################################################################


def check_tickers_in_universe(ticker_list, universe_list):

	valid = []

	universe_set = set()

	Y = 0
	while Y < len(universe_list):

		u = universe_list[Y]

		if u and str(u) != "nan":
			universe_set.add(str(u).strip().upper())

		Y += 1

	Y = 0
	while Y < len(ticker_list):

		t = ticker_list[Y]

		if t and str(t) != "nan":
			t_clean = str(t).strip().upper()

			if t_clean in universe_set:
				valid.append(t_clean)

		Y += 1

	return valid






#################################################################################################################


























#Robinhood Selenium Functions
#################################################################################################################


def check_robinhood_portfolio(driver):
	





	# ⚠️ YOUR ORIGINAL LINE (UNCHANGED)
	driver.set_page_load_timeout(6)



	
	#LOAD THE PAGE:
	######################################################################################################################################
	

	driver.get('https://robinhood.com/account/investing')    



	with open('templates/scraping_portfolio_start.py') as f:
		exec(f.read())






	#WAIT FOR PAGE TO LOAD
	wait = WebDriverWait(driver, 7, poll_frequency=1)
	random_variable = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react_root"]/main/div[2]/div/div/div/div/div[1]/div/h1')))    
	
	#SCROLL TO BOTTOM OF PAGE TO HIDE BALANCE
	time.sleep(.01)
	driver.execute_script("window.scrollTo(0, 4000)") 
	
	#WAIT FOR PAGE TO FULLY LOAD 
	random_variable2_xpath = '//*[@id="react_root"]/main/div[2]/div/div/div/div/div[2]/div/section[1]/section/div[3]/h2/span'
	wait.until(EC.element_to_be_clickable((By.XPATH, random_variable2_xpath)))    
	######################################################################################################################################
	
	# SCRAPE PORTFOLIO OVERVIEW TABLE
	###################################################################################################################
	all_data_xpath = '//*[@id="react_root"]/main/div[2]/div/div/div/div/div[2]/div/section[1]/section/div[1]/div[1]'
	all_data = driver.find_elements(By.XPATH, all_data_xpath)
	all_data = all_data[0].text.split('\n')
	
	# PARSE ALL DATA LIST TO COLUMNS LISTS
	asset_type = all_data[0::3]
	percent_of_portfolio = all_data[1::3]
	dollar_amount_held = all_data[2::3]
	
	# EDIT COLUMNS LISTS IN DOUBLE LOOP
	edit_list = [percent_of_portfolio, dollar_amount_held]
	
	Z = 0
	while Z < len(edit_list):
		Y = 0
		while Y < len(edit_list[Z]):
			edit_list[Z][Y] = (edit_list[Z][Y].replace('$', '').replace(',', '').replace('%', ''))
			try:
				edit_list[Z][Y] = float(edit_list[Z][Y])
			except:
				pass
			Y += 1
		Z += 1
	
	# PUT THE COLUMNS LISTS INTO A DICT    
	overview_col_dict = {
		'asset_type': asset_type[:],
		'percent_of_portfolio': percent_of_portfolio[:],
		'dollar_amount_held': dollar_amount_held[:],
	}
	
	current_overview = pd.DataFrame(overview_col_dict)
	###################################################################################################################
	
	# SCRAPE STOCKS TABLE 
	######################################################################################################################
	all_data_xpath = '/html/body/div[1]/main/div[2]/div/div/div/div/div[2]/div/section[1]/section/div[2]/div/div[1]/div'
	all_data = driver.find_elements(By.XPATH, all_data_xpath)
	all_data = all_data[0].text.split('\n')
	
	company_name = all_data[0::7]
	symbol = all_data[1::7]
	shares = all_data[2::7]
	market_price = all_data[3::7]
	average_cost = all_data[4::7]
	total_return = all_data[5::7]
	equity = all_data[6::7]
	
	edit_list = [shares, market_price, average_cost, total_return, equity]
	Z = 0
	while Z < len(edit_list):
		Y = 0
		while Y < len(edit_list[Z]):
			edit_list[Z][Y] = (edit_list[Z][Y].replace('$', '').replace(',', '').replace('%', ''))
			try:
				edit_list[Z][Y] = float(edit_list[Z][Y])
			except:
				pass
			Y += 1
		Z += 1
	
	stock_col_dict = {
		'ticker': symbol[1:],
		'name': company_name[1:],
		'shares': shares[1:],
		'price': market_price[1:],
		'average_cost': average_cost[1:],
		'total_return': total_return[1:],
		'equity': equity[1:],
	}
	
	current_stocks = pd.DataFrame(stock_col_dict)
	
	now = datetime.now()
	current_stocks['datetime'] = now.strftime('%Y-%m-%d %H:%M:%S')
	current_stocks['str_date'] = now.strftime('%m/%d/%Y')
	current_stocks['str_time'] = now.strftime('%H:%M:%S')
	######################################################################################################################
	
	# SCRAPE CRYPTO TABLE 
	#######################################################################################################################
	all_data_xpath = '//*[@id="react_root"]/main/div[2]/div/div/div/div/div[2]/div/section[1]/section/div[3]/div/div[1]/div'
	all_data = driver.find_elements(By.XPATH, all_data_xpath)
	all_data = all_data[0].text.split('\n')
	
	company_name = all_data[0::7]
	symbol = all_data[1::7]
	shares = all_data[2::7]
	market_price = all_data[3::7]
	average_cost = all_data[4::7]
	total_return = all_data[5::7]
	equity = all_data[6::7]
	
	edit_list = [shares, market_price, average_cost, total_return, equity]
	Z = 0
	while Z < len(edit_list):
		Y = 0
		while Y < len(edit_list[Z]):
			edit_list[Z][Y] = (edit_list[Z][Y].replace('$', '').replace(',', '').replace('%', ''))
			try:
				edit_list[Z][Y] = float(edit_list[Z][Y])
			except:
				pass
			Y += 1
		Z += 1
	
	crypto_col_dict = {
		'ticker': symbol[1:],
		'co_name': company_name[1:],
		'shares': shares[1:],
		'price': market_price[1:],
		'average_cost': average_cost[1:],
		'total_return': total_return[1:],
		'equity': equity[1:],
	}
	
	current_crypto = pd.DataFrame(crypto_col_dict)
	
	current_crypto['datetime'] = now.strftime('%Y-%m-%d %H:%M:%S')
	current_crypto['str_date'] = now.strftime('%m/%d/%Y')
	current_crypto['str_time'] = now.strftime('%H:%M:%S')
	#######################################################################################################################
	






	with open('templates/scraping_portfolio_end.py') as f:
		exec(f.read())











	run_sql("DELETE FROM robinhood_portfolio;")


	values_list = []

	Y = 0
	while Y < len(current_stocks):

		row = current_stocks.iloc[Y]

		values_list.append(f"""(
			'{str(row["ticker"])}',
			'{str(row["name"]).replace("'", "''")}',

			{str(row["shares"]).replace("—","0").replace("–","0")},
			{str(row["price"]).replace("—","0").replace("–","0")},
			{str(row["average_cost"]).replace("—","0").replace("–","0")},
			{str(row["total_return"]).replace("—","0").replace("–","0")},
			{str(row["equity"]).replace("—","0").replace("–","0")},

			'{str(row["datetime"])}',
			'{str(row["str_date"])}',
			'{str(row["str_time"])}'
		)""")

		Y += 1


	values_sql = ",\n".join(values_list)

	run_sql(f"""
	INSERT INTO robinhood_portfolio (
		ticker,
		name,
		shares,
		price,
		average_cost,
		total_return,
		equity,
		datetime,
		str_date,
		str_time
	)
	VALUES
	{values_sql};
	""")






	print("Robinhood portfolio updated")
	time.sleep(1.5) #time for animation.. kinda dumb but whatevs. 


	# 🔥 RETURN THROUGH SAFE HANDLER (ADDED)
	return current_overview, current_stocks, current_crypto







################################
#market buy fx new in progress
################################



#ticker = 'NDAQ'
#input_amount = "2.00"
#buy_in_type = 'Shares'
#buy_in_type = 'Dollars'
#live = False

	
def robinhood_market_buy(ticker, input_amount, buy_in_type, live, driver):
	
	
	wait = WebDriverWait(driver, 1, poll_frequency=0.1)



	driver.get(f'https://robinhood.com/stocks/{ticker}?source=lists_section_position')
	
	
	with open('templates/powered_by.py') as f:
		exec(f.read())
	
	
	
	time.sleep(1)
	
	
	# Force focus
	driver.execute_script("window.focus();")
	
	# Keep alive ping
	driver.execute_script("document.body.dispatchEvent(new MouseEvent('mousemove', {bubbles: true}));")
	
	
	
	
	
	
	
	#make sure you are in buy 
	buy_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='OrderFormHeading-Buy']")))
	
	if "Buy" in buy_btn.text:
		buy_btn.click()
	
	
	
	
	
	
	
	
	
	# =========================
	# Order Type dropdown 
	# =========================
	order_type_dropdown = driver.find_element(By.XPATH, "//button[@role='combobox'][.//span[text()='Buy order']]")
	order_type_dropdown.click()
	time.sleep(.05)
	
	options = driver.find_elements(By.XPATH,"//ul[@role='listbox']//li | //div[@role='option']")
	options_text_list = [opt.text.strip() for opt in options if opt.text.strip() != ""]
	options_text_index = options_text_list.index("Buy order") if "Buy order" in options_text_list else None
	options[options_text_index].click()
	
	
	
	
	
	
	
	
	# ====================================
	# Buy In Shares or Dollars  dropdown 
	# ====================================
	buy_in_dropdown = driver.find_element(By.XPATH,"//button[@role='combobox'][.//span[text()='Dollars' or text()='Shares']]")
	buy_in_dropdown.click()
	time.sleep(.05)
	
	options = driver.find_elements(By.XPATH,"//ul[@role='listbox']//li | //div[@role='option']")
	
	# ✅ FIX: only visible options
	options = [opt for opt in options if opt.is_displayed()]
	options_text_list = [opt.text.strip() for opt in options if opt.text.strip() != ""]
	
	
	if buy_in_type == 'Dollars':
		target = "Dollars"
	
	if buy_in_type == 'Shares':
		target = 'Shares'
	
	
	options_text_index = options_text_list.index(target) if target in options_text_list else None
	options[options_text_index].click()
	
	
	
	
	time.sleep(.15)
	
	
	# =========================
	# Input box  
	# =========================
	if buy_in_type == 'Dollars':
		input_box = driver.find_element(By.XPATH,"//input[@data-testid='OrderFormRows-Dollars']")
	
	if buy_in_type == 'Shares':
		input_box = driver.find_element(By.XPATH,"//input[@data-testid='OrderFormRows-Shares']")
	
	
	input_box.click()
	time.sleep(.05)
	
	# select all + delete (React-safe clear)
	input_box.send_keys("\u0001")  # CMD/CTRL + A
	input_box.send_keys("\u0008")  # delete
	
	time.sleep(.07)
	
	
	if buy_in_type == 'Dollars':
		input_box.send_keys(input_amount)
	
	
	if buy_in_type == 'Shares':
	
		input_amount = 5.00   # dollars you want to spend
	
		price_el = driver.find_element(By.XPATH,"//div[@data-testid='MarketPriceRow']//span")
		price_text = price_el.text.strip()
		price = float(price_text.replace("$", "").replace(",", ""))
	
		# CALCULATE SHARES
		shares = input_amount / price
		shares = round(shares, 6)# Robinhood usually allows fractional → round to something clean
		input_box.send_keys(str(shares))
	
	
	
	
	
	
	
	# =========================
	# Confirm_button_1 
	# =========================
	confirm_button_1 = driver.find_element(By.XPATH,"//button[@data-testid='OrderFormControls-Review'] | //button[.//span[text()='Review order' or text()='Trade now']]")
	confirm_button_1_text = confirm_button_1.text.strip()
	print(confirm_button_1_text)
	
	
	
	
	
	if confirm_button_1_text == 'Review order': 
		confirm_button_1.click()
		time.sleep(.1)
		wait = WebDriverWait(driver, 1)
	
	
		
		
		#define confirm_button_2
		try:
			confirm_button_2 = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='OrderFormControls-Submit']")))    
	
		except:
			confirm_button_2 = wait.until(EC.presence_of_element_located((By.XPATH, "//button[.//span[text()='Continue']]")))
	
		confirm_button_2_text = confirm_button_2.get_attribute("innerText").strip()
		
	
	
		
		print(confirm_button_2_text)
	
		
		if confirm_button_2_text == 'Buy':
			time.sleep(.5)
	
			if live == True: 
				print('build me')
	
	
			if live == False: 
	
				#load sucess page
				with open('templates/market_buy_test_success.py') as f:
					exec(f.read())
	
				time.sleep(1.5)
					
	
	
		if confirm_button_2_text == 'Continue':
			#print('build me')
			buy_in_whole_shares_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Buy in whole shares']]")))
			if buy_in_whole_shares_button.text == 'Buy in whole shares':
				robinhood_market_buy(ticker = ticker, input_amount = ticker, buy_in_type = 'Shares', live = False, driver = driver)
				

			  


#################################################################################################################





































#end of the page 









