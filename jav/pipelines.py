# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pickle
import gzip
from StringIO import StringIO
import urllib2
import os
import re
import scrapy
from scrapy.exceptions import DropItem
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JavPipeline(object):
    def __init__(self):
        settings = scrapy.utils.project.get_project_settings()
        self.output = settings.get('ROOT') + os.sep + "output"

    def process_item(self, item, spider):
        prefix = re.findall('[a-zA-Z]+', item['name'])[0]
        output_dir = self.output + os.sep + prefix + os.sep
        filename = item['name'] + '.torrent'
        self.down(item['image_link'], output_dir, item['name'] + '.jpg')
        for _url in item['torrent_download_link']:
            if self.down(_url, output_dir, filename):
                return item
        if item['md5'] == "":
            raise DropItem("Wrong item found: %s" % item)
        url = item['torrent']
        self.down(url, output_dir, filename)
        return item

    def down(self, url, output_dir, filename):
        try:
            request = urllib2.Request(url)
            request.add_header('Accept-encoding', 'gzip, deflate, sdch')
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36')
            response = urllib2.urlopen(request)
        except Exception, e:
            print "download error", filename, str(e.message)
            return False

        try:
            os.mkdir(output_dir)
        except Exception, e:
            print "file dir exists" + output_dir

        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else:
            buf = response.read()
            data = buf
        if data:
            file = open(output_dir + filename, 'wb')
            file.write(data)
            file.close()
            return True
        else:
            print "download data error" + filename
        return False

class duplicatesPipeline(object):
    def __init__(self):
        self.dumplicate_file = scrapy.utils.project.get_project_settings().get('ROOT') + os.sep + "dumplicate_records.txt"
        try:
            self.ids_seen = pickle.load(open(self.dumplicate_file, "r"))
        except:
            self.ids_seen = set()
        dispatcher.connect(self.on_spider_closed, signal=signals.spider_closed)

    def on_spider_closed(self, spider, reason):
        pickle.dump(self.ids_seen, open(self.dumplicate_file, "w"))

    def process_item(self, item, spider):
        if item['url'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['url'])
            return item
