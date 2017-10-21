import urllib2
import urllib




def login():

    login_url='https://passport.csdn.net/account/login?ref=toolbar'
    login_data = urllib.urlencode({
                                    "username": 'a422351001@gmail.com',
                                    "password": '123mutouren789',
                                    "it": "LT-791142-3oJYvogL9gm0bdbHy2nT1bwCptE3oe",
                                    "execution":"e14s1",
                                    "_eventId":"submit"
                                });

    try:
        
        request = urllib2.Request(login_url, data=login_data)
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0")
        response = urllib2.urlopen(request)
        
        headers = response.info()
        # print headers

        jid = str(headers).partition('JSESSIONID')[2].partition(';')[0].lstrip().rstrip();
        jid = jid[1:len(jid)]
        # print jid

        # print response.read()

    except urllib2.HTTPError,e:
        print e.getcode()
        # print e.reason                    

def post():
    print 'start'
    post_url = 'http://write.blog.csdn.net/postedit?edit=1&isPub=1&joinblogcontest=undefined&r=0.44241328025450444';

    post_data = urllib.urlencode({
                                    "titl": 'hello',
                                    "typ": '2',
                                    "cont": "<p>hello world&nbsp;</p><p>test&nbsp;</p>",
                                    "comm":"2",
                                    "checkcode":"undefined",
                                    "userinfo1":"1120",
                                    "stat":"publish",
                                    "level":"0",
                                    "artid":"0",
                                    "chnl":"0"
                                });

    try:
        request = urllib2.Request(post_url, data=post_data)
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0")
        request.add_header("UserInfo", "6qNShpjXL3H57ZcM6XumvrH166Cl5kMEtsCsCycTdx6xeXjlgCHvWnlheYRYeG6A1XeVuzM696yt4WiiWkXrIgGwCiQxaQwcYzq8Dwo2J2NJh9awswSruFZj7wfcdcqY3wzVI%2F216Vqv%2BsP8B6O%2FBQ%3D%3D")
        response = urllib2.urlopen(request)
        
        headers = response.info()
        print headers


        print response.read()

    except urllib2.HTTPError,e:
        print e.getcode()
        # print e.reason       


# login();
post();