import pandas as pd
df = pd.read_json("./hair/all.json")
df.head(10)

# 清洗数据
df["category"]=df["category"].str[3:]
df["comment_num"]=df["comment_num"].str.split(" ").str[0]
df["time"] = df["time"].str.split(" ").str[1]
df["content"] = df["content"].str.replace("(.IRPP_ruby.*\n)","")
df["content"] = df["content"].str.replace("\[.*\]","")
df["time"] = pd.to_datetime(df["time"],format="%m/%d/%y") #转换时间格式
# 查看每篇文章字数
df["word_num"] = df["content"].str.split(" ").str.len()
df["word_num"].describe().astype("int")

# 查看每篇文章的情感
# 查看词频和关键词

#1.关键词随年份时间变化
#2.关键词年周期变化（月，周）

# 查看多分类的分类占比
cate = []
for a in df["category"].str.split(","):
    cate.extend(a)
cate = [b.strip() for b in cate]
cate = pd.Series(cate).value_counts()

#1.各个分类随年份时间变化
year_group = df.groupby(df["time"].dt.year)
year_group.count()["title"]
#2.各个分类年周期变化（月，周）
month_group = df.groupby(df["time"].dt.month)
month_group.count()["title"]
week_group = df.groupby(df["time"].dt.dayofweek)
week_group.count()["title"]

# 发文量统计
#1.发文量随年份时间变化

#2.发文量年周期变化（月，周）

# 查看评论数分布
#1.查看评论数按分类统计


df.to_excel('./hair/all.xlsx', sheet_name='Sheet1')
