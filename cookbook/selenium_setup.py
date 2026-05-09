# ============================================================
# SELENIUM ENGINE v1 (CLEAN FACTORY ONLY)
# ============================================================

print("Imported Selenium engine -- v15")

# ============================================================
# CORE IMPORTS
# ============================================================

import ssl
import selenium
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pandas as pd
import time
from io import StringIO

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException
)



def create_driver_profile(profile_name="selenium_chrome_profile", headless=False):

    import undetected_chromedriver as uc
    import os

    base_path = "/Users/deanemarks/"

    profile_path = base_path + profile_name

    options = uc.ChromeOptions()

    # -------------------------
    # LOAD STRATEGY
    # -------------------------
    options.page_load_strategy = "eager"

    # -------------------------
    # BLOCK IMAGES
    # -------------------------
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 1
    }
    options.add_experimental_option("prefs", prefs)

    # -------------------------
    # PROFILE (DYNAMIC 🔥)
    # -------------------------
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--profile-directory=Default")

    # -------------------------
    # PREVENT THROTTLING
    # -------------------------
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-background-networking")

    # -------------------------
    # PERFORMANCE
    # -------------------------
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # -------------------------
    # WINDOW
    # -------------------------
    options.add_argument("--window-size=1200,900")

    # -------------------------
    # HEADLESS
    # -------------------------
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    # -------------------------
    # LAUNCH
    # -------------------------
    driver = uc.Chrome(
        options=options,
        version_main=146,
        use_subprocess=True
    )

    # -------------------------
    # KEEP ALIVE
    # -------------------------
    try:
        driver.execute_script("""
            setInterval(() => {
                document.body.dispatchEvent(new MouseEvent('mousemove', {bubbles: true}));
            }, 2000);
        """)
    except:
        pass

    # -------------------------
    # BLOCK HEAVY REQUESTS
    # -------------------------
    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setBlockedURLs", {
            "urls": [
                "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp",
                "*.woff", "*.woff2", "*.ttf",
                "*.mp4", "*.webm"
            ]
        })
    except:
        pass

    return driver



#selenium_fetch_stocktwits_sentiment(ticker_list = filtered_tickers , driver = driver)









def create_driver_profile_1(headless=False):

    import undetected_chromedriver as uc

    options = uc.ChromeOptions()

    # -------------------------
    # LOAD STRATEGY
    # -------------------------
    options.page_load_strategy = "eager"

    # -------------------------
    # KEEP CSS, BLOCK IMAGES
    # -------------------------
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 1
    }
    options.add_experimental_option("prefs", prefs)

    # -------------------------
    # YOUR PROFILE (LOGIN PERSIST)
    # -------------------------
    options.add_argument("--user-data-dir=/Users/deanemarks/selenium_chrome_profile")
    options.add_argument("--profile-directory=Default")

    # -------------------------
    # 🔥 CRITICAL: PREVENT BACKGROUND THROTTLING
    # -------------------------
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-background-networking")

    # -------------------------
    # PERFORMANCE (SAFE)
    # -------------------------
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # -------------------------
    # WINDOW (IMPORTANT)
    # -------------------------
    options.add_argument("--window-size=1200,900")

    # -------------------------
    # HEADLESS (⚠️ NOT RECOMMENDED FOR TRADING)
    # -------------------------
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    # -------------------------
    # LAUNCH
    # -------------------------
    driver = uc.Chrome(
        options=options,
        version_main=146,
        use_subprocess=True
    )

    # -------------------------
    # 🔥 FORCE ACTIVE WINDOW
    # -------------------------
    driver.execute_script("window.focus();")

    # -------------------------
    # 🔥 KEEP ALIVE LOOP (ANTI-IDLE)
    # -------------------------
    try:
        driver.execute_script("""
            setInterval(() => {
                document.body.dispatchEvent(new MouseEvent('mousemove', {bubbles: true}));
            }, 2000);
        """)
    except:
        pass

    # -------------------------
    # BLOCK HEAVY NETWORK REQUESTS
    # -------------------------
    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setBlockedURLs", {
            "urls": [
                "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp",
                "*.woff", "*.woff2", "*.ttf",
                "*.mp4", "*.webm"
            ]
        })
    except:
        pass

    return driver







# ============================================================
# BROWSER FACTORY (VERSION SAFE)
# ============================================================
def create_browser(
        headless=True,
        load_strategy="eager",
        disable_images=False,
        disable_gpu=True
    ):

    import re
    import subprocess
    import undetected_chromedriver as uc

    # --------------------------------------------------------
    # Detect Installed Chrome Version (Mac)
    # --------------------------------------------------------
    try:
        chrome_version = subprocess.check_output(
            ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"]
        ).decode("utf-8")

        version_main = int(re.search(r"\d+", chrome_version).group())

    except Exception:
        version_main = None

    options = uc.ChromeOptions()
    options.page_load_strategy = load_strategy

    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if disable_gpu:
        options.add_argument("--disable-gpu")

    if headless:
        options.add_argument("--headless=new")

    if disable_images:
        prefs = {
            "profile.managed_default_content_settings.images": 2
        }
        options.add_experimental_option("prefs", prefs)

    # --------------------------------------------------------
    # Create driver
    # --------------------------------------------------------
    driver = uc.Chrome(
        options=options,
        version_main=version_main
    )

    if headless:
        print(f"🤖 Headless Bot Created (Chrome v{version_main})")

    return driver


# ============================================================
# TAB UTILITIES
# ============================================================

def open_new_tab(driver, url="about:blank"):
    driver.execute_script(f"window.open('{url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])


def list_all_tab_urls(driver):
    urls = []
    current = driver.current_window_handle

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        urls.append(driver.current_url)

    driver.switch_to.window(current)
    return urls


def switch_to_tab(driver, index):
    tabs = driver.window_handles

    if 0 <= index < len(tabs):
        driver.switch_to.window(tabs[index])
    else:
        raise IndexError(
            f"Tab index {index} out of range. Total tabs: {len(tabs)}"
        )


def close_current_tab(driver, switch_to_index=0):
    driver.close()

    tabs = driver.window_handles

    if tabs:
        driver.switch_to.window(tabs[switch_to_index])


def close_tab_by_index(driver, index):
    tabs = driver.window_handles

    if 0 <= index < len(tabs):

        tab_to_close = tabs[index]
        driver.switch_to.window(tab_to_close)
        driver.close()

        remaining_tabs = driver.window_handles

        if remaining_tabs:
            if index < len(remaining_tabs):
                driver.switch_to.window(remaining_tabs[index])
            else:
                driver.switch_to.window(remaining_tabs[-1])

    else:
        raise IndexError(
            f"Tab index {index} out of range. Total tabs: {len(tabs)}"
        )
