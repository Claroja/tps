import requests
import time
from bs4 import BeautifulSoup
import json
import os

class Spider(object):

    def __init__(self,name,init_url,change_url):
        """
        初始化
        :param name: (str)爬虫的名字,用于新建文件夹,爬取结果有一列为name
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
        """
        获得最外层(roll)的所有连接
        :param start:(int) 开始的页面,url中类似page=1,注意有些网站第一页没有该参数
        :param end: (int)结束的页面,直接写url中的数字
        :return: (None) 拼贴好所有url直接传递给了self.roll_url
        """
        roll_url = [self.init_url]
        for i in range(start, (end+1)):
            url = self.change_url % i
            roll_url.append(url)
        self.roll_url = roll_url

    def get_page_source(self, url = None, encoding ="utf8"):
        """
        获得网页的源代码
        :param url: (str)
        :param encoding: (str) 国内网站不是"utf8"就是"gbk"
        :return: (None) 将源码传给self.raw_data每次解析这个都会变
        """
        req = requests.get(url, self.headers)
        data = req.content
        self.raw_data = data.decode(encoding)

    def clean(self,clean_def = None,type = "html"):
        """
        清洗源码,因为有些不是标准的html或者json
        :param clean_def: (def)传入自己写好的清洗函数
        :param type: (str)传入源码的格式,一般都是"html"和"json"
        :return: (None)
        """
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
        self.page_data["name"]=self.name

    def get_all_data(self, get_page_data,type = "all",interval = 2):
        if type != "all":
            os.mkdir("./%s"%self.name)

        for i in range(len(self.all_url)):
            url = self.all_url[i]
            try:
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
            except:
                file = open('./log.txt', 'a', encoding='utf8')
                file.write(url+"\n")
                file.close()

    def to_json(self,path="./"):
        file = open('%s%s.json'%(path,self.name),'w',encoding='utf8')
        json.dump(self.all_data,file)
        file.close()
