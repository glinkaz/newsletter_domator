import os
import json
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import datetime
import psycopg2
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

CENEO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

DATABASE_CONFIG = {
    "host": os.environ.get("DB_HOST", "0.0.0.0"),
    "database": os.environ.get("DB_NAME", "products"),
    "user": os.environ.get("DB_USER", "zuzannaglinka"),
    "password": os.environ.get("DB_PASSWORD", "password")
}

def scrape_single_product(prod_id, prod_price, ceneo_url):
    """Refactored helper to scrape one product, used by daily job and immediate triggers."""
    if not prod_price or not ceneo_url:
        return

    # Log processing attempt
    print(f"[CENEO] Processing product {prod_id} (Price: {prod_price})", flush=True)

    try:
        # Create separate DB connection for this thread
        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor() as cur:
                # Try to convert our price to float for comparison
                our_price_float = None
                try:
                    if prod_price:
                        # Clean price string (handle "1 200,00", "1200.00", etc)
                        clean_price = str(prod_price).replace(',', '.').replace(' ', '').replace('\xa0', '')
                        our_price_float = float(clean_price)
                except ValueError:
                    print(f"[CENEO] Product {prod_id} has invalid price format '{prod_price}'. Skipping.", flush=True)
                    return 
                
                ceneo_last_price = None
                is_visible = True

                def _parse_price_value(raw_value):
                    if raw_value is None:
                        return None
                    try:
                        cleaned = str(raw_value).replace(',', '.').replace(' ', '').replace('\xa0', '')
                        return float(cleaned)
                    except (TypeError, ValueError):
                        return None

                def _looks_blocked(html_text):
                    lowered = html_text.lower()
                    blocked_markers = (
                        'access denied',
                        'captcha',
                        'cloudflare',
                        'robot',
                        'blocked',
                        'verify you are human',
                    )
                    return any(marker in lowered for marker in blocked_markers)

                def _parse_price_candidates(soup_object):
                    candidate_prices = []

                    ld_scripts = soup_object.find_all('script', type='application/ld+json')
                    for script in ld_scripts:
                        script_text = script.string or script.get_text(strip=True)
                        if not script_text:
                            continue
                        try:
                            data = json.loads(script_text)
                        except Exception:
                            continue

                        items = data if isinstance(data, list) else [data]
                        index = 0
                        while index < len(items):
                            item = items[index]
                            index += 1

                            if not isinstance(item, dict):
                                continue

                            graph_items = item.get('@graph')
                            if isinstance(graph_items, list):
                                items.extend(graph_items)

                            offers = item.get('offers', {})
                            if isinstance(offers, dict):
                                for key in ('lowPrice', 'price'):
                                    parsed = _parse_price_value(offers.get(key))
                                    if parsed is not None:
                                        candidate_prices.append(parsed)
                            elif isinstance(offers, list):
                                for offer in offers:
                                    if isinstance(offer, dict):
                                        parsed = _parse_price_value(offer.get('price'))
                                        if parsed is not None:
                                            candidate_prices.append(parsed)

                    for element in soup_object.find_all(attrs={"data-price": True}):
                        parsed = _parse_price_value(element.get('data-price'))
                        if parsed is not None:
                            candidate_prices.append(parsed)

                    for meta_selector in ('meta[itemprop="price"]', 'meta[property="product:price:amount"]'):
                        meta_tag = soup_object.select_one(meta_selector)
                        if meta_tag and meta_tag.get('content'):
                            parsed = _parse_price_value(meta_tag.get('content'))
                            if parsed is not None:
                                candidate_prices.append(parsed)

                    for tag in soup_object.select('.price .value, .product-price'):
                        text_value = tag.get_text(' ', strip=True)
                        match = re.search(r'(\d+[\d\s\xa0]*[\.,]?\d*)', text_value)
                        if match:
                            parsed = _parse_price_value(match.group(1))
                            if parsed is not None:
                                candidate_prices.append(parsed)

                    return candidate_prices

                html = None
                try:
                    session = requests.Session()
                    request_response = session.get(ceneo_url, headers=CENEO_HEADERS, timeout=20)
                    if request_response.ok and not _looks_blocked(request_response.text):
                        html = request_response.text
                    else:
                        print(f"[CENEO] Requests fetch failed or blocked for product {prod_id}; falling back to Selenium.", flush=True)

                    if html is None:
                        options = Options()
                        options.add_argument("--headless=new")
                        options.add_argument("--disable-gpu")
                        options.add_argument("--no-sandbox")
                        options.add_argument("--disable-dev-shm-usage")
                        options.add_argument("--window-size=1920,1080")
                        options.add_argument(f"user-agent={CENEO_HEADERS['User-Agent']}")
                        options.add_argument("--disable-blink-features=AutomationControlled")

                        chrome_binary = os.environ.get("CHROME_BIN")
                        if not chrome_binary:
                            for candidate in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
                                if os.path.exists(candidate):
                                    chrome_binary = candidate
                                    break
                        if chrome_binary:
                            options.binary_location = chrome_binary

                        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
                        if not chromedriver_path:
                            for candidate in ("/usr/bin/chromedriver", "/usr/lib/chromium/chromedriver"):
                                if os.path.exists(candidate):
                                    chromedriver_path = candidate
                                    break

                        driver = None
                        try:
                            if chromedriver_path:
                                driver = webdriver.Chrome(service=ChromeService(executable_path=chromedriver_path), options=options)
                            else:
                                try:
                                    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                                except Exception:
                                    driver = webdriver.Chrome(options=options)

                            driver.set_page_load_timeout(30)
                            driver.get(ceneo_url)
                            time.sleep(6)
                            html = driver.page_source
                        finally:
                            if driver:
                                driver.quit()

                    if html:
                        soup = BeautifulSoup(html, 'html.parser')
                        candidate_prices = _parse_price_candidates(soup)
                        if candidate_prices:
                            ceneo_last_price = min(candidate_prices)
                            print(f"[CENEO] Found price candidates for product {prod_id}: {candidate_prices} -> {ceneo_last_price}", flush=True)
                        else:
                            print(f"[CENEO] Product {prod_id}: Page loaded but NO PRICE found.", flush=True)
                    else:
                        print(f"[CENEO] Product {prod_id}: Could not load HTML from Ceneo.", flush=True)
                    
                    # Comparison Logic
                    if ceneo_last_price is not None:
                        # If Ceneo price is LOWER than our price -> Hide
                        if ceneo_last_price < our_price_float:
                            is_visible = False
                        
                        print(f"[CENEO] Result for {prod_id}: Our={our_price_float}, Ceneo={ceneo_last_price}. Visible={is_visible}", flush=True)
                        
                        cur.execute(
                            "UPDATE products SET ceneo_last_price=%s, ceneo_check_date=%s, visible=%s WHERE id=%s",
                            (ceneo_last_price, datetime.date.today(), is_visible, prod_id)
                        )
                        conn.commit()
                except Exception as e:
                    print(f"[CENEO] Error processing product {prod_id}: {e}", flush=True)
    except Exception as e:
         print(f"[CENEO] DB Error in single scrape: {e}", flush=True)

def check_ceneo_prices():
    print("[CENEO] Daily price check started", flush=True)
    try:
        # Create a new connection since this runs in a thread
        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, price, ceneo_url FROM products WHERE ceneo_url IS NOT NULL AND ceneo_url != ''")
                products = cur.fetchall()
                
                for prod in products:
                    prod_id, prod_price, ceneo_url = prod
                    scrape_single_product(prod_id, prod_price, ceneo_url)
                    
    except Exception as e:
        print(f"[CENEO] Scheduler Error: {e}", flush=True)

def start_ceneo_scheduler():
    # Start scheduler logic
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_ceneo_prices, trigger="interval", days=1)
    scheduler.start()

    # Check prices immediately on startup (in a separate thread if needed, but here simple call is fine)
    # Note: This might block startup slightly, but ensures user sees results.
    Thread(target=check_ceneo_prices).start()

    atexit.register(lambda: scheduler.shutdown())
    return scheduler
