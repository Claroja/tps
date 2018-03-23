import time


def is_yesterday(stamp):
    today = time.strftime("%Y %m %d")
    today = time.strptime(today, "%Y %m %d")
    today = time.mktime(today)  # 今天凌晨的时间戳
    date = today - stamp
    if 0 < date < 86400:
        return True
    else:
        return False


if __name__ == "__main__":
    a = is_yesterday(123123)
    print(a)
