from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from autoyoula.spiders.youla import YoulaSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule('autoyoula.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(YoulaSpider)
    crawler_process.start()
