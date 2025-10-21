# Multi-Site Electronics Scraper
![alt text](https://img.shields.io/badge/python-3.8+-blue.svg)
![alt text](https://img.shields.io/badge/license-MIT-green.svg)
![alt text](https://img.shields.io/badge/built%20with-Selenium-orange.svg)
An automated web scraper designed to gather product data for used electronics from multiple online marketplaces in Egypt. It uses Selenium to control a web browser and BeautifulSoup to parse HTML, consolidating all findings into a single, structured JSON file.
✨ Features
Multi-Site Scraping: Simultaneously scrapes data from Dubizzle and OpenSooq.
Modular Design: Each scraper is a separate class, making it easy to maintain or add new sites.
Anti-Detection Measures: Implements user-agent rotation and other Selenium best practices to minimize the chance of being blocked.
Structured Output: Saves all scraped data in a clean, unified JSON format.
Configurable: Easily change search queries and the number of pages to scrape.
Websites Scraped
The script currently targets the following websites:
1. Dubizzle (Egypt)
Field	Example
product_title	iPhone 13 Pro Max 256GB
price	EGP 25,000
location	Maadi, Cairo
brand	Apple
model	iPhone 13 Pro Max
ram	6 GB
storage	256 GB
condition	Used
warranty	No
listing_url	https://dubizzle.com.eg/en/ad/...
2. OpenSooq (Egypt)
Field	Example
product_title	Samsung S22 Ultra for sale
price	22,500 EGP
location	New Cairo - 1st Settlement
brand	Samsung
model	Galaxy S22 Ultra
storage	256 GB
condition	Used
listing_url	https://eg.opensooq.com/en/search/...
💻 Tech Stack
Python 3
Selenium: For browser automation and dynamic content loading.
BeautifulSoup4: For robust HTML parsing.
WebDriver-Manager: To automatically manage the correct browser driver.
🚀 Getting Started
Follow these instructions to get the project up and running on your local machine.
Prerequisites
Python 3.8 or newer.
Google Chrome browser installed.
Git installed.
Installation & Setup
Clone the repository:
code
Bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
Create and activate a virtual environment (Recommended):
Windows:
code
Cmd
python -m venv venv
.\venv\Scripts\activate
macOS / Linux:
code
Bash
python3 -m venv venv
source venv/bin/activate
Create a requirements.txt file:
This file lists all the Python libraries needed for the project. Create a file named requirements.txt and add the following lines:
code
Code
selenium
webdriver-manager
beautifulsoup4
Install the required libraries:
code
Bash
pip install -r requirements.txt
🏃‍♀️ How to Run the Script
Configure your search:
Open the main script file (e.g., scraper.py) and navigate to the if __name__ == "__main__": block at the bottom. You can customize two key variables:
search_queries: A list of product names you want to search for.
pages_to_scrape: The number of search result pages to process for each query.
code
Python
if __name__ == "__main__":
    # ---== CONFIGURE YOUR SCRAPE HERE ==---
    search_queries = ["iphone 13", "samsung s22", "pixel 6"]
    PAGES_TO_SCRAPE_PER_QUERY = 2
    # ---==============================---

    # (The rest of the script)
    # ...
    for query in search_queries:
        urls = scraper_instance.get_all_product_urls(query, pages_to_scrape=PAGES_TO_SCRAPE_PER_QUERY)
        # ...
Execute the script:
Run the script from your terminal (with the virtual environment activated).
code
Bash
python your_script_name.py
The script will print its progress to the console.
📄 Output
After the script finishes, it will generate a final_scraped_data.json file in the root directory. This file contains a list of all the products found, with each product represented as a JSON object.
Example JSON Output:
code
JSON
[
    {
        "source": "Dubizzle",
        "product_title": "iPhone 13 Pro Max 256GB",
        "brand": "Apple",
        "model": "iPhone 13 Pro Max",
        "ram": "6 GB",
        "storage": "256 GB",
        "condition": "Used",
        "warranty": "No",
        "price": "EGP 25,000",
        "location": "Maadi, Cairo",
        "listing_url": "https://www.dubizzle.com.eg/en/ad/some-product-url.html",
        "timestamp": 1761081600.12345
    },
    {
        "source": "OpenSooq",
        "product_title": "Samsung S22 Ultra for sale",
        "price": "22,500 EGP",
        "location": "New Cairo - 1st Settlement",
        "brand": "Samsung",
        "model": "Galaxy S22 Ultra",
        "storage": "256 GB",
        "condition": "Used",
        "listing_url": "https://eg.opensooq.com/en/search/some-other-url",
        "timestamp": 1761081605.67890
    }
]
📜 License
This project is licensed under the MIT License. See the LICENSE file for details.
