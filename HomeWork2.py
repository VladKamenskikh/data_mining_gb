"""
Источник https://gb.ru/posts/
Необходимо обойти все записи в блоге и извлечь из них информацию следующих полей:
url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)

Структуру сохраняем в MongoDB
"""
import time
import typing
import requests
from urllib.parse import urljoin
from pymongo import MongoClient
import bs4
import datetime


class GbBlogParse:
    def __init__(self, start_url, collection):
        self.time = time.time()
        self.start_url = start_url
        self.collection = collection
        self.done_urls = set()
        self.tasks = []
        start_task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(start_task)
        self.done_urls.add(self.start_url)
        self.none_func = lambda *_, **__: None

    def _get_response(self, url, *args, **kwargs):
        if self.time + 1 < time.time():
            time.sleep(1)
        response = requests.get(url, *args, **kwargs)
        self.time = time.time()
        print(url)
        return response

    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_urls:
            return self.none_func
        self.done_urls.add(url)
        return task

    def task_creator(self, url, tags_list, callback):
        links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in tags_list
            if itm.attrs.get("href")
        )
        for link in links:
            task = self.get_task(link, callback)
            self.tasks.append(task)

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.task_creator(
            url, post_wrapper.find_all("a", attrs={"class": "post-item__title"}), self.parse_post
        )

    def parse_comments(self, url, commentable_id):
        url_path = f'/api/v2/comments?commentable_type=Post&commentable_id={commentable_id}&order=desc'
        response = self._get_response(urljoin(url, url_path))
        comments_list = []
        for comment in response.json():
            comments_list.append(
                {
                    'author': comment['comment']['user']['full_name'],
                    'text': comment['comment']['body']
                }
            )
        return comments_list

    def parse_post(self, url, soup):
        title = soup.find("h1", class_='blogpost-title').get_text()
        image = soup.find("img").get("src")
        post_datetime = soup.find("time", class_="text-md text-muted m-r-md").get("datetime")
        author_name = soup.find('div', itemprop='author').get_text(strip=True)
        author_href = soup.find('div', class_='col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v').find('a').get(
            'href')
        comments_list = self.parse_comments(url, soup.find("comments").get("commentable-id"))

        post_data = {
            "url": url,
            "title": title,
            "image": image,
            "date": datetime.datetime.strptime(post_datetime, '%Y-%m-%dT%H:%M:%S%z'),
            "author_name": author_name,
            "author_href": urljoin(url, author_href),
            "comments": comments_list
        }
        return post_data

    def run(self):
        for task in self.tasks:
            task_result = task()
            if isinstance(task_result, dict):
                self.save(task_result)

    def save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    collection = MongoClient()["gb_parse_blogs"]["gb_blog"]
    parser = GbBlogParse("https://gb.ru/posts", collection)
    parser.run()
