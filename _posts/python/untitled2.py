# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import urllib


nickName = '';

class CsdnHelper:
    csdn_login_url = 'https://passport.csdn.net/account/login?ref=toolbar'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    }
    blog_url = 'http://write.blog.csdn.net/postlist/'

    def __init__(self):
        self._session = requests.session()
        self._session.headers = CsdnHelper.headers

    def login(self, username, password):

        form_data = self._prepare_login_form_data(username, password)
        response = self._session.post(CsdnHelper.csdn_login_url, data=form_data)

        print response.cookies

        if 'UserNick' in response.cookies:
            global nickName;
            nickName = response.cookies['UserNick']
            print (nickName)
        else:
            raise Exception('error')

    def _prepare_login_form_data(self, username, password):

        response = self._session.get(CsdnHelper.csdn_login_url)

        login_page = BeautifulSoup(response.text, 'lxml')
        login_form = login_page.find('form', id='fm1')
        lt = login_form.find('input', attrs={'name': 'lt'})['value']
        execution = login_form.find('input', attrs={'name': 'execution'})['value']
        eventId = login_form.find('input', attrs={'name': '_eventId'})['value']
        form = {
            'username': username,
            'password': password,
            'lt': lt,
            'execution': execution,
            '_eventId': eventId
        }

        return form

    def _get_blog_count(self):
        
        self._validate_redirect_url()

        response = self._session.get(CsdnHelper.blog_url)
        blog_page = BeautifulSoup(response.text, 'lxml')
        span = blog_page.find('div', class_='page_nav').span
        span = span.string.encode('utf-8').strip()
        print 'span is :' + span

        pattern = re.compile(r"(\d*)条\s*共(\d*)页")
        result = pattern.findall(span)
        print 'result is : ' + str(result)
        
        blog_count = int(result[0][0])
        page_count = int(result[0][1])
        
        return (blog_count, page_count)

    def _validate_redirect_url(self):
        response = self._session.get(CsdnHelper.blog_url)
        if(len(re.findall('var redirect = "(\S+)";', response.text))!=0):
            redirect_url = re.findall('var redirect = "(\S+)";', response.text)
            self._session.get(redirect_url)

    def print_blogs(self):
        
        blog_count, page_count = self._get_blog_count()

        for index in range(1, page_count + 1):
            print 'index:' + str(index);

            url = 'http://write.blog.csdn.net/postlist/0/0/enabled/'+str(index)
            response = self._session.get(url)
            page = BeautifulSoup(response.text, 'lxml')

            global nickName
            links = page.find_all('a', href=re.compile(r'http://blog.csdn.net/'+nickName+'/article/details/(\d+)'))

            for link in links:
                blog_name = link.string.encode('utf-8')
                blog_url = link['href']
                print blog_name
                print ('标题:<%s>   链接:%s') %(blog_name,blog_url)


if __name__ == '__main__':

    username = 'a422351001@gmail.com'
    password = '123mutouren789'

    csdn_helper = CsdnHelper()
    csdn_helper.login(username, password)
    csdn_helper.print_blogs()
else:
    print 'being imported as module'


    