import time
import csv
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


INPUT_PATH = "groupproject_2/vk_eda/wb_links.csv"
OUTPUT_PATH = "groupproject_2/vk_eda/wb_links_articles.csv"
LOG_PATH = "groupproject_2/logs/wb_links_parser.log"
WAIT_SECONDS = 3


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger()


def get_article(url):
    patterns = [
        r'/catalog/(\d+)/detail',
        r'/product\?card=(\d+)',
        r'nm=(\d+)',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return ""


def read_csv(path):
    csv.field_size_limit(10000000)
    data = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        for r in reader:
            data.append(r)
    return data, columns


def make_driver():
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--start-maximized")
    return webdriver.Chrome(options=opts)


posts, columns = read_csv(INPUT_PATH)
out_columns = list(columns) + ["final_url", "article"]

browser = make_driver()

out_file = open(OUTPUT_PATH, "w", encoding="utf-8", newline="")
writer = csv.DictWriter(out_file, fieldnames=out_columns)
writer.writeheader()

log.info("Постов для обработки: " + str(len(posts)))

counter = 0
for post in posts:
    url = post.get("article_or_link", "").strip()
    if not url:
        continue

    log.info("Открываем " + url)

    final = ""
    try:
        browser.get(url)
        time.sleep(WAIT_SECONDS)
        final = browser.current_url
    except Exception as err:
        log.warning("Не удалось открыть: " + str(err))

    art = get_article(final)

    post["final_url"] = final
    post["article"] = art

    writer.writerow(post)
    out_file.flush()
    counter += 1

    log.info("Готово. Артикул " + art + ", URL " + final)

log.info("Готово. Обработано постов: " + str(counter))
out_file.close()
browser.quit()