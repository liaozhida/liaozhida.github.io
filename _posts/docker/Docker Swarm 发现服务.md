Docker Swarm 发现服务

### 服务发现方案:键值对储存

- Docker hub
- Consul
- Etcd
- ZooKeeper


#### 客户端创建

节点 加入swarm中会触发发现事件，当你使用脚本添加大量的节点，或者从网络分区中恢复节点连接，因为太集中的触发将会导致发现失败，可以使用 **--delay**选项指定延时限制，Swarm join 会在你指定的时间汇总添加随机的延时去减轻发现服务的压力

Etcd:
```
 swarm join --advertise=<node_ip:2375> etcd://<etcd_addr1>,<etcd_addr2>/<optional path prefix>
```

Consul:
```
 swarm join --advertise=<node_ip:2375> consul://<consul_addr>/<optional path prefix>
```

ZooKeeper:
```
 swarm join --advertise=<node_ip:2375> zk://<zookeeper_addr1>,<zookeeper_addr2>/<optional path prefix>
```

#### 启动swarm manager

Etcd:
```
 swarm manage -H tcp://<swarm_ip:swarm_port> etcd://<etcd_addr1>,<etcd_addr2>/<optional path prefix>
```

Consul:
```
 swarm manage -H tcp://<swarm_ip:swarm_port> consul://<consul_addr>/<optional path prefix>
```

ZooKeeper:
```
 swarm manage -H tcp://<swarm_ip:swarm_port> zk://<zookeeper_addr1>,<zookeeper_addr2>/<optional path prefix>
```

#### 使用docker命令测试

```
 docker -H tcp://<swarm_ip:swarm_port> info
 docker -H tcp://<swarm_ip:swarm_port> run ...
 docker -H tcp://<swarm_ip:swarm_port> ps
 docker -H tcp://<swarm_ip:swarm_port> logs ...
```

#### 列出集群中的节点

Etcd:
```
 swarm list etcd://<etcd_addr1>,<etcd_addr2>/<optional path prefix> <node_ip:2375>
```

Consul:
```
 swarm list consul://<consul_addr>/<optional path prefix> <node_ip:2375>
```

ZooKeeper:
```
 swarm list zk://<zookeeper_addr1>,<zookeeper_addr2>/<optional path prefix> <node_ip:2375>
```

#### 分布式发现服务的TSL连接方式

只能使用Consul and Etcd.  Consul示例:
```
swarm join \
    --advertise=<node_ip:2375> \
    --discovery-opt kv.cacertfile=/path/to/mycacert.pem \
    --discovery-opt kv.certfile=/path/to/mycert.pem \
    --discovery-opt kv.keyfile=/path/to/mykey.pem \
    consul://<consul_addr>/<optional path prefix>
```

### 使用静态文件或者指定节点列表

> 这种方式不适用于 复制的swarm manager，当你要使用复制特性，请使用发现服务。

可以使用文件记录节点，但是这个文件必须放在能被manager访问的地方，或者在启动的时候指定文件路径
可以指定一个IP地址范围，类似于：
```
  $ echo "10.0.0.[11:100]:2375"   >> /tmp/my_cluster
  $ echo "10.0.1.[15:20]:2375"    >> /tmp/my_cluster
  $ echo "192.168.1.2:[2:20]375"  >> /tmp/my_cluster

  swarm manage -H tcp://<swarm_ip:swarm_port> file:///tmp/my_cluster

  $ swarm list file:///tmp/my_cluster
	<node_ip1:2375>
	<node_ip2:2375>
	<node_ip3:2375>
```
或者
```
swarm manage -H <swarm_ip:swarm_port> "nodes://10.0.0.[10:200]:2375,10.0.1.[2:250]:2375"
swarm manage -H <swarm_ip:swarm_port> nodes://<node_ip1:2375>,<node_ip2:2375>
or
swarm manage -H <swarm_ip:swarm_port> <node_ip1:2375>,<node_ip2:2375>

```

使用Docker hub做发现服务，参考之前的文章 《docker swarm入门笔记》


### 参考网站
[Docker Swarm Discovery](https://docs.docker.com/swarm/discovery/)

