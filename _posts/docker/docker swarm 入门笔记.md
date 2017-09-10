docker swarm 入门笔记1

**docker swarm 简单的理解就是用 docker remote Api 对其他主机上的docker 容器进行操作**

这一篇文章是比较旧的实现方式，1.12之后的版本引入了Swarm mode ，更加的方便，参考《docker swarm 入门笔记2》

### 原理

- 每个主机拉取一个swarm镜像，启动；
- 运行swarm容器，在Docker hub 中注册地址和token，所以不适用于生产环境
- 因为每个docker配置文件都开放了地址，所以能远程操作


### swarm 过滤器和策略

- 过滤器是指启动什么指定的docker主机容器
- 策略是指主机优先级使用

### 准备两台主机

```
A:	120.24.242.119 	10.170.48.177 	192.168.0.1
B:	112.74.22.65 	10.44.73.71 	192.168.0.1  [master : 可以做节点的同时 作为master]
```

### 系统:
ubuntu

### 修改docker配置文件：

```
vim /etc/default/docker 

-H tcp://0.0.0.0:2375
-H unix:///var/run/docker.sock

不然会报错：
Cannot connect to the Docker daemon. Is the docker daemon running on this host?
```

### 安装docker swarm

```
docker pull swarm:latest
```

### 创建集群密钥 token/cluster_id

```
node B:
docker run --rm swarm create
2f7b78725e94cae1ba3098ad5c6398b1
```

### 注册节点

```
node A:
docker run -d swarm join --addr=:10.170.48.177 token://2f7b78725e94cae1ba3098ad5c6398b1
6f824e607558685554e37e4a7adaf37e1286843fef1a6a2118cea2951aabb66a

node B:
docker run -d swarm join --addr=:10.44.73.71 token://2f7b78725e94cae1ba3098ad5c6398b1
40e9645a7a250621a0f3cf0ee436085faa4b120bcd33a753f9b2e9f339236660
```

### 注册master节点

```
docker run -t -p 2376:2375 -t swarm manage token://2f7b78725e94cae1ba3098ad5c6398b1 &
```

### 查看
                                                                                                                                                                                                                                                
```
docker -H tcp://10.170.48.177:2375  info
docker -H tcp://10.44.73.71:2375  info
docker -H tcp://10.170.48.177:2375  ps
docker -H tcp://10.170.48.177:2375  logs

在master中查看多少节点： [亲测无效...]
docker run --rm swarm list token://2f7b78725e94cae1ba3098ad5c6398b1

```

### 操纵

```
docker -H tcp://10.170.48.177:2375  run -d nginx
```

### TLS

```
swarm manage --tlsverify --tlscacert=<CACERT> --tlscert=<CERT> --tlskey=<KEY> [...]
```



参考网站
[dockerhub swam](https://hub.docker.com/_/swarm/) 
[Swarm mode overview](https://docs.docker.com/engine/swarm/)
[Swarm Command](https://docs.docker.com/swarm/reference/swarm/)





1