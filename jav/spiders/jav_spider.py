# coding=utf8
import scrapy
import urlparse
import re
import datetime
import json

from jav.items import JavItem

class JavSpider(scrapy.Spider):
    name = "jav"
    allowed_domains = ["141jav.com"]
    start_urls = [
        "http://www.141jav.com/month/2016-04/", "http://www.141jav.com/month/2016-03/", "http://www.141jav.com/month/2016-02/", "http://www.141jav.com/month/2016-01/", "http://www.141jav.com/month/2015-12/", "http://www.141jav.com/month/2015-11/", "http://www.141jav.com/month/2015-10/", "http://www.141jav.com/month/2015-09/", "http://www.141jav.com/month/2015-08/", "http://www.141jav.com/month/2015-07/", "http://www.141jav.com/month/2015-06/", "http://www.141jav.com/month/2015-05/", "http://www.141jav.com/month/2015-04/", "http://www.141jav.com/month/2015-03/", "http://www.141jav.com/month/2015-02/", "http://www.141jav.com/month/2015-01/", "http://www.141jav.com/month/2014-12/", "http://www.141jav.com/month/2014-11/", "http://www.141jav.com/month/2014-10/", "http://www.141jav.com/month/2014-09/", "http://www.141jav.com/month/2014-08/", "http://www.141jav.com/month/2014-07/", "http://www.141jav.com/month/2014-06/", "http://www.141jav.com/month/2014-05/", "http://www.141jav.com/month/2014-04/", "http://www.141jav.com/month/2014-03/", "http://www.141jav.com/month/2014-02/", "http://www.141jav.com/month/2014-01/", "http://www.141jav.com/month/2013-12/", "http://www.141jav.com/month/2013-11/", "http://www.141jav.com/month/2013-10/", "http://www.141jav.com/month/2013-09/", "http://www.141jav.com/month/2013-08/", "http://www.141jav.com/month/2013-07/", "http://www.141jav.com/month/2013-06/", "http://www.141jav.com/month/2013-05/", "http://www.141jav.com/month/2013-04/", "http://www.141jav.com/month/2013-03/", "http://www.141jav.com/month/2013-02/", "http://www.141jav.com/month/2013-01/", "http://www.141jav.com/month/2012-12/", "http://www.141jav.com/month/2012-11/", "http://www.141jav.com/month/2012-10/", "http://www.141jav.com/month/2012-09/", "http://www.141jav.com/month/2012-08/", "http://www.141jav.com/month/2012-07/", "http://www.141jav.com/month/2012-06/", "http://www.141jav.com/month/2012-05/", "http://www.141jav.com/month/2012-04/", "http://www.141jav.com/month/2012-03/", "http://www.141jav.com/month/2012-02/", "http://www.141jav.com/month/2012-01/", "http://www.141jav.com/month/2011-12/", "http://www.141jav.com/month/2011-11/", "http://www.141jav.com/month/2011-10/", "http://www.141jav.com/month/2011-09/", "http://www.141jav.com/month/2011-08/", "http://www.141jav.com/month/2011-07/", "http://www.141jav.com/month/2011-06/", "http://www.141jav.com/month/2011-05/", "http://www.141jav.com/month/2011-04/", "http://www.141jav.com/month/2011-03/", "http://www.141jav.com/month/2011-02/", "http://www.141jav.com/month/2011-01/", "http://www.141jav.com/month/2010-12/", "http://www.141jav.com/month/2010-11/", "http://www.141jav.com/month/2010-10/", "http://www.141jav.com/month/2010-09/", "http://www.141jav.com/month/2010-08/", "http://www.141jav.com/month/2010-07/", "http://www.141jav.com/month/2010-06/", "http://www.141jav.com/month/2010-05/", "http://www.141jav.com/month/2010-04/", "http://www.141jav.com/month/2010-03/", "http://www.141jav.com/month/2010-02/", "http://www.141jav.com/month/2010-01/", "http://www.141jav.com/month/2009-12/", "http://www.141jav.com/month/2009-11/", "http://www.141jav.com/month/2009-10/", "http://www.141jav.com/month/2009-09/", "http://www.141jav.com/month/2009-08/"
    ]

    def format_url(self, current_url, input_url):
        #current_url = current_url.rstrip("/")
        #input_url = input_url.rstrip("/")
        _url = urlparse.urljoin(current_url, input_url)
        return _url

    def parse_dvd(self, response):
        print 'parse_dvd ', response.url
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

        item['torrent_download_link'] = []
        for _url in response.xpath("//a[@class='dlbtn dl_tor2']/@href").extract():
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
        dvds = response.xpath("//div[@class='artist-container']/a/@href").extract()
        if len(dvds) == 0:
            yield scrapy.Request(response.url, callback=self.parse_dvd, meta={'release_date': subdir})
        else:
            for dvd in dvds:
                yield scrapy.Request(self.format_url(response.url, dvd), callback=self.parse_dvd, meta={'release_date': subdir})

        #分页搜索
        dvds_pages = response.xpath("//div[@class='pagination'][last()]/a/@href").extract()
        for dvds_page in dvds_pages:
            yield scrapy.Request(self.format_url(response.url, dvds_page), callback=self.parse_day_page)

    def parse(self, response):
        print 'parse ', response.url
        articles = response.xpath('//div[@class="dvd-container"]/a/@href').extract()
        if len(articles) == 0:
            yield scrapy.Request(response.url, callback=self.parse_day_page)
        else:
            for url in articles:
                yield scrapy.Request(self.format_url(response.url, url), callback=self.parse_day_page)
