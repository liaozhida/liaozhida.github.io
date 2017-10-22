---
layout:     post
title:      "[转]spring cloud eureka 参数配置"
date:       2016-05-22 12:00:00
author:     "zhida.liao"
header-img: "img/post-bg-2015.jpg"
tags:
    - eureka
    - 微服务 & 分布式 & 架构
---

[转]spring cloud eureka 参数配置



#### eureka.client.registry-fetch-interval-seconds

表示eureka client间隔多久去拉取服务注册信息，默认为30秒，对于api-gateway，如果要迅速获取服务注册状态，可以缩小该值，比如5秒

eureka.instance.lease-expiration-duration-in-seconds

####  leaseExpirationDurationInSeconds

表示eureka server至上一次收到client的心跳之后，等待下一次心跳的超时时间，在这个时间内若没收到下一次心跳，则将移除该instance。

默认为90秒
如果该值太大，则很可能将流量转发过去的时候，该instance已经不存活了。
如果该值设置太小了，则instance则很可能因为临时的网络抖动而被摘除掉。
该值至少应该大于leaseRenewalIntervalInSeconds

#### eureka.instance.lease-renewal-interval-in-seconds

leaseRenewalIntervalInSeconds，表示eureka client发送心跳给server端的频率。如果在leaseExpirationDurationInSeconds后，server端没有收到client的心跳，则将摘除该instance。除此之外，如果该instance实现了HealthCheckCallback，并决定让自己unavailable的话，则该instance也不会接收到流量。

默认30秒

####  eureka.server.enable-self-preservation

是否开启自我保护模式，默认为true。

默认情况下，如果Eureka Server在一定时间内没有接收到某个微服务实例的心跳，Eureka Server将会注销该实例（默认90秒）。但是当网络分区故障发生时，微服务与Eureka Server之间无法正常通信，以上行为可能变得非常危险了——因为微服务本身其实是健康的，此时本不应该注销这个微服务。

Eureka通过“自我保护模式”来解决这个问题——当Eureka Server节点在短时间内丢失过多客户端时（可能发生了网络分区故障），那么这个节点就会进入自我保护模式。一旦进入该模式，Eureka Server就会保护服务注册表中的信息，不再删除服务注册表中的数据（也就是不会注销任何微服务）。当网络故障恢复后，该Eureka Server节点会自动退出自我保护模式。

综上，自我保护模式是一种应对网络异常的安全保护措施。它的架构哲学是宁可同时保留所有微服务（健康的微服务和不健康的微服务都会保留），也不盲目注销任何健康的微服务。使用自我保护模式，可以让Eureka集群更加的健壮、稳定。

####  eureka.server.eviction-interval-timer-in-ms

eureka server清理无效节点的时间间隔，默认60000毫秒，即60秒



####  测试环境参考配置

##### eureka server

```
eureka:
  server:
    enable-self-preservation: false           # 关闭自我保护模式（缺省为打开）
    eviction-interval-timer-in-ms: 5000       # 续期时间，即扫描失效服务的间隔时间（缺省为60*1000ms）
```

##### eureka client

```
eureka:
  instance:
    lease-renewal-interval-in-seconds: 5      # 心跳时间，即服务续约间隔时间（缺省为30s）
    lease-expiration-duration-in-seconds: 10  # 发呆时间，即服务续约到期时间（缺省为90s）
  client:
    healthcheck:
      enabled: true                           # 开启健康检查（依赖spring-boot-starter-actuator）
```

作者：scipio
链接：http://www.jianshu.com/p/e2bebfb0d075
來源：简书
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。


[spring cloud eureka 参数配置](http://www.jianshu.com/p/e2bebfb0d075)