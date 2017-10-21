# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import urllib
import ssl
import json
import shutil


class Helper:
    login_url = ''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Host': 'www.zhihu.com',
        'Origin': 'https://www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    def __init__(self):
        self._session = requests.session()
        self._session.headers = Helper.headers

    def login(self):

        print self._session.headers
        form_data = self._prepare_login_form_data()

        # 获取验证码图片访问得到的 cookies
        # file = open('zhihu_cookies', 'r')
        # cookies = json.load(file)
        # self._session.cookies.update(cookies)

        # 发起登录请求
        res = self._session.post(
            'https://www.zhihu.com/login/phone_num', data=form_data)
        print(res.json()['msg'])

        # response = self._session.post(Helper.url, data=form_data)

        # print response.text
        # print response.cookies

    def _prepare_login_form_data(self):
       # 获取配置文件
        data_file = open('config.json')
        data = json.load(data_file)
        Helper.url = data["zhihu"]["login-url"]
        loginpage = data["zhihu"]["login-page"]
        username = data["zhihu"]["username"]
        password = data["zhihu"]["password"]
        captcha_text = data["zhihu"]["captcha-text"]
        # 获取 在登录页面上获取xsrf
        response = self._session.get(loginpage)
        # tesst
        imageurl = data['zhihu']['captcha-url']
        res = self._session.get(imageurl % (
            time.time() * 1000), headers=Helper.headers)
        # 保存验证码到本地`
        with open('./captcha/zhihu.png', 'wb') as f:
            f.write(res.content)
        f.close
        del res
            page = BeautifulSoup(response.text, 'lxml')
            xsrf = str(page.find('input', attrs={'name': '_xsrf'})['value'])
            code = input("请输入验证码:")
            form = {
                'phone_num': str(username),
                'password': str(password),
                '_xsrf': xsrf,
                'captcha': str(captcha_text)
                # 'captcha_type':'en'
            }
            print form


if __name__ == '__main__':
    _helper = Helper()
    _helper.login()
    # _helper.postArticle('');
    # _helper.login2(username, password);


else:
    print 'being imported as module'
