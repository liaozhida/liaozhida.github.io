## Docker几种网络类型

容器连接的方式 

1.内部网络
2.Docker Networking
3.Docker link



Docker内部连网概念

1. 安装Docker时，会创建一个新的网络接口，名字是docker0
2. Docker每创建一个容器就会创建一组互联的网络接口
3. Docker创建了一个虚拟子网，由宿主机和所有的Docker容器共享



Docker Networking查看信息

docker network inspect appName

将已有的容器添加到Docker Networking中

docker network connect app redis_yea


Docker Networking使用说明

1.创建一个网络 docker network create app
2.在该网络下启动容器 docker run -d --net=app

1.如果要跨主机进行通信，需要创建overlay网络
2.一个容器可以隶属与多个Docker网络


如何使用Docker链接

1.创建一个容器，指定名字 docker run --name=redisj
2.启动一个容器 使用--link参数
 --link redisj:db
3.链接在一起之后，客户容器可以直接访问服务容器的所有端口


Docker内部连网的缺点

1.IP地址需要硬编码
2. 如果重启容器，地址会发生改变


在docker networing中断开一个容器

docker network disconnect app redis_yea

[第一本Docker书]


### 默认网络

### 用户自定义网络

### 全覆盖网络 An overlay network

[Understand Docker container networks](https://docs.docker.com/v1.10/engine/userguide/networking/dockernetworks/#an-overlay-network)