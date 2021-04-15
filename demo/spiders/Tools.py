#coding:UTF-8

import re, os, sys, json, time, string

class Tools:

    domain = "http://www.autohome.com.cn/"

    
    def build_option_url(self, car_id):
        return self.domain + str(car_id) + "/options.html"
        
        
    def build_sub_option_url(self, model_id, car_id):
        return self.domain + str(model_id) + "/" + str(car_id) + "/options.html"
        

    def save_file(self, file, content):
        handle = open("./files/" + file, 'a')
        handle.write(content + "\n")
        handle.close()        
        
        
    def write_log(self, action, url = ''):
        curr_time = time.strftime('%Y-%m-%d %H:%I:%S', time.localtime(time.time()))
        
        handle = open("./files/run.log", 'a')
        if url != '' :
            handle.write(url + "\n")
        handle.write("\t" + curr_time + "\t" + action + "\n")
        handle.close()