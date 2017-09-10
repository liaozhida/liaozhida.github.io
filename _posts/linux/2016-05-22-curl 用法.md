

#### GET

```
curl -G url
```

#### POST

```

curl -X POST -d
curl -X POST --data 
curl --request POST https://example.com/resource.cgi
curl -H "Content-Type: application/json" -X POST -d '{"username":"xyz","password":"xyz"}' http://localhost:3000/api/login

```
#### PUT

```
curl -X PUT -d arg=val -d arg2=val2 localhost:8080
```

#### DELETE

```
curl -X "DELETE" http://www.url.com/page

```



- curl --form "fileupload=@my-file.txt" https://example.com/resource.cgi
- curl --data "param1=value1&param2=value2" https://example.com/resource.cgi
- -F 上传文件 curl -F upload=@localfilename -F press=OK URL
- curl -i  输出时包括protocol头信息
- 认证 curl -u name:password www.secrets. com
- -v 输出时打印详细信息
- -# 用进度条显示当前的传送状态
- O 保留文件名