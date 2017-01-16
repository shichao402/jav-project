# coding=utf8
import scrapy


class JavItem(scrapy.Item):
    url = scrapy.Field()
    magnet = scrapy.Field()
    md5 = scrapy.Field()
    actor = scrapy.Field()
    torrent = scrapy.Field()
    name = scrapy.Field()
    torrent_download_link = scrapy.Field()
    image_link = scrapy.Field()
    release_date = scrapy.Field()
