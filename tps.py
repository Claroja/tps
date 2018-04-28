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
        self.name = name # 爬虫名称，会在工作路径中新建相对应的文件夹
        self.path = path # 爬虫工作路径
        self.encoding = encoding
        self.raw_data = None
        self.clean_data = None
        if not os.path.exists("%s" % self.path):
            os.mkdir("%s" % self.path)

        if not os.path.exists("%s%s"%(self.path,self.name)):  # 如果是第一次下载则创建文件夹
            os.mkdir("%s%s"%(self.path,self.name))
            os.mkdir("%s%s/temp"%(self.path,self.name))

    def get_page_source(self, url = None):
        """
        获得网页的源代码，并将源代码放在raw_data里
        :param url: (str) 输入请求的网址
        :return: (str) 返回请求结果
        """
        req = requests.get(url, headers =self.headers, timeout = 61)
        data = req.content
        self.raw_data = data.decode(self.encoding)
        return self.raw_data

    def get_page_source2(self, pre=None,url=None,down=100,interval = 1,driverpath="./",mod="gui"):
        """
        使用selenium来获取源代码，针对各种疑难杂症。返回网页源代码并保存。
        :param pre: (def)是否要进行预处理，比如点击页面进入某个栏目，然后再下拉
        :param url: (str)输入要访问的网页
        :param down: (int)下拉的次数
        :param interval: (int) 每次下拉间隔
        :param driverpath: (str)浏览器驱动的位置
        :param mod: (str) gui模式是使用谷歌浏览器界面，否则是phantomJS无见面模式
        :return:
        """
        if os.path.exists("%s%s/raw.html"%(self.path,self.name)):  # 断点续传
            with open("%s%s/raw.html" % (self.path,self.name), 'r',encoding=self.encoding) as file:
                self.raw_data = file.read()
        else:
            from selenium import webdriver
            if mod=='gui':
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.webdriver.common.keys import Keys

                browser = webdriver.Chrome("%schromedriver"%driverpath)  # 打开谷歌浏览器
                browser.get(url)  # 打开打开对应的网址
                if pre:
                    pre(browser)
                action = ActionChains(browser)
                for i in range(1,down+1):
                    action.send_keys(Keys.ARROW_DOWN)
                    action.perform()
                    time.sleep(interval)
            else:
                browser = webdriver.PhantomJS()
                browser.get(url)  # 打开打开对应的网址
                if pre:
                    pre(browser)
                for i in range(1,down+1):
                    browser.execute_script("window.scrollBy(0, 300)")
                    time.sleep(interval)
            data = browser.page_source
            self.raw_data = data
            with open('%s%s/raw.html'%(self.path,self.name),'w',encoding=self.encoding) as file:
                file.write(data)
            return self.raw_data

    def clean(self,clean_def = None,type = "html"):
        """
        清洗源码,为json和bs4处理做预备。清洗时如果发现bs4和json都不能处理，则直接pass，在get_page_url里面使用正则处理
        :param clean_def: (def)传入自己写好的清洗函数
        :param type: (str)传入源码的格式,一般都是"html"和"json"
        :return: () 返回解析后的数据
        """
        if clean_def == None:
            self.clean_data = self.raw_data
        else:
            self.clean_data = clean_def(self.raw_data)
        if type == "html":
            self.clean_data = BeautifulSoup(self.clean_data, 'lxml')
        elif type == "json":
            self.clean_data = json.loads(self.clean_data)
        elif type == "pass":
            pass
        return self.clean_data
    def get_page_url(self, get_page_url):
        """
        获得该页的所有文章的url，要自己写这个方法
        :param get_page_url: (def)传入重写的方法名
        :return:(list) 返回当前页面的url
        """
        self.page_url = get_page_url(self.clean_data)
        return self.page_url

    def get_page_data(self, get_page_data):
        """
        获得最终的数据,要重写获得最终数据的方法
        :param get_page_data: (def) 重写的获得数据的方法
        :return:(dic) 返回当前页面的数据
        """
        self.page_data = get_page_data(self.clean_data)
        self.page_data["name"]=self.name
        return self.page_data

    def url_json(self):
        """
        保存当前页面的url
        :param path:
        :return:
        """
        with open('%s%s/all.json'%(self.path,self.name),'w',encoding='utf8') as file:
            json.dump(self.page_url,file)

    def get_img(self,url,name):
        """
        将图片保存在主目录(self.name)下的img文件夹下
        :param url:
        :param name:保存的文件名称
        :return:
        """
        r = requests.get(url,stream=True)
        with open("%s%s/img/%s"%(self.path,self.name, name), 'wb') as fd:
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

    def get_roll_url(self,init_url,change_url = None,start=None,end=None,space=1):
        """
        获得最外层(roll)的所有连接，对应的每个页面的连接。设置init_url的初衷是很多网站第一页没有page类参数。
        :param init_url:(str) 开始的页面,url中类似page=1,注意有些网站第一页没有该参数
        :param change_url:(str) 改变的url
        :param start:(int) 改变url的参数其实位置，比如page=2
        :param end: (int)改变url的参数的结束位置，比如page=100
        :param space: (int)改变url的参数，有些网站不是间隔1，而是一个等差数列
        :return: (list) 返回拼贴好的url
        """
        roll_url = [init_url]
        if change_url:
            for i in range(start, (end+1)):
                url = change_url % (i*space)
                roll_url.append(url)
        self.roll_url = roll_url
        return self.roll_url


    def get_all_url(self,get_page_url,clean_def=None, interval = 2,type="html",engine="requests",pre=None,down=50):
        """
        遍历roll_url获得每一页的page_url，再将他们合在一起。并保存成json
        :param get_page_url: 传入获得每一页url的方法
        :param interval: 设置时间间隔
        :return:(list) 返回roll_url包含的所有url
        """
        for url in self.roll_url:
            if engine == "requests":
                self.get_page_source(url= url)
            if engine == "selenium":
                self.get_page_source2(url=url,down=down,pre=pre)
            self.clean(clean_def,type=type)
            self.get_page_url(get_page_url)
            self.all_url.extend(self.page_url)
            time.sleep(interval)
        with open('%s%s/all_url.json' % (self.path,self.name), 'w', encoding='utf8') as file:
            json.dump(self.all_url, file)
        return self.all_url

    def iter_all_url(self,init_url,get_page_url,deep=10,interval =2):
        """
        这个方法是针对没有页码只有“下一页”的网站
        :param url:(str) 传入第一页的url
        :param get_page_url: (str) 传入获得page_url的方法
        :param deep: (int) 迭代次数
        :param interval: (int) 时间间隔
        :return:(list) 所有的url
        """
        li = []
        self.get_page_source(url =init_url)
        for i in range(1,deep+1):
            try:
                self.clean()
                self.get_page_url(get_page_url=get_page_url)
                li.extend(self.page_url["urls"])
                time.sleep(interval)
                self.get_page_source(self.page_url["next"])
            except:
                pass
        self.all_url = li
        with open('%s%s/all_url.json' % (self.path,self.name), 'w', encoding='utf8') as file:
            json.dump(self.all_url, file)

        return self.all_url

    def get_all_data(self, get_page_data,interval = 2):
        """
        获得page_data，并保存在temp文件夹内
        :param get_page_data: 获得页面的数据
        :param interval: 设置时间间隔
        :return:(list) 所有的数据
        """
        start = 0  # 查看和all_url和temp文件夹里的json判断从哪个点继续
        if os.path.exists("%s%s/all_url.json"%(self.path,self.name)):
            self.all_url = json.load(open("%s%s/all_url.json" % (self.path,self.name), 'r'))
            files = os.listdir("%s%s/temp"%(self.path,self.name))
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
                with open('%s%s/temp/%s.json'%(self.path,self.name,i),'w',encoding='utf8') as file:
                    json.dump(self.page_data, file)
                time.sleep(interval)
            except Exception as e:
                if str(e) != "'NoneType' object does not support item assignment":  # 如果在文章页面验证时间，会返回None，不需要报错
                    with open('%s%s/log.txt'%(self.path,self.name), 'a', encoding='utf8') as file:
                        file.write(url +' '+str(e) +"\n")
        self.add_json()

    def add_json(self):
        """
        整合temp文件夹下所有的json文件
        """
        files = os.listdir("%s%s/temp"%(self.path,self.name))
        all_data = []
        for file in files:
            temp = json.load(open("%s%s/temp/%s" % (self.path,self.name,file)))
            all_data.append(temp)
        json.dump(all_data, open("%s%s/all.json"%(self.path,self.name), 'w'))

    def get_all_img(self):
        all_data = json.load(open("%s%s/all.json"%(self.path,self.name), 'w'))
        for i in range(len(all_data)):
            for j in range(len(all_data[i]["img"])):
                name =str(i)+"-"+str(j)
                self.get_img(all_data[i]["img"][j],name)
            with open('%simg/log.txt'%self.path, 'a', encoding='utf8') as file:
                file.write(i + '\t' + all_data[i]['url'] + "\n")