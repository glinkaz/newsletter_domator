import os
import json
import time
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
                try:
                    options = Options()
                    options.add_argument("--headless=new")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--window-size=1920,1080")
                    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
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
                        # Użyj sterownika i binarki z systemu/Dockera, a lokalnie pobierz je automatycznie.
                        if chromedriver_path:
                            driver = webdriver.Chrome(service=ChromeService(executable_path=chromedriver_path), options=options)
                        else:
                            try:
                                driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                            except Exception:
                                # Ostateczny fallback dla środowisk z poprawnie skonfigurowanym Selenium Manager.
                                driver = webdriver.Chrome(options=options)
                            
                        driver.set_page_load_timeout(15)
                        driver.get(ceneo_url)
                        
                        # Czekamy chwilę na wykonanie JavaScriptu (np. walidacja Cloudflare)
                        time.sleep(4)
                        
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                    finally:
                        if driver:
                            driver.quit()
                        
                    # Kontynuacja starym kodem parsującym
                    if soup:
                        
                        # Strategy 0: JSON-LD Schema (Najbardziej uniwersalne, wspiera MediaExpert itp)
                        ld_scripts = soup.find_all('script', type='application/ld+json')
                        for script in ld_scripts:
                            if ceneo_last_price is not None: break
                            try:
                                data = json.loads(script.string)
                                if isinstance(data, dict): data = [data]
                                for item in data:
                                    if isinstance(item, dict) and item.get('@type') in ['Product', 'Offer']:
                                        offers = item.get('offers', {})
                                        if isinstance(offers, dict):
                                            if 'lowPrice' in offers:
                                                ceneo_last_price = float(str(offers.get('lowPrice')).replace(',', '.'))
                                            elif 'price' in offers:
                                                ceneo_last_price = float(str(offers.get('price')).replace(',', '.'))
                                        elif isinstance(offers, list) and len(offers) > 0:
                                            prices = []
                                            for o in offers:
                                                if isinstance(o, dict) and 'price' in o:
                                                    try: prices.append(float(str(o.get('price')).replace(',', '.')))
                                                    except ValueError: pass
                                            if prices:
                                                ceneo_last_price = min(prices)
                                        if ceneo_last_price is not None:
                                            print(f"[CENEO] Found price via JSON-LD: {ceneo_last_price}", flush=True)
                                            break
                            except Exception: pass
                        # Strategy 1: Szukanie po atrybucie `data-price` (dokładnie to o co prosiłeś)
                        if ceneo_last_price is None:
                            # Znajduje WSZYSTKIE elementy na stronie posiadające atrybut data-price
                            data_price_elements = soup.find_all(attrs={"data-price": True})
                            if data_price_elements:
                                prices = []
                                for el in data_price_elements:
                                    # Pobieramy wyłącznie wartość z 'data-price' i ignorujemy 'data-productminprice'
                                    dp = el['data-price']
                                    try:
                                        prices.append(float(dp.replace(',', '.')))
                                    except ValueError:
                                        pass
                                
                                if prices:
                                    ceneo_last_price = min(prices) # Wybiera najniższą ze wszystkich zescrapowanych
                                    print(f"[CENEO] Znaleziono najniższą cenę po atrybutach data-price: {ceneo_last_price}", flush=True)

                        # Strategy 2: Meta tags (Jako rezerwa dla innych sklepów niż Ceneo)
                        if ceneo_last_price is None:
                            price_meta = soup.select_one('meta[itemprop="price"], meta[property="product:price:amount"]')
                            if price_meta and price_meta.get('content'):
                                 try:
                                     ceneo_last_price = float(price_meta['content'].replace(',', '.'))
                                     print(f"[CENEO] Found price via META tag: {ceneo_last_price}", flush=True)
                                 except: pass

                        # Strategy 3: Konkretne klasy CSS (Jako ostateczna rezerwa)
                        if ceneo_last_price is None:
                            price_tags = soup.select('.price .value, .product-price')
                            prices = []
                            for tag in price_tags:
                                txt = tag.text.replace(' ', '').replace('\xa0', '').replace(',', '.')
                                match = re.search(r'(\d+\.?\d*)', txt)
                                if match:
                                    try: prices.append(float(match.group(1)))
                                    except: pass
                            if prices:
                                ceneo_last_price = min(prices)
                                print(f"[CENEO] Found price via specific visual tags: {ceneo_last_price}", flush=True)

                        
                        if ceneo_last_price is None:
                             print(f"[CENEO] Product {prod_id}: Page loaded but NO PRICE found. Selector failed.", flush=True)
                    else:
                         print(f"[CENEO] Product {prod_id}: HTTP Error {r.status_code}", flush=True)
                    
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
