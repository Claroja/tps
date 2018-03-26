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
        req = requests.get(url, self.headers, timeout = 61)
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
        """
        获得该页的所有文章的url,这个方法要重写
        :param get_page_url: 传入重写的方法名
        :return:
        """
        self.page_url = get_page_url(self.clean_data)

    def get_all_url(self,get_page_url,interval = 0):
        """
        获得该栏目下所有网站的url
        :param get_page_url: 重写的获得url的方法
        :param interval: 设置时间间隔
        :return:
        """
        for url in self.roll_url:
            self.get_page_source(url= url)
            self.clean()
            self.get_page_url(get_page_url)
            self.all_url.extend(self.page_url)
            time.sleep(interval)

    def get_page_data(self, get_page_data):
        """
        获得最终的数据,要重写获得最终数据的方法
        :param get_page_data: 重写的获得数据的方法
        :return:
        """
        self.page_data = get_page_data(self.clean_data)
        self.page_data["name"]=self.name

    def get_all_data(self, get_page_data,type = None,interval = 0):
        """
        获得最终数据,总流程
        :param get_page_data: 重写的获得数据的方法
        :param type: "all"是将每篇文章添加在list表中,在内存中处理,不推荐.
        :param interval: 设置时间间隔
        :return:
        """
        start = 0
        if type != "all" and not os.path.exists("./%s"%self.name):
            os.mkdir("./%s"%self.name)
        if os.path.exists("./%s"%self.name):
            files = os.listdir("./%s"%self.name)
            files = [int(file.split(".")[0]) for file in files]
            start = max(files)+2
            self.all_url = json.load(open("./all_url.json",'r'))
        for i in range(start,len(self.all_url)):
            url = self.all_url[i]
            try:
                self.get_page_source(url=url)
                self.clean()
                self.get_page_data(get_page_data=get_page_data)
                self.page_data["url"]=url
                if type == "all":
                    self.all_data.append(self.page_data)
                else:
                    with open('./%s/%s.json'%(self.name,i),'w',encoding='utf8') as file:
                        json.dump(self.page_data, file)
                time.sleep(interval)
            except:
                with open('./log.txt', 'a', encoding='utf8') as file:
                    file.write(url+"\n")

    def to_json(self,path="./"):
        file = open('%s%s.json'%(path,self.name),'w',encoding='utf8')
        json.dump(self.all_data,file)
        file.close()

    def add_json(self):
        """
        将所有的json文件整合到一起
        :return:
        """
        files = os.listdir("./%s"%self.name)
        all_data = []
        for file in files:
            temp = json.load(open("./%s/%s" % (self.name,file)))
            all_data.append(temp)
        json.dump(all_data, open("./%s/all.json"%self.name, 'w'))