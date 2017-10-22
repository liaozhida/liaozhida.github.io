python网站登录.md

## segmentfault

#### 思路步骤

###### 启动charles 进行抓包准备 

###### 打开登录页面，然后输入账号密码登录，查看抓包信息

###### 复制登录请求的 request header信息
```
"Host": "segmentfault.com",
"Connection": "keep-alive",
"Content-Length": "55",
"Accept": "*/*",
"Origin": "https://segmentfault.com",
"X-Requested-With": "XMLHttpRequest",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
"DNT": "1",
"Referer": "https://segmentfault.com/",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2",
"Cookie": "PHPSESSID=web3~fdf535b2518f7f061780d987bb65934a; _gat=1; io=onpREhr-L-d7pRxJHvSF; Hm_lvt_e23800c454aa573c0ccb16b52665ac26=1508383051,1508500169,1508563643,1508565378; Hm_lpvt_e23800c454aa573c0ccb16b52665ac26=1508569683; _ga=GA1.2.613128477.1495522770; _gid=GA1.2.1217955936.1508498183",
"Pragma": "no-cache",
"Cache-Control": "no-cache"
```

#### 遇到的问题


#### 参考网站

[guzzle post 请求 segmentfault 登录 api, response返回 404，错在哪儿呢？](https://segmentfault.com/q/1010000009734004) 
[爬虫模拟登陆 SegmentFault](http://www.voidcn.com/article/p-hqajlhtu-c.html)

