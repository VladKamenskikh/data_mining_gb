from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hh.spiders.hh_parse import HhParseSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("hh.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HhParseSpider)
    crawler_process.start()
