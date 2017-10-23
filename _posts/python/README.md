博客同步系统.md

### 自动登录:

iteye
51cto


csdn

### API 

- 博客园


### 验证码

- 豆瓣

51CTO
iteye
新浪博客
百度百家
zhihu
开源中国
云栖

#### segmentfault
- 支持markdown格式的文章提交
- 一天提交不能超过30篇文章，超过之后需要填写验证码

#### 知乎
- 登录需要验证码
- 不支持markdown格式文章提交

#### CSDN
- 支持markdown格式的文章提交

## 流程

- 发起网址请求 获取图片验证码 保存本地
- 填写配置文件
- 登录。。。



- 读取配置文件登录信息
- 登录
- 遍历文件 - 读取历史上传文章
- 文章处理 ： 删除文件头 、删除图片base 、 删除 #号 、 文章头拼接paraller.com 地址
- 发送文章

## metaWeblog

地址	描述
http://imguowei.blog.51cto.com/xmlrpc.php	51cto
http://upload.move.blog.sina.com.cn/blog_rebuild/blog/xmlrpc.php	sina
http://write.blog.csdn.net/xmlrpc/index	csdn 
http://os.blog.163.com/word/	163
https://my.oschina.net/action/xmlrpc	oschina
http://www.cnblogs.com/apanly/services/metaweblog.aspx	cnblogs
http://blog.chinaunix.net/xmlrpc.php?r=rpc/server	chinaunix

## 参考

http://xmlrpc.scripting.com/metaWeblogApi.html
https://cyber.harvard.edu/blogs/gems/tech/sampleMetaweblogCall.txt
https://github.com/RussellLuo/pymwa



