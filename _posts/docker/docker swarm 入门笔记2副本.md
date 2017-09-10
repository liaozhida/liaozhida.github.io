## docker swarm 入门笔记2：使用docker swarm模式运行

**docker swarm mode 在 1.12版本及以上才可以使用。**
```
apt-get upgrade docker-engine
```

** 升级之后docker会重启 原来的容器要重新手动启动; docker配置文件也初始化了，需要重新配置 **,部分容器需要 rm 之后再启动

#### 概念介绍

##### manager节点

主要的工作范围：
- 维护集群状态
- 控制服务运行
- 提供swarm mode 的API

docker建议，为了实现高可用的架构，配对奇数的manager主机可以在故障中获得更高的恢复能力，最多不要超过七个manager主机
重要的是，配置更多的manager不会增加扩展性和更好的性能，恰恰相反，他提升的只是健壮性。


##### worker节点

只有一个节点主机的manager节点同时也是worker节点。worker节点必须已存于manager节点存在

### 准备3台主机

```
B:	112.74.22.65 	10.44.73.71   	[master : 可以做节点的同时 作为master]
A:	120.24.242.119 	10.170.48.177 
C:  8.250.169.6     172.20.3.42  [本机 内网]
```

### 创建manager

#### 指定成为manager

要记录下来生成的token值

```
$ docker swarm init --advertise-addr 112.74.22.65  //公网IP

Swarm initialized: current node (ru6m1erw0qwzi79xny43tiihp) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join \
    --token SWMTKN-1-2dxtk8zl8jx4tgkft7a3a9vv4krn5bwclzdelviztevrzda9u5-46lyortssxp89cvxuo7fenp4s \
    112.74.22.65:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```

#### 查看信息
```
$ docker info 

Swarm: active
 NodeID: ru6m1erw0qwzi79xny43tiihp
 Is Manager: true
 ClusterID: u9yd697us8yz9j47hezrqqmge
 Managers: 1
 Nodes: 1
 Orchestration:
  Task History Retention Limit: 5
 Raft:
  Snapshot Interval: 10000
  Number of Old Snapshots to Retain: 0
  Heartbeat Tick: 1
  Election Tick: 3
 Dispatcher:
  Heartbeat Period: 5 seconds
 CA Configuration:
  Expiry Duration: 3 months
 Node Address: 112.74.22.65
 Manager Addresses:
  112.74.22.65:237
```
 
#### 列出节点信息

```
docker node ls

ID                           HOSTNAME            STATUS  AVAILABILITY  MANAGER STATUS
ru6m1erw0qwzi79xny43tiihp *  yeamoneytestserver  Ready   Active        Leader
```
* 代表的是你目前连接的就是该节点


### 加入Swarm集群

```
$ docker swarm join \
  --token  SWMTKN-1-2dxtk8zl8jx4tgkft7a3a9vv4krn5bwclzdelviztevrzda9u5-46lyortssxp89cvxuo7fenp4s \
  112.74.22.65:2377

This node joined a swarm as a worker.

```

如果不知道执行什么命令或者Token信息，可以在manager 主机中执行命令获取信息

```
$docker swarm join-token worker
To add a worker to this swarm, run the following command:

    docker swarm join \
    --token SWMTKN-1-2dxtk8zl8jx4tgkft7a3a9vv4krn5bwclzdelviztevrzda9u5-46lyortssxp89cvxuo7fenp4s \
    112.74.22.65:2377
```

### 在Swarm上部署服务

```
$ docker service create --replicas 3 --name helloworld alpine ping docker.com
22q8v5d6yir22t0ywjbyf1tfn
```

 
- The --name flag names the service helloworld. // 服务的名字
- The --replicas flag specifies the desired state of 3 running instance.  // 代表要在几个主机上运行
- The arguments alpine ping docker.com define the service as an Alpine Linux container that executes the command ping docker.com.  //启动之后的命令



```
$ docker service ls
ID            NAME        MODE        REPLICAS  IMAGE
22q8v5d6yir2  helloworld  replicated  0/1       alpine:latest
```

### 查看Service详情

```
$  docker service inspect --pretty helloworld

ID:   22q8v5d6yir22t0ywjbyf1tfn
Name:   helloworld
Service Mode: Replicated
 Replicas:  1
Placement:
UpdateConfig:
 Parallelism: 1
 On failure:  pause
 Max failure ratio: 0
ContainerSpec:
 Image:   alpine:latest@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7
 Args:    ping docker.com
Resources:
Endpoint Mode:  vip
```

查看Service列表

```
$  docker service ps helloworld
ID            NAME              IMAGE          NODE                DESIRED STATE  CURRENT STATE                     ERROR                             PORTS
wbc2qo4xiric  helloworld.1      alpine:latest  yeamoneytestserver  Ready          Preparing less than a second ago
tzeews7o6qgk   \_ helloworld.1  alpine:latest  yeamoneytestserver  Shutdown       Rejected less than a second ago   "No such image: alpine@sha256:…"
kv22f41cvwxv   \_ helloworld.1  alpine:latest  iZ94dvsgdg7Z        Shutdown       Rejected 9 seconds ago            "No such image: alpine@sha256:…"
rb0rovqabpwp   \_ helloworld.1  alpine:latest  iZ94dvsgdg7Z        Shutdown       Rejected 15 seconds ago           "No such image: alpine@sha256:…"
s7106q2l0xk8   \_ helloworld.1  alpine:latest  yeamoneytestserver  Shutdown       Rejected 21 seconds ago           "No such image: alpine@sha256:…"

```

增加`--no-trunc` 可以查看详细信息

```
$  docker service ps helloworld --no-trunc
ID                         NAME              IMAGE                                                                                  NODE                DESIRED STATE  CURRENT STATE            ERROR                                                                                            PORTS
lodhjc9wlmu15zwoyjapdk3c7  helloworld.1      alpine:latest@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7  yeamoneytestserver  Running        Preparing 6 seconds ago
jlfhmt7xzlrm6rqzd03k4n62o   \_ helloworld.1  alpine:latest@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7  iZ94dvsgdg7Z        Shutdown       Rejected 6 seconds ago   "No such image: alpine@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7"
tq3o5d2jz0nxti84nzpbmmouw   \_ helloworld.1  alpine:latest@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7  yeamoneytestserver  Shutdown       Rejected 11 seconds ago  "No such image: alpine@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7"
```

可以得知，node节点没有拉取相应的镜像；解决方案在每个node节点 docker pull alpine
docker service rm & create 重新运行

```
$  docker service ps helloworld
ID            NAME          IMAGE          NODE                DESIRED STATE  CURRENT STATE          ERROR  PORTS
n2947klyctmh  helloworld.1  alpine:latest  iZ94dvsgdg7Z        Running        Running 2 minutes ago
5n9x4rvwspqj  helloworld.2  alpine:latest  moby                Running        Running 2 minutes ago
qw4g0aypnkur  helloworld.3  alpine:latest  yeamoneytestserver  Running        Running 2 minutes ago
```

```
$  docker ps
CONTAINER ID        IMAGE                                                                            COMMAND                  CREATED             STATUS              PORTS                                      NAMES
f219db9fcff1        alpine@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7   "ping docker.com"        2 minutes ago       Up 2 minutes                                                   helloworld.3.jxd8hgvs98ae52qvep7lwmyvi
```

在node主机上执行命令  `docker ps`

```
$ docker ps
CONTAINER ID        IMAGE                                                                            COMMAND                  CREATED             STATUS              PORTS                         NAMES
6d63dd6bbbdc        alpine@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7   "ping docker.com"        4 minutes ago       Up 4 minutes                                      helloworld.2.5n9x4rvwspqj4903kqz84iopd
```

### 移除服务

```
$ docker service rm helloworld

helloworld

```

service被移除之后，所有节点的container都会在几秒之后结束并移除

### 在Swarm上分配服务

需要启动几个容器，执行命令`docker service scale helloworld=5` , 每个主机的容器数量随机分配

```
$ docker service scale helloworld=5

helloworld scaled to 5

$  docker service ps helloworld
ID            NAME          IMAGE          NODE                DESIRED STATE  CURRENT STATE                   ERROR  PORTS
n2947klyctmh  helloworld.1  alpine:latest  iZ94dvsgdg7Z        Running        Running 9 minutes ago
5n9x4rvwspqj  helloworld.2  alpine:latest  moby                Running        Running 9 minutes ago
qw4g0aypnkur  helloworld.3  alpine:latest  yeamoneytestserver  Running        Running 9 minutes ago
1ndfe9yzs55u  helloworld.4  alpine:latest  yeamoneytestserver  Running        Running 1 second ago
l9tcsfqxky8l  helloworld.5  alpine:latest  moby                Running        Running less than a second ago

切到 moby 主机
$ docker ps 
CONTAINER ID        IMAGE                                                                            COMMAND                  CREATED             STATUS              PORTS                         NAMES
a0625111077f        alpine@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7   "ping docker.com"        58 seconds ago      Up 57 seconds                                     helloworld.5.l9tcsfqxky8ljuiqwbao0f1wb
6d63dd6bbbdc        alpine@sha256:b5a9cf627a1c875cd5574c7350dffea043f1bd6e0e40e4d437b542b7c94060b7   "ping docker.com"        10 minutes ago      Up 10 minutes                                     helloworld.2.5n9x4rvwspqj4903kqz84iopd

```

### 服务的滚动升级

以docker 的redis镜像为例，进行滚动升级

```
$  docker service create \
>   --replicas 3 \
>   --name redis \
>   --update-delay 10s \
>   redis:3.0.6
3k5xzlv2tg7amzr77c9kypcvi
 
$  docker service ps redis
ID            NAME     IMAGE        NODE                DESIRED STATE  CURRENT STATE             ERROR  PORTS
f7sbx3axuhem  redis.1  redis:3.0.6  iZ94dvsgdg7Z        Running        Preparing 13 seconds ago
lvwmh5n36r89  redis.2  redis:3.0.6  moby                Running        Preparing 13 seconds ago
q2gryyfmhmci  redis.3  redis:3.0.6  yeamoneytestserver  Running        Preparing 13 seconds ago
```

`--update-delay 10s `
number of seconds Ts, minutes Tm, or hours Th. So 10m30s indicates a 10 minute 30 second delay.


升级操作

```
$ docker service update --image redis:3.0.7 redis
redis
```

```
$  docker service ps redis
ID            NAME         IMAGE        NODE                DESIRED STATE  CURRENT STATE                ERROR                             PORTS
pzvi1k61umor  redis.1      redis:3.0.7  moby                Running        Running 48 seconds ago
yawrbq0g3fpv   \_ redis.1  redis:3.0.7  moby                Shutdown       Rejected 57 seconds ago      "No such image: redis@sha256:0…"
33os4jg92o14   \_ redis.1  redis:3.0.7  moby                Shutdown       Rejected about a minute ago  "No such image: redis@sha256:0…"
zpj717ncsube   \_ redis.1  redis:3.0.7  moby                Shutdown       Rejected about a minute ago  "No such image: redis@sha256:0…"
mkxxhw4htv3j   \_ redis.1  redis:3.0.7  moby                Shutdown       Rejected about a minute ago  "No such image: redis@sha256:0…"
nwkdiqkb126p  redis.2      redis:3.0.6  yeamoneytestserver  Running        Running 2 minutes ago
xbv2hdeu0wh4  redis.3      redis:3.0.6  iZ94dvsgdg7Z        Running        Running 2 minutes ago
```
出现Rejected的状态是因为，moby这个主机原来没有redis:3.0.7的镜像，所以导致失败，docker service会不断的进行重试，docker pull redis:3.0.7之后就恢复正常了.

删除服务，重新创建服务运行,旧版本的容器停止，新版本的正常运行

```
$  docker service ps redis
ID            NAME         IMAGE        NODE                DESIRED STATE  CURRENT STATE            ERROR  PORTS
7ctslgzycqt8  redis.1      redis:3.0.7  yeamoneytestserver  Running        Running 3 seconds ago
fwoujxg3k0j1   \_ redis.1  redis:3.0.6  yeamoneytestserver  Shutdown       Shutdown 3 seconds ago
5xveo7ww9x4u  redis.2      redis:3.0.7  iZ94dvsgdg7Z        Running        Running 15 seconds ago
dsu51uzw1kst   \_ redis.2  redis:3.0.6  iZ94dvsgdg7Z        Shutdown       Shutdown 16 seconds ago
pr9fe8sbgv3h  redis.3      redis:3.0.7  moby                Running        Running 27 seconds ago
dm806ra8f9p7   \_ redis.3  redis:3.0.6  moby                Shutdown       Shutdown 28 seconds ago
```

具体的实施步骤如下：

Stop the first task.
Schedule update for the stopped task.
Start the container for the updated task.
If the update to a task returns RUNNING, wait for the specified delay period then stop the next task.
If, at any time during the update, a task returns FAILED, pause the update.


查看更新信息,**如果更新失败了可以执行这条命令查看原因**

```
 docker service inspect --pretty redis

ID:   x3wr1no0wbf8l5av85hqjtp9t
Name:   redis
Service Mode: Replicated
 Replicas:  3
UpdateStatus:
 State:   completed
 Started: 3 minutes
 Completed: 2 minutes
 Message: update completed
Placement:
UpdateConfig:
 Parallelism: 1
 Delay:   10s
 On failure:  pause
 Max failure ratio: 0
ContainerSpec:
 Image:   redis:3.0.7@sha256:012d414140999cee2e890ac0a590151d8691fe80f636a9f17a426458f82f7a3d
Resources:
Endpoint Mode:  vip
```

升级出现异常，找到问题并解决之后，可以执行命令继续更新 `docker service update redis`

### 暂停节点

当系统维护的时候，我们可能需要节点不再接收master的命令，可以启用节点的DRAIN功能

我们以moby这个主机为例

原状态:

```
$  docker node inspect --pretty moby
ID:     wpeadffp8bsuyc51akzd2ye6f
Hostname:   moby
Joined at:    2017-02-03 05:56:18.112350834 +0000 utc
Status:
 State:     Ready
 Availability:    Active
 Address:   58.250.169.6
Platform:
 Operating System:  linux
 Architecture:    x86_64
Resources:
 CPUs:      2
 Memory:    1.952 GiB
Plugins:
  Network:    bridge, host, ipvlan, macvlan, null, overlay
  Volume:   local
```

执行命令 `docker node update --availability drain moby`

```
$  docker node inspect --pretty moby
ID:     wpeadffp8bsuyc51akzd2ye6f
Hostname:   moby
Joined at:    2017-02-03 05:56:18.112350834 +0000 utc
Status:
 State:     Ready
 Availability:    Drain
 Address:   58.250.169.6
Platform:
 Operating System:  linux
 Architecture:    x86_64
Resources:
 CPUs:      2
 Memory:    1.952 GiB
Plugins:
  Network:    bridge, host, ipvlan, macvlan, null, overlay
  Volume:   local
Engine Version:   1.13.0

```

查看服务的运行情况,moby的容器停止运行，然后master会保持三个容器的状态，选择一个主机运行容器

```
$  docker service ps redis
ID            NAME         IMAGE        NODE                DESIRED STATE  CURRENT STATE                ERROR  PORTS
7ctslgzycqt8  redis.1      redis:3.0.7  yeamoneytestserver  Running        Running 19 minutes ago
fwoujxg3k0j1   \_ redis.1  redis:3.0.6  yeamoneytestserver  Shutdown       Shutdown 19 minutes ago
5xveo7ww9x4u  redis.2      redis:3.0.7  iZ94dvsgdg7Z        Running        Running 19 minutes ago
dsu51uzw1kst   \_ redis.2  redis:3.0.6  iZ94dvsgdg7Z        Shutdown       Shutdown 19 minutes ago
p6vfvxyhavej  redis.3      redis:3.0.7  yeamoneytestserver  Running        Running about a minute ago
pr9fe8sbgv3h   \_ redis.3  redis:3.0.7  moby                Shutdown       Shutdown about a minute ago
dm806ra8f9p7   \_ redis.3  redis:3.0.6  moby                Shutdown       Shutdown 19 minutes ago
```

恢复节点的运行状态 `docker node update --availability active moby`
原来暂停的容器不会重新运行，但是这个node会重新开始接受master的命令



### Swarm网络

docker engine swarm mode 使服务很容易的就可以暴露公共端口给Swarm之外的资源访问，所有的node参与到进这一个路由网络
这个路由网络可以让每个node在swarm中去连接到任意的运行服务（即使不在自己的node中或者自己的node中没有运行任何的任务）。
路由网路中的所有请求都可以分配到任意的运行容器中

为了达到以上的目的，在运行swarm mode前，必须保证每个node主机开放以下端口
- 7946 TCP/UDP for container network discovery.
- 4789 UDP for the container ingress network.

```
docker service create \
  --name my-web \
  --publish 8080:80 \
  --replicas 3 \
  nginx
```

当你在任意节点访问8080端口的时候，Swarm负载均衡器会指定一个活跃的节点。

```

192.169.0.1:8080            192.169.0.1:8080            192.169.0.1:8080 
-----------------------------------------------------------------------------
        |                           |                           |
  swarm load balance         swarm load balance         swarm load balance
        \                           |                            /
        |  \                        |                           /
        |    \                      |                         / 
        |     \                     |                      /
        |        \                  |                     /
        |          \                |                   / 
        |            \              |                 /
        |              \            |               / 
        |                \          |             /
        |                  \        |          /
        |                    \      |        /
        |                      \    |      /
      80-web1                   80-web2                       
      node1                       node2                      node3
-----------------------------------------------------------------------------
                              ingress network

```

##### 更新已经运行的服务

```
$ docker service update \
  --publish-add <PUBLISHED-PORT>:<TARGET-PORT> \
  <SERVICE>
```

查看网路详情：

```
docker service inspect --format="" my-web
```

#### 只发布TCP或者UDP的端口

docker 默认发布的是TCP协议的端口。

##### TCP only

```
$ docker service create --name dns-cache -p 53:53 dns-cache
$ docker service create --name dns-cache -p 53:53/tcp dns-cache

两个的命令是等价的
```

##### TCP and UDP

```
$ docker service create --name dns-cache -p 53:53/tcp -p 53:53/udp dns-cache
```

##### UDP only

```
$ docker service create --name dns-cache -p 53:53/udp dns-cache
```

#### 配置外部的 负载均衡器 (HAProxy)

在这个案例中，8080端口必须对负载均衡器和swarm中的node主机开放，负载均衡器能够访问到私有网络，但是外部是无法访问的



```
                                  HAProxy 

        /                            |                          \ 

192.169.0.1:8080            192.169.0.1:8080            192.169.0.1:8080 
-----------------------------------------------------------------------------
        |                           |                           |
  swarm load balance         swarm load balance         swarm load balance
        \                           |                            /
        |  \                        |                           /
        |    \                      |                         / 
        |     \                     |                      /
        |        \                  |                     /
        |          \                |                   / 
        |            \              |                 /
        |              \            |               / 
        |                \          |             /
        |                  \        |          /
        |                    \      |        /
        |                      \    |      /
      80-web1                   80-web2                       
      node1                       node2                      node3
-----------------------------------------------------------------------------
                              ingress network

```

### worker节点升级为manager

让一或多个node主机升级为manager

```
docker node promote NODE [NODE...]
```



[Getting started with swarm mode](https://docs.docker.com/engine/swarm/swarm-tutorial/)
[Create Swarm](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/)
[docker node promote](https://docs.docker.com/engine/reference/commandline/node_promote/)
