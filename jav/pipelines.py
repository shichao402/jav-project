# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import gzip
from StringIO import StringIO
import urllib2
import os
from scrapy.exceptions import DropItem

class JavPipeline(object):
    def __init__(self):
        self.ids_seen = set()
        self.output = "D:\\jav-project\\output"

    def process_item(self, item, spider):
        output_dir = self.output + os.sep + item['release_date'] + os.sep
        if item['name'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item['name'])
        self.ids_seen.add(item['name'])
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

