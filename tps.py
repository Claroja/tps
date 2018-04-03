import requests
import time
from bs4 import BeautifulSoup
import json
import os
class Ops(object):
    def __init__(self,name,encoding = 'gbk',path="./"):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        self.name = name
        self.path = path
        self.encoding = encoding
        self.raw_data = None
        self.clean_data = None
        if not os.path.exists("./%s"%self.name):  # 如果是第一次下载则创建文件夹
            os.mkdir("./%s"%self.name)
            os.mkdir("./%s/temp"%self.name)

    def get_page_source(self, url = None):
        """
        获得网页的源代码
        :param url: (str)
        :return: (None) 将源码传给self.raw_data每次解析这个都会变
        """
        req = requests.get(url, headers =self.headers, timeout = 61)
        data = req.content
        self.raw_data = data.decode(self.encoding)

    def get_page_source2(self,url=None,down=100,interval = 1,driverpath="./"):
        """

        :param url: 输入要访问的网页
        :param down: 下拉的次数
        :param driverpath: 浏览器驱动的位置
        :return:
        """
        if os.path.exists("%s%s/raw.html"%(self.path,self.name)):  # 断点续传
            with open("%s%s/raw.html" % (self.path,self.name), 'r') as file:
                self.raw_data = file.read()
        else:
            from selenium import webdriver
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.common.keys import Keys

            browser = webdriver.Chrome("%schromedriver"%driverpath)  # 打开谷歌浏览器
            browser.get(url)  # 打开打开对应的网址


            action = ActionChains(browser)
            for i in range(1,down+1):
                # browser.execute_script("window.scrollBy(0, 100)")
                action.send_keys(Keys.ARROW_DOWN)
                # action.send_keys(Keys.UP)
                action.perform()
                time.sleep(interval)
            data = browser.page_source
            # self.raw_data = data.decode(self.encoding)
            self.raw_data = data
            with open('%s%s/raw.html'%(self.path,self.name),'w',encoding=self.encoding) as file:
                json.dump(self.raw_data,file)
        # browser.close()  # 关闭谷歌浏览器

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
        elif type == "json":
            self.clean_data = json.loads(self.clean_data)

    def get_page_data(self, get_page_data):
        """
        获得最终的数据,要重写获得最终数据的方法
        :param get_page_data: 重写的获得数据的方法
        :return:
        """
        self.page_data = get_page_data(self.clean_data)
        self.page_data["name"]=self.name

    def to_json(self):
        """
        获得文件,并保存为json
        :param path:
        :return:
        """
        with open('%s%s/all.json'%(self.path,self.name),'w',encoding='utf8') as file:
            json.dump(self.page_data,file)

    def get_img(self,url,name):
        """
        将图片保存在主目录(self.name)下的img文件夹下
        :param url:
        :param name:保存的文件名称
        :return:
        """
        r = requests.get(url,stream=True)
        with open("./%s/img/%s"%(self.name, name), 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)

class Tps(Ops):

    def __init__(self, name, encoding='gbk',path="./"):
        """
        初始化
        :param name: (str)爬虫的名字,用于新建文件夹,爬取结果有一列为name
        :param init_url: (str)初始化的url
        :param change_url: (str)改变的url
        """
        super().__init__(name, encoding=encoding,path = path)

        self.page_url = None
        self.roll_url = None
        self.all_url = []
        self.page_data = None
        self.all_data = []

    def get_roll_url(self,start,end,init_url,change_url = None):
        """
        获得最外层(roll)的所有连接
        :param start:(int) 开始的页面,url中类似page=1,注意有些网站第一页没有该参数
        :param end: (int)结束的页面,直接写url中的数字
        :return: (None) 拼贴好所有url直接传递给了self.roll_url
        """
        roll_url = [init_url]
        if change_url:
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

    def get_all_url(self,get_page_url,clean_def=None, interval = 2,type="html"):
        """
        获得该栏目下所有网站的url
        :param get_page_url: 重写的获得url的方法
        :param interval: 设置时间间隔
        :return:
        """
        for url in self.roll_url:
            self.get_page_source(url= url)
            self.clean(clean_def,type=type)
            self.get_page_url(get_page_url)
            self.all_url.extend(self.page_url)
            time.sleep(interval)
        with open('./%s/all_url.json' % self.name, 'w', encoding='utf8') as file:
            json.dump(self.all_url, file)

    def iter_all_url(self,url,get_page_url,deep=10,interval =2):
        li = []
        self.get_page_source(url =url)
        for i in range(1,deep+1):
            self.clean()
            self.get_page_url(get_page_url=get_page_url)
            li.extend(self.page_url["urls"])
            time.sleep(interval)
            try:
                self.get_page_source(self.page_url["next"])
            except:
                pass
        self.all_url = li
        with open('./%s/all_url.json' % self.name, 'w', encoding='utf8') as file:
            json.dump(self.all_url, file)

    def get_all_data(self, get_page_data,interval = 2):
        """
        获得最终数据,总流程
        :param get_page_data: 重写的获得数据的方法
        :param type: "all"是将每篇文章添加在list表中,在内存中处理,不推荐.
        :param interval: 设置时间间隔
        :return:
        """
        start = 0
        if os.path.exists("./%s/all_url.json"%self.name):  # 断点续传
            self.all_url = json.load(open("./%s/all_url.json" % self.name, 'r'))
            files = os.listdir("./%s/temp"%self.name)
            if len(files)>0:
                files = [int(file.split(".")[0]) for file in files]
                start = max(files)+2

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
                with open('./%s/log.txt'%self.name, 'a', encoding='utf8') as file:
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
        files = os.listdir("./%s/temp"%self.name)
        all_data = []
        for file in files:
            temp = json.load(open("./%s/temp/%s" % (self.name,file)))
            all_data.append(temp)
        json.dump(all_data, open("./%s/all.json"%self.name, 'w'))