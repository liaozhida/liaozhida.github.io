# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
import time  



class CaptchaHelper:

    def __init__(self):
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Host':'www.zhihu.com',
            'Origin':'https://www.zhihu.com',
            'Referer':'https://www.zhihu.com',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
        }

        data_file = open('config.json') 
        self.data = json.load(data_file)
        self._session = requests.session()

    def douban(self):
        url = self.data["douban"]["captcha-url"]
        response = self._session.get(url)
        
        # print response.text

        page = BeautifulSoup(response.text, 'lxml')
        captcha_id = page.find('input', attrs={'name':'captcha-id'})['value'] 
        imageurl = page.find('img', alt='captcha')['src']

        response = requests.get(imageurl, stream=True)
        with open('./captcha/douban.png', 'wb') as f:
            f.write(response.content)
            f.close
            del response

        self.data['douban']['captcha-id'] = captcha_id
        print self.data
        file = open('config.json','w')
        file.write('\r\n')
        json.dump(self.data,file);
        file.close()


    def zhihu(self):

        # 获取验证码链接
        imageurl = self.data['zhihu']['captcha-url']
        print imageurl

        imageurl = 'http://www.zhihu.com/captcha.gif?r=%d&type=login';
        response = self._session.get(imageurl % (time.time() * 1000), headers=self.headers)

        # 保存验证码到本地
        with open('./captcha/zhihu.png', 'wb') as f:
            f.write(response.content)
            f.close
            del response

        # 写入cookie信息
        file = open('zhihu_cookies','w');
        cookies = self._session.cookies.get_dict()  
        json.dump(cookies, file)  
        file.close()





if __name__ == '__main__':

    ch = CaptchaHelper();
    # ch.douban()
    ch.zhihu();

else:
    print 'being imported as module'
