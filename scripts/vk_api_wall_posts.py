import requests
import logging 
import json

logging.basicConfig( 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("parser_standard.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class vk_api_parser:
    def __init__(self, token, brand, method):
        self.token = token
        self.method = method
        self.brand = brand

    def delete_stuff_before_domain(self, brand_url):
        brand_url = brand_url.strip()
        brand_url = brand_url.replace("https://vk.com/", "")
        brand_url = brand_url.replace("http://vk.com/", "")
        brand_url = brand_url.replace("https://vk.ru/", "")
        brand_url = brand_url.replace("http://vk.ru/", "")
        brand_url = brand_url.strip("/")
        brand_url = brand_url.strip()
        return brand_url

    def save_to_json(self, data, group_domain):
        filename = "groupproject_2/parsed/" + str(group_domain) + ".json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Данные сохранены в {filename}")

    def fetch_date(self):
        logging.info(f"начинаем парсить паблик {self.brand}")
        group_domain = self.delete_stuff_before_domain(self.brand) 
        params_for_url = {'access_token': self.token,  'domain':group_domain, 'v':'5.199'} #v - версия, обяз параметр 
        response = requests.get(self.method, params=params_for_url)
        data = response.json() 
        self.save_to_json(data, group_domain)
        logging.info(f"Спарсили {self.brand}")
 
token = open("groupproject_2/token.txt").read()
brands = []
with open("groupproject_2/brands_vk.txt") as f:
    for link in f:
        link = link.strip()
        brands.append(link) 
method = "https://api.vk.com/method/wall.get"
for brand in brands:
    parser = vk_api_parser(token, brand, method)
    parser.fetch_date()