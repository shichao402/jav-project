# coding=utf8
import scrapy
import urlparse
import re
from datetime import datetime, date, time
import json
import logging
from jav.items import JavItem

class JavSpider(scrapy.Spider):
    name = "jav"
    allowed_domains = ["141jav.com"]

    start_urls = [
    ]

    def start_requests(self):
        if (scrapy.utils.project.get_project_settings().get('IS_GRAB_ALL') == True):
            for year in range(1998, datetime.now().year):
                for month in range(1, 13):
                    url = "http://www.141jav.com/month/%4d-%02d/" % (year, month);
                    yield scrapy.Request(url=url, callback=self.parse)
        else:
            url = "http://www.141jav.com/month/%4d-%02d/" % (datetime.now().year, datetime.now().month);
            yield scrapy.Request(url=url, callback=self.parse)

    def format_url(self, current_url, input_url):
        #current_url = current_url.rstrip("/")
        #input_url = input_url.rstrip("/")
        _url = urlparse.urljoin(current_url, input_url)
        return _url

    def get_dvd(self, response):
        item = JavItem()
        item['url'] = response.url
        image_link = response.xpath("//a[@rel='shadowbox']/@href").extract()[0]
        item['image_link'] = self.format_url(response.url, image_link)

        try:
            magnet = response.xpath("//textarea/text()").extract()[0]
        except Exception, e:
            magnet = ""
        item['magnet'] = magnet

        item['name'] = response.url.rstrip("/").split('/')[-1]

        
        temp = response.xpath("//div[@class='content-container']/text()").extract()
        for actor in temp:
            actor = re.findall('(?<=Actress\:).*(?=\n)', actor)
            if len(actor) > 0:
                actor = actor[0].strip(' \t\n\r')
                break
        item['actor'] = actor

        item['torrent_download_link'] = []
        for _url in response.xpath("//a[@class='dlbtn dl_tor2']/@href").extract():
            item['torrent_download_link'].append(self.format_url(response.url, _url))

        try:
            item['md5'] = re.findall('btih:([^&]+?)&', magnet)[0]
        except Exception:
            item['md5'] = ""
        item['torrent'] = "http://torcache.net/torrent/" + item['md5'] + ".torrent"
        item['release_date'] = response.meta['release_date']
        print item
        return item


    def parse(self, response):
        #解析dvd
        try:
            subdir = re.findall('(?<=\/)\d{4}-\d{2}(?=\/)', response.url)[0]
        except Exception, e:
            subdir = "none"
        dvds = response.xpath("//div[@class='artist-container']/a/@href").extract()
        for dvd in dvds:
            yield scrapy.Request(self.format_url(response.url, dvd), callback=self.get_dvd, meta={'release_date': subdir, 'crawl_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

        #分页搜索
        next_pages = response.xpath("//div[@class='pagination'][last()]/a[not(@class='disabled') and text()='"+"»".decode("utf-8")+"']/@href").extract()
        for next_page in next_pages:
            yield scrapy.Request(self.format_url(response.url, next_page), callback=self.parse)
        
