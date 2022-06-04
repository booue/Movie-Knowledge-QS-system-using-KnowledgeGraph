# -*-coding = utf-8-*-

# Author:qyan.li
# Date:2022/5/19 17:46
# Topic:借助于python语言构建基于知识图谱的电影智能问答系统

'''
智能问答系统构建：
1. 网络爬虫 + 数据集构建
2. 电影知识图谱构建
3. 问句处理 + 查询返回
'''

# 相关模块导入
import jieba.posseg as pseg
import jieba
from fuzzywuzzy import fuzz
from py2neo import Graph

## 建立neo4j对象，便于后续执行cyphere语句
graph = Graph("http://localhost:7474//browser/",auth = ('neo4j','999272@123xy'))

## 用户意图的判断
#设计八类问题的匹配模板
info = ['这部电影主要讲的是什么？','这部电影的主要内容是什么？','这部电影主要说的什么问题？','这部电影主要讲述的什么内容？']
director = ['这部电影的导演是谁？','这部电影是谁拍的？']
actor = ['这部电影是谁主演的？','这部电影的主演都有谁？','这部电影的主演是谁？','这部电影的主角是谁？']
time = ['这部电影是什么时候播出的？','这部电影是什么时候上映的？']
country = ['这部电影是那个国家的？','这部电影是哪个地区的？']
type = ['这部电影的类型是什么？','这是什么类型的电影']
rate = ['这部电影的评分是多少？','这部电影的评分怎么样？','这部电影的得分是多少分？']
num = ['这部电影的评价人数是多少？','这部有多少人评价过？']
# 设计八类问题的回答模板
infoResponse = '{}这部电影主要讲述{}'
directorResponse = '{}这部电影的导演为{}'
actorResponse = '{}这部电影的主演为{}'
timeResponse = '{}这部电影的上映时间为{}'
countryResponse = '{}这部电影是{}的'
typeResponse = '{}这部电影的类型是{}'
rateResponse = '{}这部电影的评分为{}'
numResponse = '{}这部电影评价的人数为{}人'
# 用户意图模板字典
stencil = {'info':info,'director':director,'actor':actor,'time':time,'country':country,'type':type,'rate':rate,'num':num}
# 图谱回答模板字典
responseDict = {'infoResponse':infoResponse,'directorResponse':directorResponse,'actorResponse':actorResponse,'timeResponse':timeResponse,'countryResponse':countryResponse,'typeResponse':typeResponse,'rateResponse':rateResponse,'numResponse':numResponse}

# 由模板匹配程度猜测用户意图
## 模糊匹配参考文献：https://blog.csdn.net/Lynqwest/article/details/109806055
def AssignIntension(text):
    '''
    :param text: 用户输入的待匹配文本
    :return: dict:各种意图的匹配值
    '''
    stencilDegree = {}
    for key,value in stencil.items():
        score = 0
        for item in value:
            degree = fuzz.partial_ratio(text,item)
            score += degree
        stencilDegree[key] = score/len(value)

    return stencilDegree


## 问句实体的提取
## 结巴分词参考文献：https://blog.csdn.net/smilejiasmile/article/details/80958010
def getMovieName(text):
    '''
    :param text:用户输入内容 
    :return: 输入内容中的电影名称
    '''
    movieName = ''
    jieba.load_userdict('./selfDefiningTxt.txt')
    words =pseg.cut(text)
    for w in words:
        ## 提取对话中的电影名称
        if w.flag == 'lqy':
            movieName = w.word
    return movieName


## cyphere语句生成，知识图谱查询，返回问句结果
## py2neo执行cyphere参考文献：https://blog.csdn.net/qq_38486203/article/details/79826028
def SearchGraph(movieName,stencilDcit = {}):
    '''
    :param movieName:待查询的电影名称 
    :param stencilDcit: 用户意图匹配程度字典
    :return: 用户意图分类，知识图谱查询结果
    '''
    classification = [k for k,v in stencilDcit.items() if v == max(stencilDcit.values())][0]
    ## python中执行cyphere语句实现查询操作
    cyphere = 'match (n:movie) where n.title = "' + str(movieName) + '" return n.' + str(classification)
    object = graph.run(cyphere)
    for item in object:
        result = item
    return classification,result

## 根据问题模板回答问题
def respondQuery(movieName,classification,item):
    '''
    :param movieName: 电影名称
    :param classification: 用户意图类别
    :param item:知识图谱查询结果 
    :return:none 
    '''
    query = classification + 'Response'
    response = [v for k,v in responseDict.items() if k == query][0]
    print(response.format(movieName,item))

def main():
    queryText = '肖申克的救赎这部电影的导演是谁？'
    movieName = getMovieName(queryText)
    dict = AssignIntension(queryText)
    classification,result = SearchGraph(movieName,dict)
    respondQuery(movieName,classification,result)

if __name__ == '__main__':
    main()






