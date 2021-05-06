import pymongo
import scrapy
import re


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector_url, callback):
        for itm in response.css(selector_url):
            url = itm.attrib['href']
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            '.TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink',
            self.brand_parse
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response,
            '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
            self.brand_parse
        )
        yield from self._get_follow(
            response,
            'article.SerpSnippet_snippet__301t2 a.SerpSnippet_name__3F7Yu.blackLink',
            self.car_parse
        )

    @staticmethod
    def get_author_id(resp):
        marker = "window.transitState = decodeURIComponent"
        for script in resp.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return (
                        resp.urljoin(f"/user/{result[0]}").replace("auto.", "", 1)
                        if result
                        else None
                    )
            except TypeError:
                pass

    def car_parse(self, response):
        data = {
            "url": response.url,
            "title": response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
            "feature": [
                {
                    "name": itm.css(".AdvertSpecs_label__2JHnS::text").extract_first(),
                    "value": itm.css(".AdvertSpecs_data__xK2Qx::text").extract_first()
                    or itm.css(".AdvertSpecs_data__xK2Qx a::text").extract_first(),
                }
                for itm in response.css("div.AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX")
            ],
            "description": response.css(
                ".AdvertCard_descriptionInner__KnuRi::text"
            ).extract_first(),
            "img_list": [
                img.attrib["src"] for img in response.css(".PhotoGallery_photoImage__2mHGn")
            ],
            "author_id": self.get_author_id(response)
        }
        self.db_client["gb_parse_youla"]['youla'].insert_one(data)
