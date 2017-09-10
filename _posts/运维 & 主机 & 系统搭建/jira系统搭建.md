# jira系统搭建实战.md

下载镜像
配置docker-compose.yml
create database jira 
set it myself
generate key   jira software(server)  -> up and running

zhida.liao@yeamoney.cn 
username : zhida
pass:liaozhida

create new project

download https://translations.atlassian.com/dashboard/download?lang=zh_CN#/JIRA Core/7.2.7 

system - >edit setting - change language



jira系统搭建.md


```
root@iZ94ft8hgzqZ:/data/git/aliyun/jira# ls -al
total 238552
drwxr-xr-x  3 root root      4096 May 25 21:47 .
drwxr-xr-x 13 root root      4096 May 20  2016 ..
-rw-r--r--  1 root root       566 Nov 16  2015 Dockerfile
-rw-r--r--  1 root root      2052 Jul  5  2015 Readme.md
-rw-r-----  1 root root 244240844 Nov 23  2015 atlassian-jira-6.3.6.tar.gz
-rw-r--r--  1 root root       444 May 25 21:47 docker-compose.yml
-rw-r--r--  1 root root       365 Jul  5  2015 init.sh
drwxr-xr-x  4 root root      4096 Nov 23  2015 lib
-rw-r--r--  1 root root      1015 Jul  5  2015 setup.md
```

docker-compose.yml

```
jira:
#  image: umiit/jira:6.3.6
  build: ./
  ports:
    - "127.0.0.1:8082:8080"
  links:
    - mysql:mysql
  environment:
    VIRTUAL_HOST: jira.umiit.cn
  volumes:
    - /etc/localtime:/etc/localtime:ro
    - /root/docker-data/jira-new:/root/jira_home
mysql:
  image: mysql:5.6
  environment:
    MYSQL_ROOT_PASSWORD: "mysecretpassword"
  volumes:
    - /etc/localtime:/etc/localtime:ro
    - /root/docker-data/jira-mysql-new:/var/lib/mysql
```

Dockerfile

```
from java:7

ADD ./atlassian-jira-6.3.6.tar.gz /root/atlassian-jira-6.3.6.tar.gz
ADD ./lib /root/lib

RUN mv /root/atlassian-jira-6.3.6.tar.gz/atlassian-jira-6.3.6-standalone/ /opt/jira
RUN chown -R -v root:root /opt/jira
RUN mv /root/lib/before/*.jar /opt/jira/atlassian-jira/WEB-INF/lib
RUN rm /opt/jira/atlassian-jira/WEB-INF/classes/jira-application.properties
RUN echo 'jira.home = /root/jira_home' > /opt/jira/atlassian-jira/WEB-INF/classes/jira-application.properties

ADD ./init.sh /init
RUN chmod +x /init

expose 8080
VOLUME /root/jira_home

cmd ["/init"]
```

init.sh 
```
#!/bin/bash

if [ -f /root/jira_home/dbconfig.xml ]; then
   if [ -f /root/lib/after/atlassian-extras-2.2.2.jar ]; then
                mv /root/lib/after/atlassian-universal-plugin-manager-plugin-2.17.13.jar /opt/jira/atlassian-jira/WEB-INF/atlassian-bundled-plugins
                mv /root/lib/after/*.jar /opt/jira/atlassian-jira/WEB-INF/lib
   fi
fi

/opt/jira/bin/start-jira.sh -fg
```


setup.md

```
系统配置
==============

1. 更新docker

	apt-get update
	apt-get install lxc-docker

2. 挂载硬盘

	fdisk -l
	fdisk /dev/xvdb
	输入n 剩余回车
	mkfs.ext4 /dev/xvdb1
	mkdir /data
	mount /dev/xvdb1 /data
	vi /etc/fstab
	写入  /dev/xvdb1  /data  ext4    defaults  0 0
	重启 df 验证

3. 设置软连接
    mkdir /data/git
    mkdir /data/docker-data
    ln -s /data/git ~/
    ln -s /data/docker-data ~/

4. [配置docker加速](https://dashboard.daocloud.io/mirror)

	echo "DOCKER_OPTS=\"\$DOCKER_OPTS --registry-mirror=http://bf1f1b58.m.daocloud.io\"" | sudo tee -a /etc/default/docker
	sudo service docker restart

5. docker-compose

	wget https://github.com/docker/compose/releases/download/1.2.0/docker-compose-`uname -s`-`uname -m`
	mv docker-compose-Linux-x86_64 /usr/local/bin/docker-compose
	chmod +x /usr/local/bin/docker-compose

6. [nginx-proxy](https://github.com/jwilder/nginx-proxy)

	docker pull jwilder/nginx-proxy:latest

6. 可选服务

	registry gitblit jira jenkins nexus
```

Readme.md

```
jira安装配置
==================

0. 去百度云下载安装文件jira,对应lib的路径

1. 配置数据库

docker run --name mysql_default -d -e MYSQL_ROOT_PASSWORD=mysecretpassword -v /etc/localtime:/etc/localtime:ro -v /root/docker-data/jira-mysql:/var/lib/mysql mysql:latest

docker run -it --rm  --link mysql_default:mysql -e MYSQL_ROOT_PASSWORD=mysecretpassword -v /etc/localtime:/etc/localtime:ro -v /root/docker-data/jira-mysql:/var/lib/mysql mysql:latest sh -c 'exec mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"
$MYSQL_ENV_MYSQL_ROOT_PASSWORD"'

CREATE DATABASE `jira` DEFAULT CHARACTER SET utf8;

GRANT ALL ON jira.* TO jira_user@'%' IDENTIFIED BY 'jira_pwd';

docker stop mysql_default
docker rm mysql_default

2. 破解
Description=JIRA: Commercial,
CreationDate=2004-05-31,
jira.LicenseEdition=ENTERPRISE,
Evaluation=false,
jira.LicenseTypeName=COMMERCIAL,
jira.active=true,
licenseVersion=2,
MaintenanceExpiryDate=2099-12-31,
Organisation=saper,
SEN=SEN-L4140432,
ServerID=BQJE-RNSR-9NMG-JDWN,
jira.NumberOfUsers=-1,
LicenseID=LIDSEN-L4140432,
LicenseExpiryDate=2099-12-31,
PurchaseDate=2004-05-31

Description=JIRA Agile (formerly GreenHopper) for JIRA\: Commercial,
NumberOfUsers=-1,
CreationDate=2014-08-01,
Evaluation=false,
greenhopper.LicenseEdition=ENTERPRISE,
licenseVersion=2,
MaintenanceExpiryDate=2099-01-01,
Organisation=saper,
greenhopper.active=true,
SEN=SEN-L4390388,
ServerID=BQJE-RNSR-9NMG-JDWN,
LicenseExpiryDate=2099-01-01,
LicenseTypeName=COMMERCIAL,
PurchaseDate=2014-08-01

Description=Git Integration Plugin for JIRA\: Commercial,
NumberOfUsers=-1,
CreationDate=2014-08-01,
Evaluation=false,
com.xiplink.jira.git.jira_git_plugin.LicenseEdition=ENTERPRISE,
com.xiplink.jira.git.jira_git_plugin.active=true,
licenseVersion=2,
MaintenanceExpiryDate=2099-01-01,
Organisation=saper,
SEN=SEN-L4390388,
ServerID=BQJE-RNSR-9NMG-JDWN,
LicenseExpiryDate=2099-01-01,
LicenseTypeName=COMMERCIAL,
PurchaseDate=2014-08-01

3.中文化
进入系统，系统信息-》编辑

4.安装插件
```

user Info

```
a422351001@gmail.com
```