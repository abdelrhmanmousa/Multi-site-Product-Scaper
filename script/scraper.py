import json
import time
import random
import csv
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# 1. THE BASE SCRAPER (PARENT CLASS) - CORRECTED
#    - Manages the browser and defines the structure for all child scrapers.
# ==============================================================================
class BaseScraper:
    def __init__(self):
        self.scraped_data = []
        self.driver = self._init_driver()
        self.site_name = "Base" # To be overridden by child classes

    def _init_driver(self):
        """Initializes a Selenium WebDriver with robust anti-detection measures."""
        try:
            chrome_options = Options()
            # Comment out the next line to see the browser in action for debugging
            #chrome_options.add_argument('--headless')
            
            # Anti-detection measures
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            # === FIX: Corrected the User-Agent string ===
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            chrome_options.add_argument(f'user-agent={user_agent}')

            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            # avoid extremely long page loads; fail and retry from our own logic
            try:
                driver.set_page_load_timeout(30)
            except Exception:
                pass
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logging.info("Selenium WebDriver initialized.")
            return driver
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {e}")
            return None

    def get_all_product_urls(self, search_query, pages_to_scrape):
        """Placeholder method: Each site-specific scraper must implement this."""
        raise NotImplementedError("This method must be implemented by the subclass.")

    def scrape_product_details(self, product_urls):
        """Placeholder method: Each site-specific scraper must implement this."""
        raise NotImplementedError("This method must be implemented by the subclass.")

    def close(self):
        """Closes the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            logging.info("Selenium WebDriver closed.")

    def _get_attribute_value(self, soup, label_variants):
        """Generic helper to extract labeled attribute values.

        label_variants may be a single string label or an iterable of possible labels.
        Returns 'N/A' when not found.
        """
        try:
            if isinstance(label_variants, str):
                labels = [label_variants]
            else:
                labels = list(label_variants)

            for label in labels:
                # Try common patterns used across sites
                # 1) <span>Label</span><span>Value</span>
                label_element = soup.find(lambda tag: tag.name in ['span', 'td', 'th', 'div'] and tag.text and tag.text.strip() == label)
                if label_element:
                    # look for sibling value
                    sib = label_element.find_next_sibling()
                    if sib and sib.text.strip():
                        return sib.text.strip()

                # 2) <li><strong>Label</strong>Value</li> or similar
                strong = soup.find(lambda tag: tag.name in ['strong', 'b'] and tag.text and tag.text.strip() == label)
                if strong:
                    parent = strong.parent
                    if parent:
                        text = parent.get_text(separator=' ', strip=True)
                        # remove label from text
                        cleaned = text.replace(label, '').strip()
                        if cleaned:
                            return cleaned

                # 3) key: value within text
                possible = soup.find(string=lambda s: isinstance(s, str) and label in s)
                if possible:
                    # attempt to split on label
                    parts = possible.split(label)
                    if len(parts) > 1 and parts[1].strip(': ').strip():
                        return parts[1].strip(': ').strip()

            return 'N/A'
        except Exception:
            return 'N/A'

    def _wait_for_selectors(self, selectors, timeout=20):
        """Try waiting for any of the supplied selectors to become visible.

        selectors: list of tuples compatible with (By.<METHOD>, selector)
        Returns True when one is found, False otherwise.
        """
        for by, sel in selectors:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, sel))
                )
                return True
            except Exception:
                # try the next selector
                continue
        return False

    def _is_captcha_present(self, html=None):
        """Heuristic to detect presence of a CAPTCHA/recaptcha on the current page."""
        try:
            page = html if html is not None else (self.driver.page_source if self.driver else '')
            low = page.lower()
            if any(k in low for k in ['captcha', 'recaptcha', 'please verify', 'verify you are human']):
                return True

            # Also try a lightweight BeautifulSoup check for recaptcha if available
            try:
                soup = BeautifulSoup(page, 'html.parser')
                # iframe with recaptcha src
                iframe = soup.find('iframe', src=lambda s: s and 'recaptcha' in s)
                if iframe:
                    return True
                # divs with captcha-like classes
                div = soup.find(lambda tag: tag.name == 'div' and tag.get('class') and any('captcha' in c.lower() for c in tag.get('class')))
                if div:
                    return True
            except Exception:
                pass

            return False
        except Exception:
            return False

    def _click_possible_cookie_buttons(self):
        """Try a set of heuristics to click cookie/consent/close buttons if present."""
        if not self.driver:
            return False
        texts = ['accept', 'agree', 'got it', 'allow', 'yes, i agree', 'close', 'ok', 'موافق']
        clicked = False
        try:
            # Try text-based buttons using XPath (case-insensitive)
            for t in texts:
                try:
                    btns = self.driver.find_elements(By.XPATH, f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{t}')]")
                    if btns:
                        for b in btns:
                            try:
                                b.click()
                                clicked = True
                                logging.info(f"Clicked cookie/modal button with text '{t}'.")
                                time.sleep(0.5)
                                break
                            except Exception:
                                continue
                    if clicked:
                        break
                except Exception:
                    continue

            # Try generic close buttons (by class or aria-label)
            if not clicked:
                try:
                    close_btns = self.driver.find_elements(By.XPATH, "//button[contains(@class,'close') or contains(@aria-label,'close') or contains(@aria-label,'dismiss')]")
                    for cb in close_btns:
                        try:
                            cb.click()
                            clicked = True
                            logging.info("Clicked a close/dismiss button.")
                            break
                        except Exception:
                            continue
                except Exception:
                    pass

        except Exception:
            pass
        return clicked


# ==============================================================================
# 2. THE DUBIZZLE SCRAPER (CHILD CLASS) - FINAL VERSION
#    - Combines resilient Selenium navigation with your proven BeautifulSoup parsing.
# ==============================================================================
class DubizzleScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Dubizzle"

    def _wait_for_page_load(self, timeout=20):
        """Waits for the page to reach the 'complete' readyState."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(1)
            return True
        except TimeoutException:
            logging.warning(f"Page load timed out after {timeout} seconds.")
            return False

    # === YOUR BEAUTIFULSOUP HELPER FUNCTION - This is the key fix ===
    def _get_attribute(self, soup, label):
        """Safely finds an attribute on a Dubizzle page by its label span."""
        try:
            label_element = soup.find("span", string=label)
            if label_element:
                value_element = label_element.find_next_sibling("span")
                if value_element:
                    return value_element.text.strip()
            return "N/A"
        except Exception:
            return "N/A"

    def get_all_product_urls(self, search_query, pages_to_scrape=2):
        
        all_urls = []
        base_url = f"https://www.dubizzle.com.eg/en/mobile-phones-tablets-accessories-numbers/mobile-phones/q-{search_query.replace(' ', '-')}/"
        logging.info(f"---[{self.site_name}] Starting to gather URLs for '{search_query}'---")

        for page_num in range(1, pages_to_scrape + 1):
            url = f"{base_url}?page={page_num}&filter=new_used_eq_2"
            logging.info(f"Gathering URLs from page {page_num}")
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[aria-label="Listing"]')))
                listing_elements = self.driver.find_elements(By.CSS_SELECTOR, 'li[aria-label="Listing"] a')
                if not listing_elements:
                    logging.warning(f"No listings found on page {page_num}. Likely the last page.")
                    break
                for link_element in listing_elements:
                    href = link_element.get_attribute('href')
                    if href: all_urls.append(href)
            except TimeoutException:
                logging.warning(f"Timeout waiting for listings on page {page_num}.")
                break
        
        logging.info(f"---[{self.site_name}] Found {len(all_urls)} product URLs for '{search_query}'---")
        return all_urls

    def scrape_product_details(self, product_urls):
        """Scrapes product details using Selenium to load and BeautifulSoup to parse."""
        logging.info(f"---[{self.site_name}] Starting scrape for {len(product_urls)} products---")
        for i, url in enumerate(product_urls):
            logging.info(f"Scraping product {i+1}/{len(product_urls)}: {url}")
            try:
                self.driver.get(url)
                if not self._wait_for_page_load(timeout=25):
                    self.scraped_data.append({'listing_url': url, 'error': 'Page load failed', 'source': self.site_name})
                    continue

                # === USING BEAUTIFULSOUP FOR RELIABLE PARSING ===
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                # Extract data using the helper function with your proven logic
                product_data = {
                    'source': self.site_name,
                    'product_title': soup.find('h1').text.strip() if soup.find('h1') else 'N/A',
                    'brand': self._get_attribute(soup, "Brand"), 
                    'model': self._get_attribute(soup, "Model"),
                    'ram': self._get_attribute(soup, "RAM"),
                    'storage': self._get_attribute(soup, "Storage"),
                    'condition': self._get_attribute(soup, "Condition"),
                    'warranty': self._get_attribute(soup, "Warranty"),
                    'price': soup.find("span", {"aria-label": "Price"}).text.strip() if soup.find("span", {"aria-label": "Price"}) else 'N/A',
                    'location': soup.find("span", {"aria-label": "Location"}).text.strip() if soup.find("span", {"aria-label": "Location"}) else 'N/A',
                    'listing_url': url,
                    'timestamp': time.time()
                }
                
                self.scraped_data.append(product_data)
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                logging.error(f"A critical error occurred parsing {url}: {e}")
                self.scraped_data.append({'listing_url': url, 'error': str(e), 'source': self.site_name})

# 3. THE OPENSOOQ SCRAPER (FINAL VERSION WITH METHOD OVERRIDE)
# ==============================================================================
class OpenSooqScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "OpenSooq"

    #  METHOD OVERRIDING ===
   
    def _get_attribute_value(self, soup, attribute_name):
        """
        Helper function specifically for OpenSooq. It finds a product attribute
        by looking for its label in a <p> tag.
        """
        try:
            # Find the <p> tag that exactly matches the label text (e.g., "Brand")
            label_p = soup.find("p", string=attribute_name)
            if label_p:
                # The value is in the very next tag
                value_tag = label_p.find_next_sibling()
                if value_tag:
                    return value_tag.text.strip()
            return "N/A"
        except Exception:
            return "N/A"

    def get_all_product_urls(self, search_query, pages_to_scrape=2):
        
        all_urls = []
        formatted_query = search_query.replace(' ', '+')
        base_url = f"https://eg.opensooq.com/en/mobile-phones-tablets/mobile-phones"
        logging.info(f"---[{self.site_name}] Starting to gather URLs for '{search_query}'---")

        for page_num in range(1, pages_to_scrape + 1):
            url = f"{base_url}?term={formatted_query}&page={page_num}"
            logging.info(f"Gathering URLs from page {page_num}: {url}")
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.postListItemData"))
                )
                listing_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.postListItemData")
                if not listing_elements:
                    break
                for link_element in listing_elements:
                    href = link_element.get_attribute('href')
                    if href and href.startswith('http'):
                        all_urls.append(href)
            except TimeoutException:
                logging.warning(f"No listings found on page {page_num}. Likely the last page or a CAPTCHA.")
                break
        
        logging.info(f"---[{self.site_name}] Found {len(all_urls)} product URLs for '{search_query}'---")
        return all_urls

    def scrape_product_details(self, product_urls):
        logging.info(f"---[{self.site_name}] Starting scrape for {len(product_urls)} products---")
        for i, url in enumerate(product_urls):
            logging.info(f"Scraping product {i+1}/{len(product_urls)}: {url}")
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.TAG_NAME, 'h1')))
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                product_data = {
                    'source': self.site_name,
                    'product_title': soup.find('h1').text.strip() if soup.find('h1') else 'N/A',
                    'price': soup.find("div", {"data-id": "post_price"}).text.strip() if soup.find("div", {"data-id": "post_price"}) else 'N/A',
                    'location': soup.find("a", {"data-id": "location"}).text.strip() if soup.find("a", {"data-id": "location"}) else 'N/A',
                    'brand': self._get_attribute_value(soup, 'Brand'),
                    'model': self._get_attribute_value(soup, 'Model'),
                    'storage': self._get_attribute_value(soup, 'Storage Size'),
                    'condition': self._get_attribute_value(soup, 'Condition'),
                    'listing_url': url,
                    'timestamp': time.time()
                }
                self.scraped_data.append(product_data)
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                logging.error(f"Failed to parse details for {url}: {e}")
                self.scraped_data.append({'listing_url': url, 'error': str(e), 'source': self.site_name})
# ==============================================================================
# 4. MAIN ORCHESTRATOR AND SAVING FUNCTION - CORRECTED
# ==============================================================================
def save_combined_data(data, filename="used_phones_scraped_data.json"):
    """Saves a list of dictionaries to a single JSON file."""
    if not data:
        logging.warning("No data was collected from any scraper. No file will be saved.")
        return
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logging.info(f"Successfully saved a combined total of {len(data)} records to {filename}")

if __name__ == "__main__":
    search_queries = ["iphone 13", "samsung s22"]
    all_scraped_data = []

    # Instead of a list of INSTANCES, create a list of CLASSES ===
    scraper_classes_to_run = [
        DubizzleScraper,
        OpenSooqScraper 
    ]

    # Now, we create and destroy each scraper one by one in the loop.
    for ScraperClass in scraper_classes_to_run:
        scraper_instance = None # Initialize to ensure it exists for the 'finally' block
        try:
            # --- The instance is created HERE, right before it's needed ---
            scraper_instance = ScraperClass()
            
            logging.info(f"\n========== STARTING SCRAPER FOR: {scraper_instance.site_name} ==========")
            all_site_urls = []
            for query in search_queries:
                urls = scraper_instance.get_all_product_urls(query, pages_to_scrape=2)
                all_site_urls.extend(urls)
                time.sleep(random.uniform(2, 4))
            
            if all_site_urls:
                unique_urls = list(dict.fromkeys(all_site_urls))
                logging.info(f"Found {len(unique_urls)} unique URLs for {scraper_instance.site_name}.")
                scraper_instance.scrape_product_details(unique_urls)
                all_scraped_data.extend(scraper_instance.scraped_data)
        
        except Exception as e:
            # It's helpful to know which scraper failed
            site_name = ScraperClass.__name__
            logging.error(f"A critical error occurred with the {site_name} scraper: {e}")
        
        finally:
            # Always ensure the browser for THIS instance is closed before the next one starts
            if scraper_instance:
                scraper_instance.close()
            logging.info(f"========== FINISHED SCRAPER FOR: {ScraperClass.__name__} ==========\n")

    # After all scrapers have finished, save the combined data.
    save_combined_data(all_scraped_data)