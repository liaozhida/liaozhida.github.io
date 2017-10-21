# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import urllib
import ssl
import json
import shutil
from preCaptcha import CaptchaHelper
import requests
import time



class Helper:
	login_url = '';
	headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Host':'www.segmentfault.com',
        'Origin':'https://www.segmentfault.com',
        'Referer':'https://www.segmentfault.com',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
	}
	
	def __init__(self):
		self._session = requests.session()
		self._session.headers = Helper.headers
		self._session.max_redirects = 60
		self._session.headers['Cookie'] = self.jsonTokv()
		self.loadConfig()
		
		
	def loadConfig(self):
		# 获取配置文件
		data_file = open('config.json')
		data = json.load(data_file)
		self.loginUrl = data["segment"]["login-url"]
		self.loginPage = data["segment"]["login-page"]
		self.username = data["segment"]["username"]
		self.password = data["segment"]["password"]
	
	def jsonTokv(self):
		try:
			file = open('segment_cookies', 'r')
			cookies = json.load(file)
		# print len(cookies)
		except ValueError, e:
			print 'cache-cookie is None'
		except IOError , e:
			print 'file is not found'
		finally:
			return None
		
		cookiesStr = ''
		for key in cookies:
			cookiesStr += key + '=' + cookies[key] + ';'
		print  'cookies is :' + cookiesStr
		return cookiesStr[0:-1]
	
	def login(self):
		
		print ' output : cookie'
		print self._session.cookies
		print self._session.headers['Cookie']
		data = self._prepare_login_form_data()
		
		res =''
		while(res == ''):
			try:
				print 'login 2'
				res = self._session.post(self.loginUrl,data=data,allow_redirects=False,timeout=40)
				print res.text
				print res
				print res.text
				print res.cookies
				print res.content
				# print res.json()['msg']
			except ValueError,e:
				print e
				print 'use cached login is succ'
				return 'succ'
			except requests.exceptions.ConnectionError:
				print 'requests.exceptions.ConnectionError  try again'
				time.sleep(5)
				print 'sleep over'
				continue
		
		print res.text
		# code = str(res.json()['r'])
		# if(code == '0'):
		# 	print '登录成功'
		# 	return 'succ'
		# else:
		# 	form_data = self._prepare_login_form_data()
		# 	res = self._session.post(self.loginUrl,data=form_data,timeout=10)
		# 	code = str(res.json()['r'])
		# 	if(code == '0'):
		# 		file = open('segment_cookies', 'w')
		# 		cookies = self._session.cookies.get_dict()
		# 		json.dump(cookies, file)
		# 		file.close()
		# 		print '登录成功'
		# 		return 'succ'
		# 	else:
		# 		print '登录失败'
		# 		print res.json()['msg']
		# 		return 'fail'
		# return 'fail'


	def _prepare_login_form_data(self):
		
		# 获取验证码 保存到本地
		print self.loginPage
		response = ''
		while response == '':
			try:
				response = self._session.get(self.loginPage,allow_redirects=False, headers=self.headers)
				print 'hello world'
				print response.text
			except:
				print("Connection refused by the server..")
				print("Let me sleep for 5 seconds")
				print("ZZzzzz...")
				time.sleep(5)
				print("Was a nice sleep, now let me continue...")
				continue
			
		
		# 获取xsrf
		# response = self._session.get(self.loginpage)
		# page = BeautifulSoup(response.text, 'lxml')
		# xsrf = str(page.find('input', attrs={'name': '_xsrf'})['value'])
		#
		# # 封装返回数据
		# code = raw_input("请输入知乎验证码:")
		# form = {
		# 	'phone_num': str(self.username),
		# 	'password': str(self.password),
		# 	'_xsrf': xsrf,
		# 	'captcha': code,
		# 	'captcha_type':'en'
		# }
		# print form
		# return form
		#
	def _prepare_login_form_data2(self):
		
		# 获取验证码 保存到本地
		response = self._session.get(self.imageurl % (time.time() * 1000), headers=self.headers)
		with open('./captcha/segment.png', 'wb') as f:
			f.write(response.content)
			f.close
			del response
		
		# 获取xsrf
		response = self._session.get(self.loginpage)
		# print response.text
		page = BeautifulSoup(response.text, 'lxml')
		xsrf = str(page.find('input', attrs={'name': '_xsrf'})['value'])
		
		
		form = {
			'phone_num': str(self.username),
			'password': str(self.password),
			'_xsrf': xsrf,
			'captcha': 'code',
			'captcha_type': 'en'
		}
		print form
		return form
		
	def postArticle(self):
		print '--submit post--'
		self._session.get()
  
	def destroy(self):
		self._session.close()

if __name__ == '__main__':

	_helper = Helper()
	_helper.login()
	# _helper.postArticle();
	# _helper.login2(username, password);
	_helper.destroy()
	



else:
	print 'being imported as module'


