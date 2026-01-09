from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random

# -------------------------
# 1️⃣ Setup Chrome
# -------------------------
options = Options()
options.add_argument("--headless")  # remove for debugging
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# -------------------------
# 2️⃣ Open Daraz page
# -------------------------
url = "https://www.daraz.com.np/sports-water-bottles/?from=hp_categories&q=still%2Bwater"
driver.get(url)

# -------------------------
# 3️⃣ Manually inspected classes
# -------------------------
container_selector = ".qmXQo"  # Product container class
title_selector = ".RfADt"      # Product title class
link_selector = "a"             # <a> tag inside container
image_selector = "img"          # Image inside container
price_selector = ".ooOxS"       # Price class
description_selector = ".buTCk" # Optional description
next_button_selector = ".ant-pagination-next"  # Pagination next button (inspect this manually if different)

# -------------------------
# 4️⃣ Wait for initial products
# -------------------------
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, container_selector))
    )
except TimeoutException:
    print("No products found! Exiting.")
    driver.quit()
    exit()

# -------------------------
# 5️⃣ Scrape products with pagination
# -------------------------
data = []

while True:
    containers = driver.find_elements(By.CSS_SELECTOR, container_selector)

    for container in containers:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", container)
            time.sleep(0.2)

            # Title
            try:
                title = container.find_element(By.CSS_SELECTOR, title_selector).text.strip()
            except:
                title = ""

            # Link
            try:
                link = container.find_element(By.CSS_SELECTOR, link_selector).get_attribute("href")
            except:
                link = ""

            # Image
            try:
                img_el = container.find_element(By.CSS_SELECTOR, image_selector)
                image = (
                    img_el.get_attribute("src") or
                    img_el.get_attribute("data-src") or
                    img_el.get_attribute("data-lazy-img") or
                    ""
                )
                if not image:
                    try:
                        div_el = container.find_element(By.CSS_SELECTOR, "div.picture-wrapper")
                        style = div_el.get_attribute("style")
                        if "url(" in style:
                            image = style.split('url("')[1].split('")')[0]
                    except:
                        pass
            except:
                image = ""

            # Price
            try:
                price = container.find_element(By.CSS_SELECTOR, price_selector).text.strip()
            except:
                price = ""

            # Description (optional)
            try:
                description = container.find_element(By.CSS_SELECTOR, description_selector).text.strip()
            except:
                description = ""

            # Append
            data.append({
                "title": title,
                "link": link,
                "image": image,
                "price": price,
                "description": description
            })

        except StaleElementReferenceException:
            continue

        time.sleep(random.uniform(0.1, 0.3))

    # -------------------------
    # Check for next page
    # -------------------------
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
        if "disabled" in next_button.get_attribute("class"):
            break  # No more pages
        else:
            next_button.click()
            time.sleep(3)  # Wait for next page to load
    except NoSuchElementException:
        break  # No pagination found, exit loop

# -------------------------
# 6️⃣ Save to Excel
# -------------------------
df = pd.DataFrame(data)
df.to_excel("daraz_products_all_pages.xlsx", index=False)

print(f"Scraped {len(data)} products successfully and saved to daraz_products_all_pages.xlsx")
driver.quit()
