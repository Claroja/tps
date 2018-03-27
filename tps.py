import requests
import time
from bs4 import BeautifulSoup
import json
import os
class Ops(object):
    def __init__(self,name):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        self.name = name

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

    def get_page_data(self, get_page_data):
        """
        获得最终的数据,要重写获得最终数据的方法
        :param get_page_data: 重写的获得数据的方法
        :return:
        """
        self.page_data = get_page_data(self.clean_data)
        self.page_data["name"]=self.name

    def to_json(self,path="./"):
        file = open('%s%s/all.json'%(path,self.name),'w',encoding='utf8')
        json.dump(self.page_data,file)
        file.close()

    def get_img(self,url,name):
        r = requests.get(url, stream=True)
        with open("./%s/img/%s"%(self.name, name), 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)


class Tps(Ops):

    def __init__(self, name ):
        """
        初始化
        :param name: (str)爬虫的名字,用于新建文件夹,爬取结果有一列为name
        :param init_url: (str)初始化的url
        :param change_url: (str)改变的url
        """
        super().__init__(name)
        self.raw_data = None
        self.clean_data = None
        self.page_url = None
        self.roll_url = None
        self.all_url = []
        self.page_data = None
        self.all_data = []

    def get_roll_url(self,init_url, change_url,start,end):
        """
        获得最外层(roll)的所有连接
        :param start:(int) 开始的页面,url中类似page=1,注意有些网站第一页没有该参数
        :param end: (int)结束的页面,直接写url中的数字
        :return: (None) 拼贴好所有url直接传递给了self.roll_url
        """
        roll_url = [init_url]
        for i in range(start, (end+1)):
            url = change_url % i
            roll_url.append(url)
        self.roll_url = roll_url

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
        with open('./%s/all_url.json' % self.name, 'w', encoding='utf8') as file:
            json.dump(self.all_url, file)

    def get_all_data(self, get_page_data,interval = 0):
        """
        获得最终数据,总流程
        :param get_page_data: 重写的获得数据的方法
        :param type: "all"是将每篇文章添加在list表中,在内存中处理,不推荐.
        :param interval: 设置时间间隔
        :return:
        """
        start = 0
        if not os.path.exists("./%s"%self.name):
            os.mkdir("./%s"%self.name)
            os.mkdir("./%s/temp"%self.name)
        if os.path.exists("./%s"%self.name):
            files = os.listdir("./%s/temp"%self.name)
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
                with open('./%s/temp/%s.json'%(self.name,i),'w',encoding='utf8') as file:
                    json.dump(self.page_data, file)
                time.sleep(interval)
            except:
                with open('./log.txt', 'a', encoding='utf8') as file:
                    file.write(url+"\n")

    def get_all_img(self):
        all_data = json.load(open("./%s/all.json"%self.name, 'w'))
        for i in range(len(all_data)):
            for j in range(len(all_data[i]["img"])):
                name =str(i)+"-"+str(j)
                self.get_img(all_data[i]["img"][j],name)
            with open('./img/log.txt', 'a', encoding='utf8') as file:
                file.write(i + '\t' + all_data[i]['url'] + "\n")

    def add_json(self):
        """
        将所有的json文件整合到一起
        :return:
        """
        files = os.listdir("./temp/%s"%self.name)
        all_data = []
        for file in files:
            temp = json.load(open("./%s/temp/%s" % (self.name,file)))
            all_data.append(temp)
        json.dump(all_data, open("./%s/all.json"%self.name, 'w'))