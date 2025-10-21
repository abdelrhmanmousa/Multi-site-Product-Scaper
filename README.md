# 🧠 Multi-Site Electronics Scraper

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Selenium](https://img.shields.io/badge/built%20with-Selenium-orange.svg)

An automated web scraper designed to gather product data for **used electronics** from multiple online marketplaces in Egypt.  
It uses **Selenium** to control a web browser and **BeautifulSoup** to parse HTML, consolidating all findings into a single, structured JSON file.

---

## ✨ Features

- 🔄 **Multi-Site Scraping**: Simultaneously scrapes data from **Dubizzle** and **OpenSooq**.  
- 🧩 **Modular Design**: Each scraper is a separate class, making it easy to maintain or add new sites.  
- 🕵️ **Anti-Detection Measures**: Implements user-agent rotation and Selenium best practices to minimize detection.  
- 📦 **Structured Output**: Saves all scraped data in a unified JSON format.  
- ⚙️ **Configurable**: Easily change search queries and number of pages to scrape.  

---

## 🌐 Websites Scraped

### **1. Dubizzle (Egypt)**

| Field | Example |
|-------|----------|
| product_title | iPhone 13 Pro Max 256GB |
| price | EGP 25,000 |
| location | Maadi, Cairo |
| brand | Apple |
| model | iPhone 13 Pro Max |
| ram | 6 GB |
| storage | 256 GB |
| condition | Used |
| warranty | No |
| listing_url | https://dubizzle.com.eg/en/ad/... |

---

### **2. OpenSooq (Egypt)**

| Field | Example |
|-------|----------|
| product_title | Samsung S22 Ultra for sale |
| price | 22,500 EGP |
| location | New Cairo - 1st Settlement |
| brand | Samsung |
| model | Galaxy S22 Ultra |
| storage | 256 GB |
| condition | Used |
| listing_url | https://eg.opensooq.com/en/search/... |

---

## 💻 Tech Stack

- **Python 3**
- **Selenium** – For browser automation and dynamic content loading  
- **BeautifulSoup4** – For HTML parsing  
- **WebDriver-Manager** – To manage browser drivers automatically  

---

## 🚀 Getting Started

Follow these steps to run the scraper locally.

### **Prerequisites**

- Python **3.8+**
- Google Chrome browser
- Git installed

---

### **Installation & Setup**

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/your-repository-name.git
   cd your-repository-name
2. **Create and activate a virtual environment**
    ```bash

    python -m venv venv
    .\venv\Scripts\activate





3. **Create a requirements.txt file**

    selenium
    webdriver-manager
    beautifulsoup4


4. **Install the dependencies**
   ```bash

    pip install -r requirements.txt

## 🏃‍♀️ How to Run the Script

1. **Configure your search**

Open the main script (e.g., scraper.py) and navigate to the bottom block:

if __name__ == "__main__":
    # ---== CONFIGURE YOUR SCRAPE HERE ==---
    search_queries = ["iphone 13", "samsung s22", "pixel 6"]
    PAGES_TO_SCRAPE_PER_QUERY = 2
    # ---==============================---

    for query in search_queries:
        urls = scraper_instance.get_all_product_urls(query, pages_to_scrape=PAGES_TO_SCRAPE_PER_QUERY)
        # ...


2. **Run the script**
   ```bash

    python your_script_name.py


# The script will display progress in your console.

📄 Output

# After completion, the script will generate a file:

📁 final_scraped_data.json

# This file contains all scraped products in JSON format.

Example Output:
```
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
```
📜 License

This project is licensed under the MIT License – see the LICENSE
 file for details.
