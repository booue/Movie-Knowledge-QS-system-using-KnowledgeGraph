# -*-coding = utf-8-*-

# Author:qyan.li
# Date:2022/5/19 20:03
# Topic:生成jieba分词的自定义词典
# Reference:https://blog.csdn.net/smilejiasmile/article/details/80958010

## 相关模块引入
import pandas as pd


## jiaba分词添加自定义词典，以保证电影名称分词正确
## 自定义词典构建时，分别写入 名词 词频 词性(词性，可以省略，但建议自定义写出，方便后续使用)
# 读取原数据库
storage_df = pd.read_csv('./movieInfo.csv',encoding = 'utf-8')
movieNameLst = [name for name in storage_df['title']]

# 构建自定义词典
with open('./selfDefiningTxt.txt','w',encoding = 'utf-8') as f:
    for name in movieNameLst:
        f.write(name + ' 100 lqy')
        f.write('\n')









