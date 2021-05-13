from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from avito.spiders.parse_avito import ParseAvitoSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("avito.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(ParseAvitoSpider)
    crawler_process.start()
