#coding:utf-8
import scrapy
import MySQLdb
import string, os, sys, json, re
from configobj import ConfigObj
from scrapy.spider import BaseSpider

class Test_Spider(BaseSpider):
    name = "test"
    conn = None
    level_id = 'b'
    attributes = []
    allowed_domains = ["autohome.com.cn"]
    
    start_urls = [
        "http://www.autohome.com.cn/472/options.html"
    ]
    
    def start_requests(self):
        urls = [
            "http://www.autohome.com.cn/472/options.html",
            "http://www.autohome.com.cn/18/options.html",
            "http://www.autohome.com.cn/740/options.html"
        ]
        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

        
    # parse document
    def parse(self, response):
        print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        
        print response.url
        #return Request(url=("http://www.163.com"), callback=self.just_test2)    
    