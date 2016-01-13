# coding=utf8
import scrapy
import urlparse
import re
from scrapy.selector import Selector
from jav.items import JavItem
from scrapy.http import Request
import datetime
import json
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

class JavSpider(scrapy.Spider):
    name = "jav"
    allowed_domains = ["141jav.com"]
    start_urls = [
        "http://www.141jav.com/"
    ]
    visited = set()
    visited_fp = None
    output_dir = "output"

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        try:
            self.visited_fp = open('sitemap_visited.json', 'w+')
            self.visited = json.load()
        except Exception, e:
            self.visited_fp = open('sitemap_visited.json', 'w+')
            self.visited = set()

    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError

    def spider_closed(self, spider):
        json.dump(self.visited, self.visited_fp, default=self.set_default)
        self.visited_fp.close()

    def format_url(self, current_url, input_url):
        #current_url = current_url.rstrip("/")
        #input_url = input_url.rstrip("/")
        _url = urlparse.urljoin(current_url, input_url)
        return _url

    def parse_dvd(self, response):
        print 'parse_dvd ', response.url
        item = JavItem()
        sel = Selector(response)

        image_link = sel.xpath("//a[@rel='shadowbox']/@href").extract()[0]
        item['image_link'] = self.format_url(response.url, image_link)

        try:
            magnet = sel.xpath("//textarea/text()").extract()[0]
        except Exception, e:
            magnet = ""
        item['magnet'] = magnet

        item['name'] = response.url.rstrip("/").split('/')[-1]

        item['torrent_download_link'] = []
        for _url in sel.xpath("//a[@class='dlbtn dl_tor2']/@href").extract():
            item['torrent_download_link'].append(self.format_url(response.url, _url))

        try:
            item['md5'] = re.findall('btih:([^&]+?)&', magnet)[0]
        except Exception:
            item['md5'] = ""
        item['torrent'] = "http://torcache.net/torrent/" + item['md5'] + ".torrent"
        item['release_date'] = response.meta['release_date']
        return item

    def parse_day_page(self, response):
        print 'parse_day_page ', response.url
        try:
            subdir = re.findall('(?<=\/)\d{4}-\d{2}-\d{2}(?=\/)', response.url)[0]
        except Exception, e:
            subdir = ""
        sel = Selector(response)
        dvds = sel.xpath("//div[@class='artist-container']/a/@href").extract()
        if len(dvds) == 0:
            yield Request(response.url, callback=self.parse_dvd, meta={'release_date': subdir})
        else:
            for dvd in dvds:
                _url = self.format_url(response.url, dvd)
                if _url not in self.visited:
                    yield Request(_url, callback=self.parse_dvd, meta={'release_date': subdir})
                    self.visited.add(_url)

        #分页搜索
        dvds_pages = sel.xpath("//div[@class='pagination']/a/@href").extract()
        dvds_pages = {}.fromkeys(dvds_pages).keys()
        for dvds_page in dvds_pages:
            _url = self.format_url(response.url, dvds_page)
            if _url not in self.visited:
                yield Request(_url, callback=self.parse_day_page)
                self.visited.add(_url)

    def parse(self, response):
        print 'parse ', response.url
        sel = Selector(response)
        articles = sel.xpath('//div[@class="dvd-container"]/a/@href').extract()
        if len(articles) == 0:
            yield Request(response.url, callback=self.parse_day_page)
        else:
            for url in articles:
                _url = self.format_url(response.url, url)
                if _url not in self.visited:
                    yield Request(_url, callback=self.parse_day_page)
                    self.visited.add(_url)