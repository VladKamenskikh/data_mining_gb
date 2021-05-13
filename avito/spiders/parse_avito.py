import scrapy
from ..loaders import FlatLoader

class ParseAvitoSpider(scrapy.Spider):
    name = 'parse_avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/perm/kvartiry/prodam']

    _xpath_selectors = {
        "pagination": '//div[contains(@class, "pagination-hidden")]//a[@class="pagination-page"]/@href',
        "flat_url": '//div[contains(@class, "iva-item-body")]'
                    '//a[@data-marker="item-title"]/@href',
    }

    _xpath_data_selectors = {
        "title": '//span[@class="title-info-title-text"]/text()',
        "price": '//span[@itemprop="price"]/text()',
        "address": '//span[@class="item-address__string"]/text()',
        "parameters": '//div[@class="item-params"]//li[@class="item-params-list-item"]//text()',
        "seller_url": '//div[@data-marker="seller-info/name"]/a/@href'
    }


    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, self._xpath_selectors["pagination"], self.parse
        )
        yield from self._get_follow(
            response, self._xpath_selectors["flat_url"], self.flat_parse
        )

    def flat_parse(self, response):
        loader = FlatLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
