import json
import time
from pathlib import Path
import requests

"""
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    params = {
        "records_per_page": 20,
    }
    cat_name = 'parent_group_name'
    cat_code = 'parent_group_code'
    cat_url = 'https://5ka.ru/api/v2/categories/'

    def __init__(self, start_url: str, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path

    def _get_response(self, url, *args, **kwargs):
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(3)

    def run(self):
        categories = self._parse_cat(self.cat_url)

        for category in categories:
            products = []
            params = f"?categories={category['parent_group_code']}"
            url = f"{self.start_url}{params}"
            products.extend(list(self._parse(url)))

            result = {
                "name": category[self.cat_name],
                "code": category[self.cat_code],
                "products": products,
            }
            file_path = self.save_path.joinpath(f"{category['parent_group_name']}.json")
            self._save(result, file_path)

    def _parse_cat(self, url:str):
        while url:
            time.sleep(0.1)
            response = self._get_response(url, headers=self.headers, params=self.params)
            categories = response.json()
            return categories

    def _parse(self, url: str):
        while url:
            time.sleep(5)
            response = self._get_response(url, headers=self.headers, params=self.params)
            data = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product

    def _save(self, data: dict, file_path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == "__main__":
    save_path = get_save_path("categories")
    url = "https://5ka.ru/api/v2/special_offers/"
    parser = Parse5ka(url, save_path)
    parser.run()