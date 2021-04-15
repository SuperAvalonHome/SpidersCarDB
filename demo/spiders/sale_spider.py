#coding:utf-8

import scrapy
import string, os, sys, json, re

from Tools import Tools
from MysqlDB import MysqlDB
from configobj import ConfigObj
from scrapy.spider import BaseSpider

class Sale_Spider(BaseSpider):
    name = "sale"
    db = None
    tools = None
    debug = True
    level_id = ''
    attributes = []
    domain = "http://www.autohome.com.cn/"
    allowed_domains = ["autohome.com.cn"]
    
    start_urls = [
        "http://www.autohome.com.cn/b/",
    ]
    
    # parse start
    def parse(self, response):
        urls = []
        handle = open("./files/sale_urls.log", 'r')
        
        while True:
            url = handle.readline()
            if len(url) == 0:
                break
            urls.append(url[0:-1])
        
        handle.close()
        
        self.tools = Tools()
        
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_page)
        
        
    def parse_page(self, response):
        re_url = re.findall(r"(\d+)", response.url)
        model_id = re_url[0]
        
        re_cars = re.findall(r"<a href=\""+model_id+"\/(\d+)\/options\.html\">.*?<\/a>", response.body)
        if len(re_cars) > 0 :
            for car_id in re_cars : 
                option_url = self.tools.build_sub_option_url(model_id, car_id)
                self.tools.save_file("sub_option_urls.log", option_url)
        
    
        
        