import requests # type: ignore
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("parser_standard.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

token = open("groupproject_2/token.txt").read().strip()

brands_vk = []
with open("groupproject_2/brands_vk.txt") as f:
    for link in f:
        link = link.strip()
        brands_vk.append(link)

for brand_url in brands_vk:
    domain = brand_url.replace("https://vk.com/", "").replace("https://vk.ru/", "")
    domain = domain.replace("http://vk.com/", "").replace("http://vk.ru/", "")
    domain = domain.strip("/").strip()

    logging.info(f"Парсим: {domain}")

    response = requests.get("https://api.vk.com/method/wall.get", params={
        'access_token': token,
        'domain': domain,
        'count': 100,
        'v': '5.199'
    })

    data = response.json()

    filename = "groupproject_2/parsed/" + domain + ".json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logging.info(f"Сохранено в {filename}")