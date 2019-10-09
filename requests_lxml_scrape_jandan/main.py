#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/25/19 8:10 PM
# @Author  : frank
# @File    : main.py
# @Software: PyCharm
import requests
from lxml import etree
import numpy as np
import base64
import datetime

number = 1
thres = 100

res = requests.get("https://jandan.net/ooxx")
page = etree.HTML(res.text)
current_page = page.xpath("//span[@class='current-comment-page']/text()")[0].replace("[","").replace("]","")
print(current_page)

hash_time = base64.b64encode((datetime.datetime.now().strftime("%Y%m%d")+"-"+str(number)).encode("utf-8")).decode("utf-8")
url = "https://jandan.net/ooxx/{}#comments".format(hash_time)
res = requests.get(url)
page = etree.HTML(res.text)
img_list = page.xpath(
    '//ol[@class="commentlist"]/li/div[1]/div/div[@class="text"]/p[1]/a[1]/@href')
oo_list = page.xpath(
    '//ol[@class="commentlist"]/li/div/div/div[@class="jandan-vote"]/span[@class="tucao-like-container"]/span/text()')

img_index = [int(x) > thres for x in oo_list]
["http:"+x for x in np.array(img_list)[img_index].tolist()]