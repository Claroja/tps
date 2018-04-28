import time
import requests
import os
import json
import shutil

def is_yesterday(stamp):
    today = time.strftime("%Y %m %d")  # 生成凌晨的时间
    today = time.strptime(today, "%Y %m %d")  # 生成凌晨的时间
    today = time.mktime(today)  # 今天凌晨的时间戳
    date = today - stamp
    if 0 < date < 86400:
        return True
    else:
        return False

def get_img(path,filename):
    r = requests.get(path, stream=True)
    with open(filename, 'wb') as fd:
        for chunk in r.iter_content():
            fd.write(chunk)

def agg(path,yesterday):
    # 整合数据模块
    if not os.path.exists("%s" % path): os.mkdir("%s" % path)
    if not os.path.exists("%s/day" % path) : os.mkdir("%s/day" % path)
    cities = os.listdir(path=path)
    cities.remove("day")
    if os.path.exists("%ssche"%path) : cities.remove("sche")

    li = []
    for city in cities:
        # city = cities[0]
        temp = json.load(open("%s%s/all.json" % (path,city)))
        li.extend(temp)
    json.dump(li,open("%sday/%s.json"%(path,yesterday),'w'))

    # log文件模块
    for city in cities:
        if os.path.exists("%s%s/log.txt" % (path, city)):
            with open("%s%s/log.txt" % (path, city),encoding='utf8') as file : a = file.read()
            with open("%sday/%s.error"%(path,yesterday),'a',encoding='utf8') as file : file.write(a+"\n")

    # 删除模块

    for city in cities:
        shutil.rmtree("%s%s"%(path,city))

    num = len(json.load(open("%sday/%s.json" % (path,yesterday)))) # 今天的条数
    with open("%ssche" % (path), 'a') as file: file.write(yesterday+"\t"+str(num) + "\n")

def excel(path,yesterday):
    import pandas as pd
    df = pd.read_json(path_or_buf="./%s/day/%s.json" % (path, yesterday))
    df.head()
    df.to_excel("./%s/day/%s.xlsx" % (path, yesterday))

def csv(path,yesterday):
    import pandas as pd
    df = pd.read_json(path_or_buf="./%s/day/%s.json" % (path, yesterday))
    df.head()
    df.to_csv("./%s/day/%s.csv" % (path, yesterday))

if __name__ == "__main__":
    a = is_yesterday(123123)
    print(a)
