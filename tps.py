import requests
import time
from bs4 import BeautifulSoup
import json
import os

class Spider(object):

    def __init__(self,name,init_url,change_url):
        """
        初始化
        :param init_url: (str)初始化的url
        :param change_url: (str)改变的url
        """
        self.headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        self.name = name
        self.init_url = init_url
        self.change_url = change_url
        self.raw_data = None
        self.clean_data = None
        self.page_url = None
        self.roll_url = None
        self.all_url = []
        self.page_data = None
        self.all_data = []

    def get_roll_url(self,start,end):
        roll_url = [self.init_url]
        for i in range(start, (end+1)):
            url = self.change_url % i
            roll_url.append(url)
        self.roll_url = roll_url

    def get_page_source(self, url = None, encoding ="utf8"):
        req = requests.get(url, self.headers)
        data = req.content
        self.raw_data = data.decode(encoding)

    def clean(self,clean_def = None,type = "html"):
        if clean_def == None:
            self.clean_data = self.raw_data
        else:
            self.clean_data = clean_def(self.raw_data)
        if type == "html":
            self.clean_data = BeautifulSoup(self.clean_data, 'lxml')

    def get_page_url(self, get_page_url):
        self.page_url = get_page_url(self.clean_data)

    def get_all_url(self,get_page_url,interval = 2):
        for url in self.roll_url:
            self.get_page_source(url= url, encoding="GBK")
            self.clean()
            self.get_page_url(get_page_url)
            self.all_url.extend(self.page_url)
            time.sleep(interval)

    def get_page_data(self, get_page_data):
        self.page_data = get_page_data(self.clean_data)

    def get_all_data(self, get_page_data,type = "all",interval = 2):
        if type != "all":
            os.mkdir("./%s"%self.name)
        for i in range(len(self.all_url)):
            url = self.all_url[i]
            self.get_page_source(url=url, encoding="gbk")
            self.clean()
            self.get_page_data(get_page_data=get_page_data)
            self.page_data["url"]=url
            if type == "all":
                self.all_data.append(self.page_data)
            else:
                file = open('./%s/%s.json'%(self.name,i),'w',encoding='utf8')
                json.dump(self.page_data, file)
                file.close()
            time.sleep(interval)

    def to_json(self,path="./"):
        file = open('%s%s.json'%(path,self.name),'w',encoding='utf8')
        json.dump(self.all_data,file)
        file.close()
