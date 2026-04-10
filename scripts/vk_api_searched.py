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

brands = []
with open("groupproject_2/brands.txt") as f:
    for link in f:
        link = link.strip()
        brands.append(link)

for domain in brands:
    logging.info(f"Ищем посты с WB в: {domain}")

    response = requests.get("https://api.vk.com/method/wall.search", params={
        'access_token': token,
        'domain': domain,
        'query': 'WB',
        'count': 100,
        'v': '5.199'
    })

    data = response.json()

    filename = "groupproject_2/parsed/" + domain + "_searched_wb.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logging.info(f"Сохранено в {filename}")