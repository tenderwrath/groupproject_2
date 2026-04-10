import time
import csv
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("groupproject_2/logs/proxy_links_parser.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

csv.field_size_limit(10000000)

posts = []
with open("groupproject_2/vk_eda/proxy_links.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames
    for row in reader:
        posts.append(row)

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--start-maximized")

browser = webdriver.Chrome(options=options)

out_file = open("groupproject_2/vk_eda/proxy_links_articles.csv", "w", encoding="utf-8", newline="")
writer = csv.DictWriter(out_file, fieldnames=list(columns) + ["final_url", "article"])
writer.writeheader()

logging.info("Постов: " + str(len(posts)))

for post in posts:
    url = post.get("article_or_link", "").strip()
    if not url:
        continue

    logging.info("Открываем " + url)
    browser.get(url)
    time.sleep(4)

    if "showcaptcha" in browser.current_url:
        print("прохождение капчи вручную")
        input()
        time.sleep(2)

    if "wildberries" not in browser.current_url:
        buttons = browser.find_elements(By.CSS_SELECTOR, "a, button")
        for b in buttons:
            try:
                text = (b.text or "").lower()
                href = (b.get_attribute("href") or "").lower()
            except Exception:
                continue
            if "wildberries" in href or "перейти" in text or "открыть" in text:
                try:
                    b.click()
                    time.sleep(3)
                    break
                except Exception:
                    pass

    if "showcaptcha" in browser.current_url:
        print("прохождение капчи вручную")
        input()
        time.sleep(2)

    final = browser.current_url

    article = ""
    m = re.search(r'/catalog/(\d+)/detail', final)
    if m:
        article = m.group(1)

    post["final_url"] = final
    post["article"] = article

    writer.writerow(post)
    out_file.flush()
    logging.info("Артикул " + article + ", URL " + final)

out_file.close()
browser.quit()