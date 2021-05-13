from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose
from urllib.parse import urljoin


def get_title(itm):
    return itm.replace('\xa0', '')


def get_url(itm):
<<<<<<< HEAD
    return urljoin("https://www.avito.ru", itm)


def get_price(itm):
    itm = itm.replace(" ", "")
=======
    return urljoin('https://www.avito.ru', itm)


def get_price(itm):
    itm = itm.replace(' ', '')
>>>>>>> 92657dc (Lesson 6 HW)
    return float(itm)


def get_address(itm):
<<<<<<< HEAD
    itm = itm.replace("\n ", "")
=======
    itm = itm.replace('\n ', '')
>>>>>>> 92657dc (Lesson 6 HW)
    return itm


def get_parameters(data):
<<<<<<< HEAD
    parameters_list_raw = [itm.replace(":", "") for itm in data if (itm != " ") and (itm != "\n  ")]
    parameters_list = [itm[:-1] if itm[-1] == " " else itm for itm in parameters_list_raw]
=======
    parameters_list_raw = [itm.replace(':', '').replace('\xa0', '') for itm in data if (itm != ' ') and (itm != '\n  ')]
    parameters_list = [itm[:-1] if itm[-1] == ' ' else itm for itm in parameters_list_raw]
>>>>>>> 92657dc (Lesson 6 HW)
    parameters_dict = dict(zip(parameters_list[::2], parameters_list[1::2]))
    return parameters_dict


class FlatLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = MapCompose(get_title)
    title_out = TakeFirst()
    seller_url_in = MapCompose(get_url)
    seller_url_out = TakeFirst()
    price_in = MapCompose(get_price)
    price_out = TakeFirst()
    address_in = MapCompose(get_address)
    address_out = TakeFirst()
    parameters_out = Compose(get_parameters)
