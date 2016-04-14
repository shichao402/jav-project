# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JavItem(scrapy.Item):
    url = scrapy.Field()
    magnet = scrapy.Field()
    md5 = scrapy.Field()
    torrent = scrapy.Field()
    name = scrapy.Field()
    torrent_download_link = scrapy.Field()
    image_link = scrapy.Field()
    release_date = scrapy.Field()
