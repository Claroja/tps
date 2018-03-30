import time
import requests

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
def agg(a):
    """

    :param a:字典
    :return:
    """
    import pandas as pd
    df = pd.DataFrame()
    for name in a.keys():
        dft = pd.read_json("./%s/all.json"%name)
        df = df.append(dft,ignore_index=True)
    return df

if __name__ == "__main__":
    a = is_yesterday(123123)
    print(a)
