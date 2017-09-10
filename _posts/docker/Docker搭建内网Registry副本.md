#Docker搭建内网Registry

因为自己的云主机pull/push image到Docker hub下载速度慢和经常性抽风，于是在自己的主机上搭建registry存放 image,简述搭建过程和列出遇到的坑。

## 准备工作
### docker容器启动配置文件

- 使用官方的镜像
- 暴露5000端口
- registry的image会存在 /tmp/registry中，如果主机重启了image就丢失了，所以挂载在本机
- 设定基本的变量环境

**docker-compose.yml**
```Markup
registry:
 image: registry
 ports:
   - "5000:5000"
 volumes:
   - /opt/data/registry:/tmp/registry
 environment:
   - STORAGE_PATH:/tmp/registry
   - SETTINGS_FLAVOR:dev
```

### nginx配置文件

- 将本机IP映射成域名
- 注意proxy_pass不带端口号

**default.conf**
``` Markup
# registry
server {
    listen       80 ;
    server_name docker.paraller.com;

    location / {
        proxy_pass http://$localeIP;
    }
}
```

###docker配置文件

- docker配置文件 centos在 /etc/sysconfig/docker ; ubuntu在 /etc/default/docker
- 因为默认是只允许https上传下载，所以要指定安全地址
- 重启docker服务 
**/etc/sysconfig/docker**
```Markup
other_args="--insecure-registry docker.paraller.com:5000"
```

### 打好tag的需要上传的镜像
```
docker tag paraller/nginx  docker.paraller.com:5000/paraller/nginx:3.0
```

## 开始运行

- docker-compose up -d registry
- service nginx start
- curl -i docker.paraller.com:5000
- curl -i http://docker.paraller.com:5000/v1/search
- docker push docker.paraller.com:5000/paraller/nginx:3.0
- ls /opt/data/registry/    //检查镜像是否存在
- docker pull docker.paraller.com:5000/paraller/nginx:3.0

## QA

1. 没有在docker文件配置过滤IP
```
Error response from daemon: invalid registry endpoint https://docker.paraller.com:5000/v0/: unable to ping registry endpoint https://docker.paraller.com:5000/v0/
v2 ping attempt failed with error: Get https://docker.paraller.com:5000/v2/: EOF
 v1 ping attempt failed with error: Get https://docker.paraller.com:5000/v1/_ping: EOF. If this private registry supports only HTTP or HTTPS with an unknown CA certificate, please add `--insecure-registry docker.paraller.com:5000` to the daemon's arguments. In the case of HTTPS, if you have access to the registry's CA certificate, no need for the flag; simply place the CA certificate at /etc/docker/certs.d/docker.paraller.com:5000/ca.crt
```
2.  标签制作错误
```
Repository XXX not found
```

#1
##2
###3
####4
#####5
######6
