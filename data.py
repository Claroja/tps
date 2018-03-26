# 清洗数据
# .str[3:] 直接用str截取有用信息
# str.split(" ").str[0] 先split分割,再用str截取信息
# str.replace("(.IRPP_ruby.*\n)","") 利用正则表达式提取信息
    # 提取中文内容[^\u4e00-\u9fa5！，。（）《》“”？：；【】]
# pd.to_datetime(df["time"],format="%m/%d/%y") #转换时间格式
import pandas as pd
class Data(object):
    def __init__(self,path):
        self.df = pd.read_json(path)
    def word_num(self):
        pass

class EData(Data):
    # 查看每篇文章字数
    def word_num(self,origin, target, split):
        """
        统计没篇文章的字数,并创建新的列
        :param origin:
        :param target:
        :param split:
        :return:
        """
        self.df[target] = self.df[origin].str.split(split).str.len()

    def cate_stat(self,col,split):
        """
        查看多分类占比
        :param col: 类别
        :param split:
        :return:
        """
        cate = []
        for a in self.df[col].str.split(split):
            cate.extend(a)
        cate = [b.strip() for b in cate]
        cate = pd.Series(cate).value_counts()

        return cate

    def works_change(self,time,col):
        """
        #1.发文量随年份时间变化
        #2.发文量年周期变化（月，周）
        :return:
        """
        year_group = self.df.groupby(self.df[time].dt.year)
        year = year_group.count()[col]
        month_group = self.df.groupby(self.df[time].dt.month)
        month = month_group.count()[col]
        week_group = self.df.groupby(self.df[time].dt.dayofweek)
        weekday = week_group.count()[col]

        return [year,month,weekday]

class CData(Data):
    def word_num(self,origin, target, split):
        self.df["temp"] = self.df[origin]
        self.df["temp"] = self.df["temp"].str.replace(r"[^\u4e00-\u9fa5]", "")
        self.df[target] = self.df["temp"].str.len()
        del self.df["temp"]


# 查看每篇文章字数(英文,中文 已实现)
# 查看每篇文章的情感
# 查看词频和关键词

#1.关键词随年份时间变化
#2.关键词年周期变化（英文 月，周）

# 查看多分类的分类占比(英文 已实现)
#1.各个分类随年份时间变化
#2.各个分类年周期变化（英文 月，周）

# 发文量统计(英文 已实现)
#1.发文量随年份时间变化(英文 已实现)
#2.发文量年周期变化（月，周）(英文 已实现)

# 查看评论数分布
#1.查看评论数按分类统计
