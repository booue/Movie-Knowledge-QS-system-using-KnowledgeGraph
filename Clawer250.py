# -*-coding = utf-8-*-

# Author:qyan.li
# Date:2022.3.11
# Topic:借助于python爬取豆瓣前250电影的相关信息


# 模块引入
from bs4 import BeautifulSoup
import urllib.request,urllib.error
import re
import time
import csv
import jieba

# 全局变量
titleList = []
rateLst = []
numLst = []
infoLst = []
directorLst = []
actorLst = []
timeLst = []
countryLst = []
typeLst = []

# jieba中文分词
def jiebaCut(text):
    '''
    :param text:待分词的字符串 
    :return: 分词后的字符结果
    '''
    textCut = ' '.join(jieba.cut(text)).split(' ')
    ## 此处字符串处理必须保证'中国大陆'在原有列表中的位置(使用insert函数，而不是append函数)
    if '中国大陆' in text:
        index = textCut.index('中国')
        textCut.remove('中国')
        textCut.remove('大陆')
        textCut.insert(index,'中国大陆')
    return textCut[0]

# 处理演员信息，获得主演中的第一个，否则赋值'演职人员不详'
def ActorDealing(ActorInfo):
    '''
    :param ActorInfo:待处理的演职人员信息 
    :return: 演职人员名称或'演职人员不详'
    '''
    if '主演:' in ActorInfo:
        ActorInfo = ActorInfo.strip('主演:')
        if ActorInfo == "":
            ActorInfo = '演职人员不详'
        else:
            ActorInfo = ActorInfo.split('/')[0] # 获得演职员表中的第一个
    if ActorInfo == '主' or ActorInfo == '主演':
        ActorInfo = '演职人员不详'
    return ActorInfo


# 正则表达式匹配
findTitle = re.compile(r'<span class="title">(.*?)</span>') # 获取标题title
'''
1. 注意从网页源码复制，而不是手敲 2. 内容匹配时注意忽略其中的换行符 
'''
findContent = re.compile(r'<p class="">(.*?)</p>',re.S) # 获取电影主要内容
findRate = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>') # 获取评分
findNum = re.compile(r'<span>(.*?)</span>') # 获取评价人数
findInfo = re.compile(r'<span class="inq">(.*?)</span>') # 获取电影简介


# 请求获取网页信息
def askURL(url):
    '''模拟浏览器进行网页请求，返回网页信息
    :param url:待爬取的网页链接 
    :return: 获取到html网页信息
    '''
    head = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39'
    }
    request = urllib.request.Request(url,headers = head)
    html = ''
    try:
        responseInfo = urllib.request.urlopen(request)
        html = responseInfo.read().decode('utf-8')
    except urllib.error.URLError as e: # 异常处理机制
        if hasattr(e,'code'):
            print(e.code)
        if hasattr(e,'reason'):
            print(e.reason)

    return html

# 解析网页获得目标信息
def getData(html):
    '''网页内容解析，获取目标字段
    :param html: 获取到的html网页对象
    :return: None
    '''

    soup = BeautifulSoup(html,'lxml') # 网页解析

    ObjectPart = soup.find_all('ol',class_ = "grid_view")[0]
    for item in ObjectPart.find_all('li'):
        flag = 0

        item = str(item)

        movieDict = {}

        # title匹配，仅提取中文名称
        title = re.findall(findTitle,item)[0]
        titleList.append(title)

        # 电影内容内容匹配
        content = re.findall(findContent,item)[0]
        # 电影内容解析
        contentLst = content.split('\n')
        Time_Country_type = contentLst[2].replace(' ','').strip('/') # 去除所有的空格借助于replace(' ','')函数
        # 导演信息
        director = contentLst[1].replace(' ','').split('\xa0\xa0\xa0')[0].strip('导演:').split('/')[0]
        directorLst.append(director)

        # 演员信息(解决演员信息获取不到的问题)
        if len(contentLst[1].replace(' ','').split('\xa0\xa0\xa0')) == 1:
            actor = '演职人员不详'
        else:
            actor = contentLst[1].replace(' ','').split('\xa0\xa0\xa0')[1].strip('...<br/>') # 多人之间以'/'区分
        actor = ActorDealing(actor)
        actorLst.append(actor)

        # 上映时间信息
        time = Time_Country_type.split('/')[0].strip('\xa0')
        ## 添加数据筛选代码:后续报错->[py2neo]TypeError: Neo4j does not support JSON parameters of type int64尚未解决
        # if '(中国大陆)' in time:
        #     time = time.strip('(中国大陆)')
        timeLst.append(str(time))

        # 国家信息获取
        # country = Time_Country_type.split('/')[1].strip('\xa0')
        country = Time_Country_type.split('/')[1].replace('\xa0','')
        countryCut = jiebaCut(country)
        countryLst.append(countryCut)

        # 类型信息获取
        type = contentLst[2].strip('/').split('/')[-1].strip('\xa0').split(' ')[0] # 多类型之间以' '区分
        typeLst.append(type)

        # 电影评分内容匹配
        rate = re.findall(findRate,item)[0]
        rateLst.append(str(rate))
        # 电影评价人数匹配
        num = re.findall(findNum,item)[0].strip('评价')
        numLst.append(num)
        # 电影简介获取
        info = re.findall(findInfo,item)
        # 解决信息可能获取不到
        if len(info) != 0:
            info = info[0]
        else:
            info = '电影详细信息不详'
        infoLst.append(info)



# python内容写入excel表格
# csv文件写入-参考文献：https://blog.csdn.net/lbj1260200629/article/details/89600055
def writeIntoCSVFile(fileName):
    '''
    :param fileName:待保存csv文件路径 
    :return: None
    '''
    # newline = ''解决csv写入内容自动换行的问题
    # 参考文献：https://blog.csdn.net/weixin_44064937/article/details/105745398
    f = open(fileName,'w',newline = '',encoding = 'utf-8')
    csv_writer = csv.writer(f)
    # 构建列表头
    csv_writer.writerow(['title','rate','num','info','director','actor','time','country','type'])
    for i in range(len(titleList)):
        csv_writer.writerow([titleList[i],rateLst[i],numLst[i],infoLst[i],directorLst[i],actorLst[i],timeLst[i],countryLst[i],typeLst[i]])
    f.close()



def ClawerCode():
    '''网络爬虫主体程序：获取电影各部分信息,写入csv文件
    :return: None
    '''
    # 比较网页url区别，多界面爬取
    for i in range(10):
        LoopUrl = 'https://movie.douban.com/top250?start=' + str(i*25) + '&filter=' # 网页切换
        time.sleep(2) # 爬虫速率控制(自己添加，不知道有没有用)
        html = askURL(LoopUrl)
        getData(html)
        print(i)
    writeIntoCSVFile(fileName='./movieInfo.csv')

def main():
    ClawerCode()

if __name__ == '__main__':
    main()
