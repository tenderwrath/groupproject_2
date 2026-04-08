import time
import csv
import logging
import os 
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

 
csv_file = "groupproject_2/parsed/wb_data.csv" 


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("groupproject_2/logs/wildberries_data.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

def scroll_page_to_bottom(driver):
    current_height = 0
    while True:
        page_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script(f"window.scrollTo(0, {current_height});")
        current_height += 600
        time.sleep(0.05)

        if current_height > page_height:
            time.sleep(1)
            new_page_height = driver.execute_script("return document.body.scrollHeight")
            if new_page_height == page_height:
                break


def load_existing_cards(csv_file): # функция для проверки уже распарсенных карточек
    existing_cards = set()

    if not os.path.exists(csv_file):
        return existing_cards

    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            card_id = (row.get("id") or "").strip()
            search_url = (row.get("search_url") or "").strip()

            if card_id and search_url:
                existing_cards.add((card_id, search_url))
    return existing_cards


def get_card_data(card, search_url):
    data = {
        "id": "",
        "brand": "",
        "name": "",
        "price": "",
        "old_price": "",
        "discount": "",
        "rating": "",
        "reviews": "",
        "link": "",
        "search_url": search_url,
    } # структура строчки которую мы засунем в csvшку с распарсенными данными

    data["id"] = card.get_attribute("data-nm-id") or ""

    try:
        link_el = card.find_element(By.CSS_SELECTOR, "a.product-card__link")
        data["link"] = link_el.get_attribute("href") or ""
    except Exception:
        pass

    try:
        brand_el = card.find_element(By.CSS_SELECTOR, "span.product-card__brand")
        data["brand"] = brand_el.text.strip()
    except Exception:
        pass

    try:
        name_el = card.find_element(By.CSS_SELECTOR, "span.product-card__name")
        data["name"] = name_el.text.strip().lstrip("/ ").strip()
    except Exception:
        pass

    try:
        price_el = card.find_element(By.CSS_SELECTOR, "ins.price__lower-price")
        data["price"] = clean_number(price_el.text)
    except Exception:
        pass

    try:
        old_price_el = card.find_element(By.CSS_SELECTOR, "del")
        data["old_price"] = clean_number(old_price_el.text)
    except Exception:
        pass

    try:
        discount_el = card.find_element(By.CSS_SELECTOR, "span.percentage-sale")
        data["discount"] = discount_el.text.strip()
    except Exception:
        try:
            discount_el = card.find_element(By.CSS_SELECTOR, "p.product-card__tip--sale")
            data["discount"] = discount_el.text.strip()
        except Exception:
            pass

    try:
        rating_el = card.find_element(By.CSS_SELECTOR, "span.address-rate-mini")
        data["rating"] = rating_el.text.strip()
    except Exception:
        pass

    try:
        reviews_el = card.find_element(By.CSS_SELECTOR, "span.product-card__count")
        data["reviews"] = clean_number(reviews_el.text)
    except Exception:
        pass

    return data


def open_csv_for_append(csv_file):
    file_exists = os.path.exists(csv_file)
    csv_f = open(csv_file, "a")
    writer = csv.DictWriter(csv_f, fieldnames=["id", "brand", "name", "price", "old_price","discount", "rating", "reviews", "link", "search_url"])

    if not file_exists or os.path.getsize(csv_file) == 0:
        writer.writeheader()

    return csv_f, writer


def load_search_links(path):
    links = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            brand = line.strip() 
            if brand is not None:
                url = "https://www.wildberries.ru/catalog/0/search.aspx?search=" + brand
                links.append(url)
    return links

options = Options()

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options) 

wait = WebDriverWait(driver, 15)

existing_cards = load_existing_cards(csv_file)
links = load_search_links("groupproject_2/brands.txt")

total_new = 0

csv_file, writer = open_csv_for_append(csv_file)
 
logger.info(f"Всего ссылок для обработки: {len(links)}")



for search_url in links:
    logger.info('Обрабатываем ссылку: ' + search_url)

    driver.get(search_url)
    time.sleep(3)
    logger.info('Прокручиваем страницу вниз')
    scroll_page_to_bottom(driver)
    time.sleep(2)
    cards = driver.find_elements(By.CSS_SELECTOR, "article.product-card")
    logger.info('Найдено карточек: ' + len(cards))

    if not cards:
        logger.warning('Карточек нет, переходим дальше')
        continue

    added_for_url = 0
    skipped_for_url = 0

    for i, card in enumerate(cards, start=1): 
        data = get_card_data(card, search_url)

        if not data['id']:
            continue
        unique_key = (data["id"], data["search_url"])

        if unique_key in existing_cards:
            skipped_for_url += 1
            continue
        writer.writerow(data)
        existing_cards.add(unique_key)
        added_for_url += 1
        total_new += 1

        logger.info(f'Добавлен товар {data['id']}, {data['brand']},  {data['name']} Цена: {data['price']}, Рейтинг: {data['rating']}') 
        csv_file.flush()
        logger.info('По ссылке добавлено новых: ' + added_for_url+ ' пропущено уже существующих: '+ skipped_for_url) 
logger.info('Парсинг завершен, всего новых товаров: ' + total_new)
csv_file.close()
driver.quit()