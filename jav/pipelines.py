# coding=utf8
import os, sys, re, pickle, hashlib, StringIO, bencode, logging, requests, time
import scrapy
from scrapy.exceptions import DropItem
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
ids_seen = set()
class JavPipeline(object):
    def __init__(self):
        settings = scrapy.utils.project.get_project_settings()
        self.output = settings.get('ROOT') + os.sep + "output"
        self.delay = scrapy.utils.project.get_project_settings().get('DOWNLOAD_DELAY')

    def process_item(self, item, spider):
        prefix = re.findall('[a-zA-Z]+', item['name'])[0]
        output_dir = self.output + os.sep + prefix + os.sep
        if item['actor'] != "":
            fileprefix = item['name'] + '_' + item['actor']
        else:
            fileprefix = item['name']
        fileprefix = fileprefix.replace(" ", "_")
        torrent_filename = fileprefix + '.torrent'
        image_filename = fileprefix + '.jpg'
        
        if not self.download(item['image_link'], output_dir, image_filename):
            logging.log(logging.DEBUG, '图片下载失败: %s'.decode('utf-8') % (image_filename))
            return item

        for _url in item['torrent_download_link']:
            if self.download(_url, output_dir, torrent_filename):
                try:
                    torrent_file = None
                    torrent_file = open(output_dir + torrent_filename, "rb")
                    metainfo = bencode.bdecode(torrent_file.read())
                    ids_seen.add(item['name'])
                    return item
                except Exception as e:
                    try:
                        if torrent_file != None:
                            torrent_file.close()
                    except Exception as e:
                        pass
                    logging.log(logging.DEBUG, '下载文件解析失败: %s, %s'.decode('utf-8') % (output_dir + torrent_filename, str(e.message)))
                    try:
                        os.remove(output_dir + torrent_filename)
                    except Exception as e:
                        logging.log(logging.DEBUG, '下载文件删除失败: %s, %s'.decode('utf-8') % (output_dir + torrent_filename, str(e.message)))
                    continue
        
        return item

    def download(self, url, output_dir, filename):
        if not os.path.isdir(output_dir):
            if not os.makedirs(output_dir):
                logging.log(logging.DEBUG, '创建失败: %s'.decode('utf-8') % (output_dir))
        try:
            time.sleep(self.delay)
            r = requests.get(url)
            if r:
                with open(output_dir + filename, "wb") as file:
                    file.write(r.content)
                    return True
        except Exception, e:
            logging.log(logging.DEBUG, '下载失败: %s, %s'.decode('utf-8') % (filename, str(e.message)))
        return False

class duplicatesPipeline(object):
    def __init__(self):
        global ids_seen
        self.dumplicate_file = scrapy.utils.project.get_project_settings().get('ROOT') + os.sep + "dumplicate_records.txt"
        try:
            ids_seen = pickle.load(open(self.dumplicate_file, "r"))
        except:
            ids_seen = set()
        self.id_seen_count = len(ids_seen)
        dispatcher.connect(self.on_spider_closed, signal=signals.spider_closed)

    def on_spider_closed(self, spider, reason):
        self.save_ids()

    def save_ids(self):
        new_count = len(ids_seen)
        logging.log(logging.DEBUG, '新增抓取数量: %d'.decode('utf-8') % (new_count - self.id_seen_count))
        pickle.dump(ids_seen, open(self.dumplicate_file, "w"))

    def process_item(self, item, spider):
        if item['name'] in ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        return item
