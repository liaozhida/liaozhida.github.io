---
layout:     post
title:      "zookeeper简介及Java集成"
date:       2017-05-22 12:00:00
author:     "zhida"
header-img: "img/post-bg-js-module.jpg"
tags:
    - zookeeper
    - 微服务 & 分布式 & 架构
---

## 重要知识点

- 所有结构都是在内存中
- 观察者模式，基于数据的变动做出响应
- 共享锁 ： 需要获得锁的 Server 创建一个 EPHEMERAL_SEQUENTIAL 目录节点，然后调用 getChildren方法获取当前的目录节点列表中最小的目录节点是不是就是自己创建的目录节点，如果正是自己创建的，那么它就获得了这个锁，如果不是那么它就调用 exists(String path, boolean watch) 方法并监控 Zookeeper 上目录节点列表的变化，一直到自己创建的节点是列表中最小编号的目录节点，从而获得锁，释放锁很简单，只要删除前面它自己所创建的目录节点就行了。

## 了解zookeeper 目录结构
 
```
[zk: 127.0.0.1:2181(CONNECTED) 18] ls /
[services, zookeeper, config, configuration]

```

#### services

代表注册的服务

```
[zk: 127.0.0.1:2181(CONNECTED) 21] ls /services
[serverB, clientA, serverA]
```

当clientA启动的时候
```
[zk: 127.0.0.1:2181(CONNECTED) 29] ls /services/clientA
[2a280d84-4d65-46b6-aad4-4583af6dd809]
```

获取clientA的元数据
```
[zk: 127.0.0.1:2181(CONNECTED) 31] get /services/clientA/2a280d84-4d65-46b6-aad4-4583af6dd809

{"name":"clientA","id":"2a280d84-4d65-46b6-aad4-4583af6dd809","address":"172.20.3.42","port":8080,"sslPort":null,"payload":{"@class":"org.springframework.cloud.zookeeper.discovery.ZookeeperInstance","id":"clientA:8080","name":"clientA","metadata":{}},"registrationTimeUTC":1500977838186,"serviceType":"DYNAMIC","uriSpec":{"parts":[{"value":"scheme","variable":true},{"value":"://","variable":false},{"value":"address","variable":true},{"value":":","variable":false},{"value":"port","variable":true}]}}
cZxid = 0x5d00000075
ctime = Tue Jul 25 10:17:18 GMT 2017
mZxid = 0x5d00000075
mtime = Tue Jul 25 10:17:18 GMT 2017
pZxid = 0x5d00000075
cversion = 0
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x15d727a12c2001c
dataLength = 501
numChildren = 0
```

#### config

查看什么项目有配置信息
```
[zk: 127.0.0.1:2181(CONNECTED) 35] ls /config
[clientA]
```

查看clientA项目的配置信息
```
[zk: 127.0.0.1:2181(CONNECTED) 36] ls /config/clientA
[name]
```

查看具体信息
```
[zk: 127.0.0.1:2181(CONNECTED) 38] get /config/clientA/name
Mark
cZxid = 0x1400000231
ctime = Thu Apr 13 08:50:03 GMT 2017
mZxid = 0x1400000231
mtime = Thu Apr 13 08:50:03 GMT 2017
pZxid = 0x1400000231
cversion = 0
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 4
numChildren = 0
```

#### configuration

和config发挥的作用一致

## 与Java集成

clientA 的配置文件如下, 和serverA有关联关系，代表能够监控他serverA的事件

**application.yml:**
```
server:
  port: 8080

endpoints:
  restart:
    enabled: true
  shutdown:
    enabled: true
  health:
    sensitive: false

logging.level:
  org.apache.zookeeper.ClientCnxn: WARN

management:
  security:
    enabled: false

spring.cloud.zookeeper:
  dependencies:
    serverA:
        path: /serverA
        loadBalancerType: ROUND_ROBIN
        contentTypeTemplate: application/vnd.newsletter.$version+json
        version: v1
        required: false


```

**监控代码如下， 能够监控到事件然后输出控制台**
```
@Service
public class WatcherSample implements DependencyWatcherListener,BeanFactoryPostProcessor {

	@Override
	public void stateChanged(String arg0, DependencyState arg1) {

		System.out.println("~~~~~~~~~~~~> " + arg0 + "--" + arg1);
	}

	@Override
	public void postProcessBeanFactory(ConfigurableListableBeanFactory arg0) throws BeansException {
		
		System.out.println("~~~~~~>>> WatcherSample is init");
	}

}

```

**获取属性值**

```
@Component
public class HelloWorldService {

  @Value("${name}")
  private String name;

  public String getHelloMessage() {
    return "Hello " + this.name;
  }

}  
```

[sample-spring-boot-zookeeper-embedded](https://github.com/alexbt/sample-spring-boot-zookeeper-embedded)