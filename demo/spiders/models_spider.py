#coding:utf-8

import scrapy
import string, os, sys, json, re

from Tools import Tools
from MysqlDB import MysqlDB
from configobj import ConfigObj
from scrapy.spider import BaseSpider

class Models_Spider(BaseSpider):
    name = "models"
    
    db = None
    tools = None
    debug = True
    
    level_id = ''
    attributes = []
    
    domain = "http://www.autohome.com.cn/"
    allowed_domains = ["autohome.com.cn"]
    
    start_urls = [
        "http://www.autohome.com.cn/a00/"
    ]
    
    start_urls1 = [
        "http://www.autohome.com.cn/a00/",
        "http://www.autohome.com.cn/a0/",
        "http://www.autohome.com.cn/a/",
        "http://www.autohome.com.cn/b/",
        "http://www.autohome.com.cn/c/",
        "http://www.autohome.com.cn/d/",
        "http://www.autohome.com.cn/suv/",
        "http://www.autohome.com.cn/mpv/",
        "http://www.autohome.com.cn/s/"
    ]
    

    # parse document
    def parse(self, response):
    
        level = re.findall("\/(\w*?)\/$", response.url)
        self.level_id = level[0]
    
        self.db = MysqlDB()
        self.db.connection()
        self.tools = Tools()
        
        option = re.findall(r"<dt><a href=\".*?brand-(\d+)\.html[\w|\W]*?<ul class=\"rank-list-ul\">([\w|\W]*?)<\/ul>", response.body)
        for _html in option :
            if len(_html) > 0 :
                parent_id = _html[0]
                option_urls = self.sub_parse(parent_id, _html[1])
                for option_url in option_urls:
                    yield scrapy.Request(option_url, callback=self.parse_option_page)
    
        exit()
        self.db.commit()
        self.db.close()   
    
    
    def sub_parse(self, parent_id, html):
        
        option_urls = []
        _items = re.findall(r"<li data-state=\"\d+\" >([\w|\W]*?)<\/li>", html)
        for k in range(0, len(_items)):
            car_id = re.findall(r"<a class=\"red\" href=\"\/(\d+)\/.*?\">", _items[k])
            car_name = re.findall(r"\s+<h4.*?><a href=\".*?\">(.*?)<\/a>", _items[k])
            car_price = re.findall(r"<a class=\"red\" href=\".*?\">([\d|\.]+)-([\d|\.]+)", _items[k])
            if len(car_id) > 0 and len(car_name) > 0 and len(car_price[0]) == 2 :
                option_url = self.tools.build_option_url(car_id[0])
                self.tools.save_file("option_urls.log", option_url)
                #insert_sql = self.build_sql(car_id[0], parent_id, car_name[0], car_price[0][0], car_price[0][1])
                #self.db.query(insert_sql)
                option_urls.append(option_url)
                
        return option_urls


    def parse_option_page(self, response):
        sale_page = re.findall(r"<a href=\"(.*?)\" class=\"link-sale\">.*?<\/a>", response.body)
        
        if self.debug:
            print "************************************* Parse Option Page *********************************************"
        
        if len(sale_page) == 1:
            sale_url = self.domain + sale_page[0][1:]
            self.tools.save_file("sale_urls.log", sale_url)
    
        
          
    def build_sql(self, car_id, parent_id, car_name, min_price, max_price):
        sql = "INSERT INTO car_models (`id`,`level_id`,`company_id`,`parent_id`,`cn_name`,`en_name`,`min_price`,`max_price`)VALUES"
        sql += "(" + car_id + ",'" + self.level_id + "',0," + parent_id + ",'" + car_name.decode("GB2312") + "',''," + min_price + "," + max_price + ")"
        if self.debug:
            print "************************************* SQL *********************************************"
        if self.debug:
            print sql
        return sql