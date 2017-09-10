# zookeeper 实战.md

## 入门教程

- 主要用来解决分布式集群中应用系统的一致性问题
- 让我们首先讨论一下为什么想使用 ZooKeeper。ZooKeeper 是一个面向分布式系统的构建块。当设计一个分布式系统时，一般需要设计和开发一些协调服务：

### 概念

**名称服务**
名称服务是将一个名称映射到与该名称有关联的一些信息的服务。电话目录是将人的名字映射到其电话号码的一个名称服务。同样，DNS 服务也是一个名称服务，它将一个域名映射到一个 IP 地址。在分布式系统中，您可能想跟踪哪些服务器或服务在运行，并通过名称查看其状态。ZooKeeper 暴露了一个简单的接口来完成此工作。也可以将名称服务扩展到组成员服务，这样就可以获得与正在查找其名称的实体有关联的组的信息。

**锁定**
为了允许在分布式系统中对共享资源进行有序的访问，可能需要实现分布式互斥（distributed mutexes）。ZooKeeper 提供一种简单的方式来实现它们。

**同步**
与互斥同时出现的是同步访问共享资源的需求。无论是实现一个生产者-消费者队列，还是实现一个障碍，ZooKeeper 都提供一个简单的接口来实现该操作。您可以在 Apache ZooKeeper 维基上查看示例，了解如何做到这一点（参阅 参考资料）。

**配置管理**
您可以使用 ZooKeeper 集中存储和管理分布式系统的配置。这意味着，所有新加入的节点都将在加入系统后就可以立即使用来自 ZooKeeper 的最新集中式配置。这还允许您通过其中一个 ZooKeeper 客户端更改集中式配置，集中地更改分布式系统的状态。

**集群管理**
分布式系统可能必须处理节点停机的问题，您可能想实现一个自动故障转移策略。ZooKeeper 通过`领导者选举`对此提供现成的支持。
如有多台 Server 组成一个服务集群，那么必须要一个“总管(Zookeeper)”知道当前集群中每台机器的服务状态，一旦有机器不能提供服务，**集群中其它集群必须知道**，从而做出调整重新分配服务策略。同样当增加集群的服务能力时，就会增加一台或多台 Server，同样也必须让“总管”知道。

### 架构
ZooKeeper 虽然是一个针对分布式系统的协调服务，但它本身也是一个分布式应用程序。ZooKeeper 遵循一个简单的`客户端-服务器`模型.
其中客户端 是使用服务的节点（即机器）
而服务器 是提供服务的节点。
ZooKeeper 服务器的集合形成了一个 `ZooKeeper 集合体（ensemble）`。
在任何给定的时间内，一个 ZooKeeper 客户端可连接到一个 ZooKeeper 服务器。每个 ZooKeeper 服务器都可以同时处理大量客户端连接。每个客户端定期发送 ping 到它所连接的 ZooKeeper 服务器，让服务器知道它处于活动和连接状态。被询问的 ZooKeeper 服务器通过 ping 确认进行响应，表示服务器也处于活动状态。如果客户端在指定时间内没有收到服务器的确认，那么客户端会连接到集合体中的另一台服务器，而且客户端会话会被透明地转移到新的 ZooKeeper 服务器。

### 文件系统
ZooKeeper 有一个类似于文件系统的数据模型，由 znodes 组成。可以将 znodes（ZooKeeper 数据节点）视为类似 UNIX 的传统系统中的文件，但它们可以有子节点。另一种方式是将它们视为目录，它们可以有与其相关的数据。每个这些目录都被称为一个 znode。图 2 显示的图代表与两个城市中的运动队相同的层次结构。
 
### 内存结构
znode 层次结构被存储在每个 ZooKeeper 服务器的内存中。这实现了对来自客户端的读取操作的可扩展的快速响应。每个 ZooKeeper 服务器还在磁盘上维护了一个事务日志，记录所有的写入请求。因为 ZooKeeper 服务器在返回一个成功的响应之前必须将事务同步到磁盘，所以事务日志也是 ZooKeeper 中对性能最重要的组成部分。可以存储在 znode 中的数据的默认最大大小为 1 MB。因此，即使 ZooKeeper 的层次结构看起来与文件系统相似，也不应该将它用作一个通用的文件系统。相反，应该只将它用作少量数据的存储机制，以便为分布式应用程序提供可靠性、可用性和协调。 

### 组成方式
法定数量是通过严格意义上的多数节点来表示的。在集合体中，可以包含一个节点，但它不是一个高可用和可靠的系统。如果在集合体中有两个节点，那么这两个节点都必须已经启动并让服务正常运行，因为两个节点中的一个并不是严格意义上的多数。如果在集合体中有三个节点，即使其中一个停机了，您仍然可以获得正常运行的服务（三个中的两个是严格意义上的多数）。出于这个原因，ZooKeeper 
 的集合体中通常包含奇数数量的节点，因为就容错而言，与三个节点相比，四个节点并不占优势，因为只要有两个节点停机，ZooKeeper 服务就会停止。在有五个节点的集群上，需要三个节点停机才会导致 ZooKeeper 服务停止运作。

现在，我们已经清楚地了解到，节点数量应该是奇数，让我们再来思考一下 ZooKeeper 集合体中需要有多少个节点。读取操作始终从连接到客户端的 ZooKeeper 服务器读取数据，所以它们的性能不会随着集合体中的服务器数量额变化而变化。但是，仅在写入法定数量的节点时，写入操作才是成功的。这意味着，随着在集合体中的节点数量的增加，写入性能会下降，因为必须将写入内容写入到更多的服务器中，并在更多服务器之间进行协调。

ZooKeeper 的美妙之处在于，想运行多少服务器完全由您自己决定。如果想运行一台服务器，从 ZooKeeper 的角度来看是没问题的；只是您的系统不再是高度可靠或高度可用的。三个节点的 ZooKeeper 集合体支持在一个节点故障的情况下不丢失服务，这对于大多数用户而言，这可能是没问题的，也可以说是最常见的部署拓扑。不过，为了安全起见，可以在您的集合体中使用五个节点。五个节点的集合体让您可以拿出一台服务器进行维护或滚动升级，并能够在不中断服务的情况下承受第二台服务器的意外故障。

因此，在 ZooKeeper 集合体中，三、五或七是最典型的节点数量。请记住，ZooKeeper 集合体的大小与分布式系统中的节点大小没有什么关系。分布式系统中的节点将是 ZooKeeper 集合体的客户端，每个 ZooKeeper 服务器都能够以可扩展的方式处理大量客户端。例如，HBase（Hadoop 上的分布式数据库）依赖​​于 ZooKeeper 实现区域服务器的领导者选举和租赁管理。您可以利用一个相对较少（比如说，五个）节点的 ZooKeeper 集合体运行有 50 个节点的大型 HBase 集群。

### 保证
Zookeeper非常简单和高效。因为它的目标就是作为建设复杂服务的基础，比如同步。zookeeper提供了一套保证，他们包括：

- 顺序一致性 - 来自客户端的更新会按顺序应用。
- 原子性 - 更新成功或者失败，没有局部的结果产生。
- 唯一系统映像 - 客户端不管连接到哪个服务端都会看到同样的视图。
- 可靠性- 一旦一个更新被应用，它将从更新的时间开始一直保持到一个客户端重写更新。
- 时效性 - 系统中的客户端视图在特定的时间点保证是最新的。

### API
Zookeeper的设计目标的其中之一就是提供一个简单的程序接口。因此，它只支持这些操作：

- create - 在树形结构的位置中创建节点
-delete - 删除一个节点
exists - 测试节点在指定位置上是否存在
get data - 从节点上读取数据
set data - 往节点写入数据
get chilren - 检索节点的子节点列表
sync - 等待传输数据

### 实现

ZooKeeper Components 展示了Zookeeper service的高等级组建。除了请求处理器，组成Zookeeper服务的服务器都会复制它们自己组件的副本
ZooKeeper Components shows the high-level components of the ZooKeeper service. With the exception of the request processor, each of the servers that make up the ZooKeeper service replicates its own copy of each of the components.



## 搭建环境

### 如何使用镜像

#### 开始服务实例
```
$ docker run --name some-zookeeper --restart always -d zookeeper
```
This image includes EXPOSE 2181 2888 3888 (the zookeeper  客户端连接端口, follower相互连接端口, 选举端口 )1 
so standard container linking will make it automatically available to the linked containers. Since the Zookeeper "fails fast" it's better to always restart it.

#### 应用程序链接到Zookeeper中
```
$ docker run --name some-app --link some-zookeeper:zookeeper -d application-that-uses-zookeeper
```
Connect to Zookeeper from an application in another Docker container

#### 使用zookeeper 客户端命令 连接到Zookeeper
```
$ docker run -it --rm --link some-zookeeper:zookeeper zookeeper zkCli.sh -server zookeeper
```
Connect to Zookeeper from the Zookeeper command line client

#### 编辑compose文件
```
version: '2'
services:
    zoo1:
        image: zookeeper
        restart: always
        ports:
            - 2181:2181
        environment:
            ZOO_MY_ID: 1
            ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888

    zoo2:
        image: zookeeper
        restart: always
        ports:
            - 2182:2181
        environment:
            ZOO_MY_ID: 2
            ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888

    zoo3:
        image: zookeeper
        restart: always
        ports:
            - 2183:2181
        environment:
            ZOO_MY_ID: 3
            ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888
```
This will start Zookeeper in replicated mode. Run docker-compose up and wait for it to initialize completely. Ports 2181-2183 will be exposed.

Please be aware that setting up multiple servers on a single machine will not create any redundancy. If something were to happen which caused the machine to die, all of the zookeeper servers would be offline. Full redundancy requires that each server have its own machine. It must be a completely separate physical server. Multiple virtual machines on the same physical host are still vulnerable to the complete failure of that host.

Consider using Docker Swarm when running Zookeeper in replicated mode.



### 配置

Zookeeper configuration is located in /conf. One way to change it is mounting your config file as a volume:

$ docker run --name some-zookeeper --restart always -d -v $(pwd)/zoo.cfg:/conf/zoo.cfg zookeeper

### Environment variables

如果zoo.cfg没有被提供， ZooKeeper默认推荐使用以下的常量 . They can be overridden using the following environment variables.

$ docker run -e "ZOO_INIT_LIMIT=10" --name some-zookeeper --restart always -d 31z4/zookeeper

#### ZOO_TICK_TIME

Defaults to 2000. ZooKeeper's tickTime

The length of a single tick,  基本的单位时间，毫秒为单位， 用来作心跳
It is used to regulate heartbeats, and timeouts. For example, the minimum session timeout will be two ticks

#### ZOO_INIT_LIMIT
Defaults to 5. ZooKeeper's initLimit

Amount of time, in ticks (see tickTime), follower链接到leader的最大值. 如果管理的follower数据很大，可以根据需要调整这个值.

#### ZOO_SYNC_LIMIT
Defaults to 2. ZooKeeper's syncLimit

Amount of time, in ticks (see tickTime), to allow followers to sync with ZooKeeper. If followers fall too far behind a leader, they will be dropped.

### 主从模式

#### ZOO_MY_ID

集合体中ID必须唯一，并且在1-255的范围内。
需要注意的是：如果你的容器启动的时候/data文件夹已经有myid的文件，这个配置将不会生效

The id must be unique within the ensemble and should have a value between 1 and 255. Do note that this variable will not have any effect if you start the container with a /data directory that already contains the myid file.

#### ZOO_SERVERS

这个变量允许你详细的列出zookeeper集合体中的机器.
每一个条目的格式如下：server.id=host:port:port，每个条目用空格分开
需要注意的是：如果你的容器启动的时候/data文件夹已经有myid的文件，这个配置将不会生效

This variable allows you to specify a list of machines of the Zookeeper ensemble. 
Each entry has the form of server.id=host:port:port. Entries are separated with space. 
Do note that this variable will not have any effect if you start the container with a /conf directory that already contains the zoo.cfg file.

### 储存数据

镜像使用volumes 挂载/data 和 /datalog 来配置，分别用来储存内存数据库的快照和更新数据库的事务日志。
This image is configured with volumes at /data and /datalog 
to hold the Zookeeper in-memory database snapshots and the transaction log of updates to the database, respectively.

对于事务日志要小心对待，一个专门储存事务日志的设备是推荐的做法。
Be careful where you put the transaction log. A dedicated transaction log device is key to consistent good performance. Putting the log on a busy device will adversely affect performance.

## 实践

### 启动

通过docker-compose启动镜像，服务器是默认打开的，并且设置了相应的端口。

手动启动服务器
```
bin/zkServer.sh start
or
sh /zookeeper-3.4.9/bin/zkServer.sh
```

手动从其中一台正在运行 ZooKeeper 服务器的机器上启动一个 CLI 客户端
```
sh /zookeeper-3.4.9/bin/zkCli.sh   -server 127.0.0.1:2181
or
bin/zkCli.sh -server 127.0.0.1:2181
```

### 命令行操作

- 查看目录
```
[zk: 127.0.0.1:2181(CONNECTED) 2] ls /
[zhida, zookeeper]
```

- 获取目录信息
```
[zk: 127.0.0.1:2181(CONNECTED) 4] get /zhida
test2
cZxid = 0x200000002
ctime = Tue Mar 21 10:28:28 GMT 2017
mZxid = 0x200000003
mtime = Tue Mar 21 10:31:29 GMT 2017
pZxid = 0x200000002
cversion = 0
dataVersion = 1
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 5
numChildren = 0
```

- 创建 create

```
create /zk_test my_data
```


- 删除 rmr

## 参考链接
[ZooKeeper 基础知识、部署和应用程序](https://www.ibm.com/developerworks/cn/data/library/bd-zookeeper/)
[zookeeper docker](https://hub.docker.com/_/zookeeper/)
[Zookeeper - Quick Guide](https://www.tutorialspoint.com/zookeeper/zookeeper_quick_guide.htm)
[分布式服务框架 Zookeeper -- 管理分布式环境中的数据 场景介绍](https://www.ibm.com/developerworks/cn/opensource/os-cn-zookeeper/)
[hadoop介绍](https://zookeeper.apache.org/doc/r3.3.3/zookeeperStarted.html)
