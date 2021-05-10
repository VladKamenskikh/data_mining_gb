import pymongo
import scrapy
from ..loaders import VacancyLoader, EmployerLoader


class HhParseSpider(scrapy.Spider):
    name = 'hh_parse'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _xpath_selectors = {
        "pagination": "//div[@data-qa='pager-block']//a[@class='bloko-button']/@href",
        "vacancy": "//a[@data-qa='vacancy-serp__vacancy-title']/@href",
        "employer": "//a[@data-qa='vacancy-company-name']/@href",
    }
    _xpath_vacancy_data_selectors = {
        "title": "//h1//text()",
        "salary": "//p[@class='vacancy-salary']/span/text()",
        "description": "//script[@type='application/ld+json']/text()",
        "skills": "//span[@data-qa='bloko-tag__text']/text()",
        "employer_name": "//div[@class='company-header']//h1//text()",
    }
    _xpath_employer_data_selectors = {
        "employer_website": "//a[@data-qa='sidebar-company-site']/@href",
        "fields": "//div[class, 'bloko-text-emphasis']/p/text()",
        "employer_description": "//div[@class, 'company-description']//p/text()",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)


    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, self._xpath_selectors["pagination"], self.parse
        )
        yield from self._get_follow(
            response, self._xpath_selectors["vacancy"], self.vacancy_parse,
        )

    def vacancy_parse(self, response):
        loader = VacancyLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_vacancy_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
        yield from self._get_follow(
            response, self._xpath_selectors["employer"], self.employer_parse,
        )

    def employer_parse(self, response):
        loader = EmployerLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_employer_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
