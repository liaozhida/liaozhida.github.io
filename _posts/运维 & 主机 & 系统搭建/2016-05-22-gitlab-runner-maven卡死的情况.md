---
layout:     post
title:      "gitlab-runner-maven卡死的情况"
date:       2016-05-22 12:00:00
author:     "zhida.liao"
header-img: "img/post-bg-2015.jpg"
tags:
    - 运维 & 主机 & 系统搭建
    - gitlab
---

## 起因：
项目中遇到的情况，gitlab-docker runner在构建项目的时候，
总会在download jar包或者pom文件的时候挂起，每次都是在不同的下载文件中卡住

## 原因分析：
- maven 服务器是内网搭建的，所以不存在网络不通畅的问题。
- 每次项目构建时间都比较长，有可能是docker runner存在超时的问题 ，寻找各种资料无果放弃；
- 既然每次都是不同的Jar包卡住，就有可能这个卡住的jar上次有成功下载的情况；于是将重点放在缓存

## 针对第三点的解决方案：

1、宿主机 install maven2 ,cd /root && vim  settings.xml；配置镜像服务器和仓库地址

2、浏览docker-compose.yml ；调整配置 /root/.m2

```
grdocker:
  image: gitlab/gitlab-runner:latest
  restart: always
  volumes:
    - /root/docker-data/gitlab-runner/docker/config:/etc/gitlab-runner
    - /var/run/docker.sock:/var/run/docker.sock
    - /data/git/aliyun/gitlab/hosts:/etc/hosts
    - /root/.m2:/root/.m2
    - /usr/bin/docker:/usr/bin/docker
```

3、vim /data/docker-data/gitlab-runner/docker/config/config.toml ; 添加volumes

```
concurrent = 2

[[runners]]
  name = "docker"
  url = "http://gitlab.umiit.cn/ci"
  token = "65331a98de9d6780c9f3403f14b9c6"
  tls-ca-file = ""
  executor = "docker"
  [runners.docker]
    image = "ubuntu:14.04"
    privileged = false
    volumes = ["/cache","/root/.m2:/root/.m2","/var/run/docker.sock:/var/run/docker.sock"]
```

## 结果
runner 在构建的时候不在卡死，jar包在很短的时间内下载或缓存定位完毕；

## 参考网站
(docker runner cache maven repository)[https://gitlab.com/gitlab-org/gitlab-ce/issues/15167]