# -*- coding: utf-8 -*-
import sys
import os
import requests
import time
import threading
import pymongo
from pymongo import UpdateOne
import Queue
import conf
import HTMLParser
import re
import json
from lxml import html
import lxml.etree 
import guppy
import gc
hp = guppy.hpy()

reload(sys)
sys.setdefaultencoding('utf-8')

# connect mongodb, acquire mongodb collection
conn = pymongo.MongoClient(conf.mongo_address)
meta = getattr(conn.product, conf.collect_name)

# read config file write dict
name = sys.argv[1]
my_conf = [s for s in conf.all_site if name == s['name']][0]

isOver = False
cnt_put = 0
cnt_requests = 0

count_lock = threading.Lock()
update_lock = threading.Lock()
url_queue = Queue.Queue(200000)

update_url_list = []

fw_put_url = open('fw_put_url', 'a+')
fw_down_url = open('fw_down_url', 'a+')
fw_301 = open('fw_301', 'a+')
    
def request_url(line):
    """
    through requests.get(url) download web, if sucesss then parse web 
    """
    if line is None:
	pass
    
    line = line.strip()
    print 'url', line
    try:
        r = requests.get(line, headers={'Connection':'close'})
        
        if r.status_code == 200:
            print r.url
            parse(r)
    except Exception as e:
        print e

def parse(response):
    """
    parse web(html || json),   
    """
    
    status = response.status_code

    num_overseas = 0
    parameter_xpath_list = my_conf['parameter_xpath']

    if response.history != []:
        try:
            response = requests.get(response.url, headers={'Connection':'close'})
            if response.status_code == 200:
                num_overseas = 1 
                parameter_xpath_list = my_conf['global_parameter_xpath']
            else:
                print 'error'
        except Exception as e:
            print e
            return
    
    # web type is html
    if my_conf['data_type'] == 'html':

	# detail parameter list
        item = {}
        
        # string convert to html type 
        tree = html.fromstring(response.content)
        
	if len(my_conf['parameter_xpath']) == 3:
	    
            # parse tree, if format is error , return 
            try:
                html_all = tree.xpath(parameter_xpath_list[0])[0]

                # HTMLParser.unescape , original format convert to unicode -> utf-8  
                html_parser = HTMLParser.HTMLParser()
                res = html_parser.unescape(lxml.etree.tostring(html_all)).encode('utf-8')
                
                # through regular expression, acquire product field key & value
                key = re.findall(unicode(parameter_xpath_list[1],'utf8'),res,re.I|re.M)
                value = re.findall(unicode(parameter_xpath_list[2],'utf8'),res,re.I|re.M)

                parameter_list = []
                for i in xrange(len(key)):
                    temp_dict = {}
                    temp_dict[key[i]] = value[i]
                    parameter_list.append(temp_dict)
                item['parameter_list'] = parameter_list
            except Exception as e:
                print e

            if my_conf['name'] == 'jd': 

                try:
                    html_all = tree.xpath(my_conf['product_introduction_xpath'][0])[0]

                    html_parser = HTMLParser.HTMLParser()
                    res = html_parser.unescape(lxml.etree.tostring(html_all)).encode('utf-8')
                    key_value_list = re.findall(unicode(my_conf['product_introduction_xpath'][1],'utf8'),res,re.I|re.M)

                    product_introduction_list = []
                    for i in xrange(len(key_value_list)):
                        key_value_dict = {}
                        key_value_sp = key_value_list[i].split(u'：')
                        if 'href' in key_value_sp[1]:
                            content = re.search(unicode('<a.+?>(.+?)</a>'), key_value_list[i],re.I|re.M)
                            key_value_sp[1] = content.group(1)
                        key_value_dict[key_value_sp[0]] = key_value_sp[1]
                        product_introduction_list.append(key_value_dict)
                    item['product_introduction'] = product_introduction_list 
                except Exception as e:
                    print e
	
	item['url'] = response.url 
	item['name'] = sys.argv[1] 
        
        if "product_introduction" not in item and "parameter_list" not in item:
            return
        
        # acquire lock & add info to update_url_list & release lock
        global update_lock, update_url_list
        if "product_introduction" in item and "parameter_list" in item:
            
            if update_lock.acquire():
                update_url_list.append(
                    UpdateOne(
                        {"wap_product_url":item['url']}, 
                        {"$set":{
                            "parameter_list":item['parameter_list'],
                            "product_introduction":item['product_introduction'],
                            "is_overseas":num_overseas
                            }
                        }
                    )
                )
                update_lock.release()
        elif "parameter_list" in item:
            
            if update_lock.acquire():
                update_url_list.append(
                    UpdateOne(
                        {"wap_product_url":item['url']}, 
                        {"$set":{
                            "parameter_list":item['parameter_list'],
                            "is_overseas":num_overseas
                            }
                        }
                    )
                )
                update_lock.release()
        elif "product_introduction" in item:
            
            if update_lock.acquire():
                update_url_list.append(
                    UpdateOne(
                        {"wap_product_url":item['url']}, 
                        {"$set":{
                            "product_introduction":item['product_introduction'],
                            "is_overseas":num_overseas
                            }
                        }
                    )
                )
                update_lock.release()

        # write statistics file & flush file
        print >> fw_down_url, item['url']
        fw_down_url.flush()

        if is_overseas == 1:
            print >> fw_301, item['url']
        
    # web type is json
    if my_conf['data_type'] == 'json':
        pass


def update_mongo():
    """
    batch update mongodb data
    if list length > 5K, batch update mongodb 
    """
    
    fw_update_mongo = open('fw_update_mongo', 'a+')
    
    cnt_update = 5000
    cnt_current = 0
    isOver_update = False

    global isOver, update_lock, update_url_list
    
    while not isOver_update:
        
        # 10 seconds update_url_list not add + original data put is over = stop update mongodb   
        if cnt_current == len(update_url_list) and isOver:
            isOver_update = True
        
        cnt_current = len(update_url_list)
            
        if len(update_url_list) >= cnt_update:
            pre_time = time.time()
            if update_lock.acquire():
                print 'update_lock.acquire......................'
                update_url_temp_list = update_url_list[0:cnt_update]
                update_url_list = update_url_list[cnt_update:]
                update_lock.release()
            
            if len(update_url_temp_list) > 0:
                try:
                    result = meta.bulk_write(update_url_temp_list)
                except Exception as e:
                    print e
            print >> fw_update_mongo, 'time', time.time() - pre_time, cnt_update 
            fw_update_mongo.flush()
        else:
            time.sleep(10)
            gc.collect()
    if len(update_url_list) > 0:
        try:
            result = meta.bulk_write(update_url_list)
        except Exception as e:
            print e
        print >> fw_update_mongo, 'time', time.time() - pre_time, len(update_url_list) 
       
    
def put_url_from_ucp():
    """
    read data from ucp_dump tool, then put data to queue
    queue size < 2W, put data to queue, or else sleep 10 seconds 
    """
    
    print 'start put_url_from_ucp...'
    global isOver, url_queue, cnt_put 

    name = sys.argv[1]
    machine_id = int(sys.argv[2])
    view_id = sys.argv[3] 
    field = sys.argv[4] 
    start = int(sys.argv[5])
    end = int(sys.argv[6])

    ucp_dump_path = "ucp_dump/lib/ucp_dump"
    
    index = end
    
    while (index >= start):
        if url_queue.qsize() < 20000:
            
            ucp_scan = '%s scan %s %s %s' % (ucp_dump_path, view_id, index , field)
            r = os.popen(ucp_scan)
            all_res = r.readlines()
            
            cnt_put += len(all_res)
            print 'ucp_scan', ucp_scan
            print 'cnt_put', cnt_put
            print >> fw_put_url, machine_id, start, end, index, len(all_res), cnt_put 
            print >> fw_put_url , time.time() 
            fw_put_url.flush()

            for url in all_res:
                url = url.strip()
                url = json.loads(url)['wap_product_url']
                url_queue.put(url)

            index -= 1
        else: 
            time.sleep(10)
            
    isOver = True


class MyThread(threading.Thread):
    
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = "Thread-" + str(name)

    def run(self):

        global cnt_requests, count_lock, url_queue, isOver
        while not isOver:
            line = ""
            # acquire lock, get url from queue, release lock 
            if count_lock.acquire():
                if url_queue.qsize() > 0: 
                    line = url_queue.get()
                    cnt_requests += 1
                count_lock.release()
                print self.name, line
                # current url not empty, invoke request_url func 
                if line != "":
                    request_url(line)


# start multi thread crawl url
def download_parse_url():

    print 'start multi threading...'
    threadList = []
    for i in xrange(1, 50):
        my_thread = MyThread(i)
        threadList.append(my_thread)
    for t in threadList:
        t.start()
    for t in threadList:
        t.join()

if __name__ == "__main__":
    
    print 'start ...'
    print 'crawl site is  ', sys.argv[1]

    put_url_from_ucpThread = threading.Thread(target=put_url_from_ucp)
    download_parse_urlThread = threading.Thread(target=download_parse_url)
    update_mongo_urlThread = threading.Thread(target=update_mongo)
    put_url_from_ucpThread.start()
    download_parse_urlThread.start()
    update_mongo_urlThread.start()
    put_url_from_ucpThread.join()
    download_parse_urlThread.join()
    update_mongo_urlThread.join()
    
