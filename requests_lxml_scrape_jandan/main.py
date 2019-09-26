#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/25/19 8:10 PM
# @Author  : frank
# @File    : main.py
# @Software: PyCharm
import requests
from lxml import etree
import numpy as np

number = 8
thres = 100
res = requests.get("https://jandan.net/ooxx/page-{}#comments".format(number))
page = etree.HTML(res.text)
img_list = page.xpath(
    '//ol[@class="commentlist"]/li/div[1]/div/div[@class="text"]/p[1]/a[1]/@href')
oo_list = page.xpath(
    '//ol[@class="commentlist"]/li/div/div/div[@class="jandan-vote"]/span[@class="tucao-like-container"]/span/text()')

img_index = [int(x) > thres for x in oo_list]
np.array(img_list)[img_index].tolist()