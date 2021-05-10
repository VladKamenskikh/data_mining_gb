from json import loads as json_loads
from html2text import html2text
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose, Join


def clear_unicode(itm):
    return itm.replace("\xa0", "")


def get_description(data):
    description = html2text(json_loads(data)["description"]).replace('\n', ' ')
    return description


def get_employer(data):
    employer = "https://hh.ru" + data
    return employer


def get_title(data):
    title = "".join(itm for itm in data if itm != " ")
    return title


def get_fields(data):
    fields = "".join(data).split(sep=', ')
    return fields


class VacancyLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = Join("")
    title_out = TakeFirst()
    salary_in = MapCompose(clear_unicode)
    salary_out = Join('')
    description_in = MapCompose(get_description)
    description_out = TakeFirst()
    employer_in = MapCompose(get_employer)
    employer_out = TakeFirst()


class EmployerLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = Compose(get_title)
    title_out = TakeFirst()
    website_out = TakeFirst()
    fields_out = MapCompose(get_fields)
    description_in = Join("")
    description_out = TakeFirst()
