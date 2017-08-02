# -*- encoding=utf-8 -*-
import json
import sys
import os
import pymongo
from pymongo import UpdateOne
import time
import conf

reload(sys)
sys.setdefaultencoding('utf-8')

conn = pymongo.MongoClient(conf.mongo_address)
meta = getattr(conn.product, conf.collect_name)

mongo_request = []

pre_time = time.time()
with open('request_result', 'r') as f:

    for line in f:
        line = line.strip()
        
        json_obj = json.loads(line)
        url = json_obj['url']
        
        update_queue.put(json_obj)
        
        mongo_request.append(UpdateOne({"wap_product_url":json_obj['url']}, {"$set": {"parameter_list":json_obj['parameter_list'], "product_introduction":json_obj['product_introduction']}}))

        if len(mongo_request) > 1000:
            try:
                result = meta.bulk_write(mongo_request)
                print "update data " + str(len(mongo_request))
                mongo_request = []
                print time.time() - pre_time
                pre_time = time.time()
            except Exception as e:
                print e
                print>>sys.stderr, "error", url

    if len(mongo_request) > 0:
        try:
            result = collection.bulk_write(mongo_request)
        except:
            print>>sys.stderr, "error", url
