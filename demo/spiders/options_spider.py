#coding:utf-8

import scrapy
import re, os, sys, json, time, string

from Tools import Tools
from MysqlDB import MysqlDB
from configobj import ConfigObj
from scrapy.spider import BaseSpider


class Options_Spider(BaseSpider):
    db = None
    debug = True
    name = "options"
    attributes = []
    allowed_domains = ["autohome.com.cn"]
    
    start_urls = [
        "http://www.autohome.com.cn/199/options.html"
    ]
    
    # parse start
    def parse(self, response):
        urls = []
        handle = open("./files/option_urls.log", 'r')
        
        while True:
            url = handle.readline()
            if len(url) == 0:
                break
            urls.append(url[0:-1])
        
        handle.close()
        
        self.tools = Tools()
        self.attributes = ConfigObj("./spiders/attributes.ini", encoding='UTF8')
        
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.main_parse)
        
    
    def main_parse(self, response):
        if self.debug:
            print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Parse Page xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            
        self.db = MysqlDB()
        self.db.connection()
        
        self.tools.write_log('Start Parse', response.url)
        #self.parse_option(response)
        self.parse_config(response)
        self.tools.write_log('Finish All')
        
        self.db.commit()
        self.db.close()
        
    
            
    #parse page
    def parse_option(self, response):
        
        self.tools.write_log('Parse Option...')
        option_js = re.findall(r"var option = (.*);", response.body)
        option_str = option_js[0].decode("GB2312")
        option_data = json.loads(option_str, encoding="UTF-8")
        option_configs = option_data["result"]["configtypeitems"]
        car_option = self.analysis_json("configitems", option_configs)
        
        self.save_option(car_option)
        self.tools.write_log('<Finish Option>')
        
    
    def parse_config(self, response):
    
        self.tools.write_log('Parse Config...')
        config_js = re.findall(r"var config = (.*);", response.body)
        config_str = config_js[0].decode("GB2312")
        config_data = json.loads(config_str, encoding="UTF-8")
        config_configs = config_data["result"]["paramtypeitems"]
        car_info = self.analysis_json("paramitems", config_configs)
        
        self.save_option(car_info)
        self.tools.write_log('<Finish Config>')
        
        
        
    #parse option
    def analysis_json(self, _key, _configs):
        car_option = dict()
        first_item = _configs[0][_key][0]["valueitems"]
        
        # init car_option keys
        for i in range(0, len(first_item)):
            _id = int(first_item[i]["specid"])
            car_option[_id] = dict()
        
        # set car_option data
        for i in range(0, len(_configs)):
            _configis = _configs[i][_key]

            for j in range(0, len(_configis)):
                _values = _configis[j]["valueitems"]
                for k in range(0, len(_values)):
                    _id = _values[k]["specid"]
                    
                    if i not in car_option[_id] :
                        car_option[_id][i] = dict()
                        car_option[_id][i]['items'] = dict()

                    if j not in car_option[_id][i]['items'] :
                        car_option[_id][i]['items'][j] = dict()

                    car_option[_id][i]['title'] = _configs[i]["name"]
                    car_option[_id][i]['items'][j]['title'] = _configis[j]["name"]
                    car_option[_id][i]['items'][j]['value'] = _values[k]["value"]
                    
        return car_option
        
        
    # save option
    def save_option(self, car_option):
        for car_id in car_option :
            print car_id           
            for i in car_option[car_id] :     
                fileds = dict()
                for j in car_option[car_id][i]['items'] :
                    _title = car_option[car_id][i]['items'][j]['title']
                    _filed = self.get_filed(_title)
                    if _filed != None :
                        if len(_filed) == 1:
                            fileds[_filed[0]] = car_option[car_id][i]['items'][j]['value']
                        elif len(_filed) == 2:
                            filed_titles = self.resolve_title(car_option[car_id][i]['items'][j]['value'])
                            for k in range(0, len(_filed)):
                                fileds[_filed[k]] = filed_titles[k]
                    
                table_title = car_option[car_id][i]['title']
                table_name = self.get_table_name(table_title)
                sql = self.build_sql(table_name, car_id, fileds)
                if self.debug:
                    print "************************************* SQL *********************************************"
                if self.debug:
                    print sql
                self.db.query(sql)


    def build_sql(self, table_name, car_id, fileds):
        if len(fileds) == 0:
            return ''
            
        sql = "INSERT INTO " + table_name + "(`ID`,"
        for key in fileds:
            sql += "`"+ key +"`,"
        sql = sql[0:-1] + ") VALUES(" + str(car_id) + ","
        
        for key in fileds:
            sql += '"' + self.parse_value(fileds[key]) + '",'
            
        return sql[0:-1] + ")"
        
        
    def get_filed(self, _title):
        
        filed_keys = []
        filed_titles = []
        
        if u"前/后" in _title:
            filed_titles.append(u"前"+_title[3:])
            filed_titles.append(u"后"+_title[3:])
        elif u"主/副" in _title:
            filed_titles.append(u"主"+_title[3:])
            filed_titles.append(u"副"+_title[3:])
        else:
            filed_titles.append(_title)
            
        for title in filed_titles:        
            for key in self.attributes:
                if key == 'tables' :
                    continue
                for sub_key in self.attributes[key]:
                    if title == self.attributes[key][sub_key]:
                        filed_keys.append(sub_key)
                        break
                    
        return filed_keys
    
    
    def resolve_title(self, _title):
        filed_values = []
        
        if u"/" in _title:
            _title = _title.replace(u"&nbsp;", "")
            _title = _title.replace(u"前", "")
            _title = _title.replace(u"后", "")
            _title = _title.replace(u"主", "")
            _title = _title.replace(u"副", "")
            filed_values = _title.split(u"/")
        else:
            filed_values.append(_title)
            filed_values.append("-")
        
        return filed_values
    
    
    def get_table_name(self, title):
        for key in self.attributes['tables']:
            if title == self.attributes['tables'][key]:
                return key
        return ''
        
        
    def parse_value(self, value):
        if value == u"●":
            return '1'
        elif value == u"○":
            return '2'
        elif value == u"-":
            return '0'
        else:
            return value
    