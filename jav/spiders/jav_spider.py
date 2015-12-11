# coding=utf8
import scrapy
import urlparse
import re
from scrapy.selector import Selector
from jav.items import JavItem
from scrapy.http import Request
import datetime


class JavSpider(scrapy.Spider):
    name = "jav"
    allowed_domains = ["141jav.com"]
    start_urls = [
        "http://www.141jav.com/latest/" + datetime.datetime.now().strftime("%Y-%m-%d") + '/'
    ]
    release_date = datetime.datetime.now().strftime("%Y-%m-%d")
    visited = set()
    output_dir = "output"

    def format_url(self, current_url, input_url):
        #current_url = current_url.rstrip("/")
        input_url = input_url.rstrip("/")
        _url = urlparse.urljoin(current_url, input_url)
        print [current_url, input_url]
        print _url
        return _url

    def parse_dvd(self, response):
        print 'parse_dvd ', response.url
        item = JavItem()
        sel = Selector(response)

        image_link = sel.xpath("//a[@rel='shadowbox']/@href").extract()[0]
        item['image_link'] = self.format_url(response.url, image_link)

        magnet = sel.xpath("//textarea/text()").extract()[0]
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
        item['release_date'] = self.release_date

        return item

    def parse_day_page(self, response):
        print 'parse_day_page ', response.url
        sel = Selector(response)
        dvds = sel.xpath("//div[@class='artist-container']/a/@href").extract()
        if len(dvds) == 0:
            yield Request(response.url, callback=self.parse_dvd)
        else:
            for dvd in dvds:
                _url = self.format_url(response.url, dvd)
                if _url not in self.visited:
                    yield Request(_url, callback=self.parse_dvd)
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
