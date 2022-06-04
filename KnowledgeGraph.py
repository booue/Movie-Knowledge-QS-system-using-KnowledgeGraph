# -*-coding = utf-8-*-

# Author:qyan.li
# Date:2022/5/19 14:49
# Topic:豆瓣电影数据解析，处理形成电影知识图谱
# Reference:https://blog.csdn.net/black_lightning/article/details/114499690


## 相关模块导入
import pandas as pd
from py2neo import Graph,Node,Relationship

## 连接图形库，配置neo4j
graph = Graph("http://localhost:7474//browser/",auth = ('neo4j','********'))
# 清空全部数据
graph.delete_all()
# 开启一个新的事务
graph.begin()

## 此处使用utf-8编码会报编码错误:UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc9 in position 56: invalid continuation byte
## 将此处编解码方式修改为gbk
## 修改文件的录入内容后，gbk编码报错，utf-8编码可以正常使用

## csv源数据读取
storageData = pd.read_csv('./movieInfo.csv',encoding = 'utf-8')
# 获取所有列标签
columnLst = storageData.columns.tolist()
# 获取数据数量
num = len(storageData['title'])

# KnowledgeGraph知识图谱构建(以电影为主体构建的知识图谱)
for i in range(num):

    '''
    py2neo.errors.ClientError: [Request.InvalidFormat] Unable to deserialize request: Non-standard token 'NaN': enable JsonParser.Feature.ALLOW_NON_NUMERIC_NUMBERS to allow
    at [Source: (org.eclipse.jetty.server.HttpInputOverHTTP); line: 1, column: 588]
    问题在于‘黑客帝国’电影的演员表为nan，且在某种程度上无法通过重新写入，修改csv文件实现修改，解决办法：直接在程序运行时剔除
    '''
    if storageData['title'][i] == '黑客帝国2：重装上阵' or storageData['title'][i] == '黑客帝国3：矩阵革命':
        continue

    # 为每部电影构建属性字典
    dict = {}
    for column in columnLst:
        dict[column] = storageData[column][i]
    # print(dict)
    node1 = Node('movie',name = storageData['title'][i],**dict)
    graph.merge(node1,'movie','name')

    ## 上述代码已经成功构建所有电影的主节点，下面构建所有的分结点以及他们之间的联系
    # 去除所有的title结点
    dict.pop('title')
    ## 分界点以及关系
    for key,value in dict.items():
        ## 建立分结点
        node2 = Node(key,name = value)
        graph.merge(node2,key,'name')
        ## 创建关系
        rel = Relationship(node1,key,node2)
        graph.merge(rel)


## 到此为止，知识图谱基本已经构建完成，下面进行知识图谱结构的微调

'''
小Tips：
1. 所有的node的相同relationship的对象只能有一个
2. 为增加电影之间的关联性，对于内容具有多个标签的，仅选取其中第一个
'''




