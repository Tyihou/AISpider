#-*-coding:UTF-8-*-
from scrapely import Scraper
from scrapely.htmlpage import HtmlPage, page_to_dict, url_to_page
import json
import os.path
class AISpider:
	@classmethod
	# 从本地文件训练
	def trainFromLocalFiles(cls,htmlFilepath="",annotationItemData="",saveFilename="",encoding='utf-8'):

		s = Scraper()
		file = open(htmlFilepath)
		content =file.read()
		page = HtmlPage(body=unicode(content.decode(encoding)),encoding=encoding)
		s.train_from_htmlpage(page,annotationItemData)
		if(saveFilename!=""):
			saveDir = os.path.dirname(saveFilename)
			# 创建模板保存目录
			if not os.path.exists(saveDir):
				os.makedirs(saveDir)
			# 判断是否模板已存在
			try:
				file = open(saveFilename, "r")
				data = json.load(file)#存在就直接读
				# 关闭文件
				file.close()
			except IOError:#不存在创建
				data = {}
				data['annotation']={}

			tpls = [page_to_dict(x) for x in s._templates]
			data['annotation']['templates']=tpls
			# 输出模板信息
			file = open(saveFilename, "w")
			json.dump(data, file)
			# 关闭文件
			file.close()
		return s

	@classmethod
	def trainFromUrls(cls,items,saveFilename="",encoding='utf-8'):
		s = Scraper()
		for item in items:
			s.train(item["url"],item["data"],encoding=encoding)
		if(saveFilename!=""):
			file = open(saveFilename,"wb")
			print file
			# s.tofile(file)
		return s
	# 从以存在的模板获取一个Scrapely实例
	@classmethod
	def getScrapelyFromTpl(cls,filename):
		file = open(filename,"rb")
		return Scraper.fromfile(file)
	# 将本地网页转成Scrapely需要的Page对象
	@classmethod
	def fileToPage(csl,filename,encoding='utf-8'):
		file = open(filename)
		content =file.read()
		return HtmlPage(body=unicode(content.decode(encoding)),encoding=encoding)
		