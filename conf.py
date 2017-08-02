# -*- coding: utf-8 -*-
import os
import sys

mongo_address = 'mongodb://10.85.39.45:8188/product'
collect_name = 'product_jdsku'

all_site = [
    {
        'name': 'wbiao',
        'data_type': 'html',
        'parameter_xpath': ['//div[@class="series v-995-770"]/ul/li/text()'],
        'mall_name': '万表'
    },
    {
        'name': 'mia',
        'data_type': 'html',
        'comment_xpath': ['//ul[@class="title yahei"]/li[2]/text()', '蜜芽圈\((\d+)\)'],
        'mall_name': '蜜芽'
    },
    {
        'name': 'gome',
        'data_type': 'html',
        'parameter_xpath' : ['//ul[@class="specbox"]','<span class="specinfo">(.+?)</span><span>','<span>(.+?)</span>'],
        'mall_name': '国美在线'
    },
    {   
        'name':'meilishuo',
        'data_type': 'json',
        'comment_xpath': ['result/rate/cRate','(.*)'],
        'mall_name': '美丽说'
    },
    {
        'name':'mogujie',
        'data_type': 'json',
        'parameter_xpath' : ['data/itemParams/info/set','key','value'],
        'mall_name': '蘑菇街'
    },
    {
        'name':'kaola',
        'data_type': 'html',
        'comment_xpath':['//b[@id="commentCounts"]/text()','(\d+)'],
        'good_rate_xpath':['//div[@class="goodpercent"]/i/text()','(\S+)'],
        'mall_name':'网易考拉海购'
    },
    {
        'name':'juanpi',
        'data_type': 'html',
        'parameter_xpath' : ['//div[@class="tm-goodsinfo"]/div[2]/table[1]','<td width="33%">(.+?)</td>'],
        "mall_name": '卷皮'
    },
    {
        'name': 'zol',
        'data_type': 'html',
        'parameter_xpath' : ['//*[@id="zp-tab-goods-params"]/table','<td class="zs-parameter-title">(.+?)</td>','<td class="zs-parameter-infor">(.+?)</td>', '">(.+?)</a>'],
        'mall_name': '中关村在线'
    },
    {
        'name': 'yhd',
        'data_type': 'html',
        'parameter_xpath' : ['//*[@id="detail_desc_content"]','<label>(.+?)</label>','</label>\r\n(.+?)\r\n</dd>'],
        "mall_name": '一号店'
    },
    {
        'name': 'vmall',
        'data_type': 'json',
        'parameter_xpath': ['data/@0/specificationList', 'name', 'value'],
        'mall_name': '华为商城'
    },
    {
        'name':'jd',
        'data_type':'html',
        'parameter_xpath': ['//div[@class="Ptable"]','<dt>(.+?)</dt>','<dd>(.+?)</dd>'], 
        'product_introduction_xpath':['//div[@class="p-parameter"]','<li title=".+?">(.+?)</li>'],
        'mall_name':'京东'
    }
]
