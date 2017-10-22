# -*- coding: utf-8 -*-
import json
import os
import re

def jsonTokv():
	file = open('zhihu_cookies', 'r')
	try:
		cookies = json.load(file)
		# print len(cookies)
	except ValueError,e:
		print 'cache-cookie is None'
	
	
	cookiesStr = ''
	for key in cookies:
		cookiesStr += key+'='+cookies[key]+';'
	print cookiesStr[0:-1]
	return cookiesStr[0:-1]
	
	
	
def jsonDelete():
	draftData = {
		"do": "saveArticle",
		"type": "1",
		"title": "如何正确的发布md",
		"text": "# 这是标题",
		"weibo": "0",
		"blogId": "0",
		"aticleId": "",
		"id": "",
		"tags[]": "1040000000366352",
		"url": ""
	}
	
	del draftData['do']
	
	print draftData
	

def demo():
	
	file = open('demo.md').read()
	print file[0:1000]
	
	
	print '----------------'
	
	pattern = re.compile(r"---(\n(.{0,}))*---")
	print	re.sub(pattern,'tihuan',file[0:1000])
	# print 'result is : ' + result
	
	# print len(result)
	
	# map = {}
	# map['a'] = 1
	# print map
	#
	# print 'test:'
	# for line in os.listdir('../'):
	# 	print line
		# print os.path.abspath(os.path.join('/Users/zhidaliao/Desktop/zhida_blog/_posts/docker',line))
	
	
# jsonTokv()
# jsonDelete()
demo()
