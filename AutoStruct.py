#encoding=utf-8
from AI import AISpider
import os.path
from scrapely.template import AnnotationError
from scrapely.template import FragmentNotFound
from scrapely.template import FragmentAlreadyAnnotated
import re
import json
import scrapely.htmlpage
from lxml import etree
from scrapely import Scraper

# ###########################配置项目#############################################3
# 默认编码
defaultEncoding="utf-8"
#默认训练模板保存位置
defaultTplSaveDir="./tpl/"


##########################训练（生成模板）相关代码###################################
# 注解训练
def trainByAnnotation(htmlFilePath=None,annotationItemData=None,tplSaveDir=None,tplSavename=None,encoding=None):
    # 错误检测
    errorMsg=""
    if not htmlFilePath:
        return  "error:Html文件没有提供！"
    if not annotationItemData:
        return  "error:训练的字段没有提供！"

    if htmlFilePath and annotationItemData:
        # 选择模板保存目录
        if not tplSaveDir:
            Savedir=os.path.abspath(defaultTplSaveDir)
        else:
            Savedir = os.path.abspath(tplSaveDir)
        # 选择模板保存的文件名
        if not tplSavename:
            # 带后缀文件名
            filename = os.path.basename(htmlFilePath)
            # 不带后缀文件名
            filename = os.path.splitext(filename)[0]
            filename += ".tpl"
        else:
            filename  = tplSavename
        #拼接保存路径
        tplSavepath = Savedir + "/" + filename
        # 编码
        if not encoding:
            encoding=defaultEncoding
        # 模板生成成功返回模板位置
        try:
            if AISpider.trainFromLocalFiles(os.path.abspath(htmlFilePath),annotationItemData,tplSavepath,encoding):
                return tplSavepath
        except FragmentNotFound,e:
            # 字段训练失败
            return "error:"+re.search(r'Fragment not found annotating \'(.*?)\' using', e.message, re.M | re.I).group(1) + "字段训练失败！"
            #同一字段多次训练
        except FragmentAlreadyAnnotated:
            return  "error:同值字段多次训练！"
# print trainByAnnotation(htmlFilePath="./test.html",annotationItemData={"name1":"Harry Potter","title1":"i am title"},encoding="gb2312")

# 把xpath存到模板
def appendXpathToTpl(tplSavePath=None,xpathItemList=None):
    file = open(os.path.abspath(tplSavePath),'r')
    data = json.load(file)
    file.close()
    data['xpath']={}
    tmp=[]
    for xpath in xpathItemList:
            t={}
            t["key"] = xpath['key']
            t['xpathstr']=xpath['xpathstr']
            tmp.append(t)
    data['xpath']=tmp
    file = open(os.path.abspath(tplSavePath), 'w')
    json.dump(data,file)
    file.close()
# appendXpathToTpl('./tpl/test.tpl',[{"key":"name","xpathstr":"//book[@category='WEB'][1]/title"},{"key":"title","xpathstr":"//book[@category='WEB'][2]/title"}])

# 集成注解和xpath
def train(htmlFilePath=None,annotationItemData=None,tplSaveDir=None,tplSavename=None,encoding=None,xpathItemList=None,mode="both"):
    tplpath=trainByAnnotation(htmlFilePath=htmlFilePath,annotationItemData=annotationItemData,tplSaveDir=tplSaveDir,tplSavename=tplSavename,encoding=encoding)
    # 注解训练失败返回错误信息
    if re.search(r'error.*?',tplpath,re.I|re.M):
        return tplpath
    else:
        appendXpathToTpl(tplSavePath=tplpath,xpathItemList=xpathItemList)
        dataFile = open(tplpath,'r')
        data = json.load(dataFile )
        dataFile.close()
        data['mode']=mode
        dataFile=open(tplpath,'w')
        json.dump(data,dataFile)
        dataFile.close()
        return tplpath
# print train(htmlFilePath='./test.html',annotationItemData={"name1":"Harry Potter","title1":"Vaidyanathan Nagarajan"},xpathItemList=[{"key":"name","xpathstr":"//book[@category='WEB'][1]/title"},{"key":"title","xpathstr":"//book[@category='WEB'][2]/title"}])

##############################结构化相关代码##############################


# 注解提取
def annotationStruct(htmlFilePath=None,tplFilePath=None,encoding="utf-8"):
    # 打开模板文件并加载数据
    try:
        tplFileObj = open(os.path.abspath(tplFilePath))
    except IOError:
        return "error:模板文件不存在！"
    try:
        data = json.load(tplFileObj)
    except:
        return "error:模板解析失败！"
    tplFileObj.close()
    # 加载annotation数据
    templates = [scrapely.htmlpage.HtmlPage(**x) for x in data['annotation']['templates']]
    # 创建scrapely实例
    s = Scraper(templates=templates)
    # 创建htmlpage对象
    try:
        htmlFileObj=  open(os.path.abspath(htmlFilePath))
    except IOError:
        return "error:html文件不存在！"
    page = scrapely.htmlpage.HtmlPage(body=unicode(htmlFileObj.read().decode(encoding)),encoding=encoding)
    htmlFileObj.close()
    # 结构化提取数据
    annotationResult = s.scrape_page(page)
    # 返回数据
    #没有提取到结果返回空数组
    if annotationResult[0]=={}:
        return {}
    #提取到返回字典数组
    res = {}
    for (k,v) in annotationResult[0].items():
        res[k]=v[0]
    return res
# print annotationStruct(htmlFilePath="./test.html",tplFilePath="./tpl/test.tpl")

# xpath提取
def xpathStruct(htmlFilePath=None,tplFilePath=None,encoding="utf-8"):
    try:
        tplFileObj = open(os.path.abspath(tplFilePath))
    except IOError:
        return "error:模板文件不存在！"
    # 打开模板并加载数据
    try:
        data = json.load(tplFileObj)
    except Exception,e:
        return u"error:模板文件解析失败！"+e.message
    # 加载xpath数据
    try:
        xpathList = data['xpath']
    except Exception,e:
        return u"error:模板xpath不存在！"
    # 解析html文件
    try:
        htmlFileObj = open(os.path.abspath(htmlFilePath))
    except IOError:
        return "error:html文件不存在！"
    try:
        html = etree.parse(htmlFileObj)
        htmlFileObj .close()
    except Exception,e:
        return u"hmtl解析失败！" +e.message

    # 结构化提取数据
    xpathResult = {}
    for xpath in xpathList:
        tmp = {}
        value = ""
        for v in html.xpath(xpath['xpathstr']):
            value += v.xpath('string(.)')
        if value!="":
            xpathResult[xpath['key']] = value
    return xpathResult
# print xpathStruct(htmlFilePath="./test.html",tplFilePath="./tpl/test.tpl")

# 结构化集成
def struct(htmlFilePath=None,tplFilePath=None,encoding="utf-8"):
    annotationResult = annotationStruct(htmlFilePath=htmlFilePath, tplFilePath=tplFilePath)

    # 有错误信息就返回
    if type(annotationResult) is not dict and re.search(r'error.*?',annotationResult,re.I|re.M):
        return annotationResult

    xpathResult = xpathStruct(htmlFilePath=htmlFilePath, tplFilePath=tplFilePath)
    # 有错误信息返回
    if type(xpathResult) is not dict and re.search(r'error.*?', xpathResult, re.I | re.M):
        return xpathResult

    return dict(xpathResult.items() + annotationResult.items())
# print struct(htmlFilePath="./test.html", tplFilePath="./tpl/test.tpl")



###########################测试代码##########################

# 训练
# print train(htmlFilePath='./test.html',annotationItemData={"name1":"Harry Potter","title1":"Vaidyanathan Nagarajan"},xpathItemList=[{"key":"name","xpathstr":"//book[@category='WEB'][1]/title"},{"key":"title","xpathstr":"//book[@category='WEB'][2]/title"}])
# 结构化
# print struct(htmlFilePath="./test.html", tplFilePath="./tpl/test.tpl")