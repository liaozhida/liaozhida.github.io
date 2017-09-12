---
layout:     post
title:      "微服务教程-使用Spring Cloud&Eureka服务发现和注册"
subtitle:   "Microservice Registration and Discovery with Spring Cloud and Netflix's Eureka"
date:       2017-05-22 12:00:00
author:     "zhida.liao"
header-img: "img/post-bg-2015.jpg"
tags:
    - eureka
    - 微服务 & 分布式 & 架构
---


微服务教程-使用Spring Cloud & Eureka实现服务发现和注册 


## 概念介绍

微服务的架构不是用来构建一个庞大独立的服务的，他用来实现服务间的可靠以及高可用的服务交互

这篇文章主要是翻译外文，我们会着重关注 Spring Cloud  如何为你实现复杂的服务注册，例如Eureka 、 Consul 、 client-side load-balancing.

## 云通讯录

一个服务发现就像微服务架构的通讯录，每个服务会在注册器上注册自己并告诉注册器他的地址（域名、端口、节点），以及一些特定的元数据（为其他服务提供一些必要的信息），客户端会询问注册器一些信息，比如服务是否可用以及他的地址，以及这些服务的用途。你可能之前使用过这些集群概念的技术，类似于Cassandra, Memcached等等。将这些信息保存在服务注册器中是非常适合的。

服务注册器有很多理想的选项，Netflix构建了并且开源了他们的服务注册器Eureka。当然还有其他更流行的Consul，我们将会着重关注spring cloud和 Eureka的集成。


Spring Cloud project 主页是这样介绍的: “Spring Cloud 为开发者提供一些工具， 快速的在分布式应用中构建一些常用场景  (e.g. 配置管理、服务发现, 断路器circuit breakers, 智能路由, 微代理, control bus, one-time tokens, 全局锁,领导选举 ，分布式会话, 集群 state). 开发者使用 Spring Cloud developers 可以快速的实现这些模式来构建自己的服务和应用程序 ，在任何集群环境中都能完美运行，包括开发者自己的笔记本、元数据中心、管理平台

Spring Cloud 已经支持  Eureka and Consul, 我们着重讲解Eureka是因为使用springBoot的自动配置可以快速启动. Eureka is implemented on the JVM but Consul is implemented in Go.

## 安装 Eureka

运行一个Eureka服务注册器实例非常简单，只要在类加载路径中存在org.springframework.boot:spring-cloud-starter-eureka-server


```
package registry;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

@SpringBootApplication
@EnableEurekaServer
public class Application {

  public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
  }
}
```
src/main/resources/application.yml looks like this :

```
server:
  port: ${PORT:8761}

eureka:
  client:
    registerWithEureka: false
    fetchRegistry: false
    server:
      waitTimeInMsWhenSyncEmpty: 0
```

如果 Cloud Foundry’s 的VCAP_APPLICATION_PORT 的环境变量没有指定. 服务端口默认 8761 ，
剩下的配置表示：这个实例不注册在 Eureka中，因为它自己就是注册器。如果你再本地运行它，可以在浏览器中http://localhost:8761，监控这个注册器的状态。


## 发布 Eureka

Spring Cloud 使用Spring Boot auto-configuration可以快速运行Eureka. 发布 Eureka需要考虑事情. 1, 在生产环境中使用高可用配置. [The Spring Cloud Eureka sample](https://github.com/spring-cloud-samples/eureka) 将会演示如何发布高可用应用的一些配置


## Speak for Yourself

Spring Cloud-based 的服务有一个 spring.application.name 属性. 在 Eureka中区分每个服务, 当构建Spring Cloud-based 应用程序的时候这个属性和很多上下文有关联， 
在src/main/resources/bootstrap.(yml,properties)文件中定义, 相较于 src/main/resources/application.(yml,properties)会更早的使用这个值初始化. 
一个服务程序在类路径中使用了org.springframework.cloud:spring-cloud-starter-eureka依赖，BootStrap将会使用spring.application.name注册为一个发现服务实例。

src/main/resources/boostrap.yml 
```
spring:
  application:
    name: my-service
```

src/main/resources/application.yml可以改变默认的IP地址,Eureka 注册器中可能有很多个相同的ID，使用IP地址可以区分他们

```
eureka:
  client:
    serviceUrl:
      defaultZone: ${vcap.services.eureka-service.credentials.uri:http://127.0.0.1:8761}/eureka/

---
spring:
  profiles: cloud
eureka:
  instance:
    hostname: ${APPLICATION_DOMAIN}
    nonSecurePort: 80
```

在这个配置中，Spring Cloud Eureka 客户端知道如何去连接本地运行的Eureka实例。 如果 Cloud Foundry’s VCAP_SERVICES 这个环境变量没有配置或者无效的情况下。

--- 分割符下面的配置代表：应用程序使用cloud 环境文件运行
如果你使用了SPRING_PROFILES_ACTIVE变量，可以在 manifest.yml or, on Cloud Foundry Lattice, your Docker file.配置这个变量

在我的发布脚本中设置了APPLICATION_DOMAIN 环境变量，告诉服务外部的关联地址。
在Eureka监控界面下点击刷新，30秒后你会看到你的服务已经注册好了。

## 使用 Ribbon 实现客户端的负载均衡

Spring Cloud 中关联其他服务使用的是 spring.application.name . 当我们构建  Spring Cloud-based 的服务的时候，这个值可以在很多上下文中被用到

为的是让客户端基于一些上下文信息，去决定哪一个服务将会被连接使用， Spring Cloud 把client-side load-balancing用途的 Ribbon集成进来了。
看一下示例，直接使用 Eureka然后使用Ribbon.

```
package passport;

import org.apache.commons.lang.builder.ToStringBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.cloud.client.ServiceInstance;
import org.springframework.cloud.client.discovery.DiscoveryClient;
import org.springframework.cloud.netflix.eureka.EnableEurekaClient;
import org.springframework.cloud.netflix.feign.EnableFeignClients;
import org.springframework.cloud.netflix.feign.FeignClient;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@SpringBootApplication
@EnableEurekaClient
@EnableFeignClients
public class Application {

    public static void main(String[] args) {
        new SpringApplicationBuilder(Application.class)
                .web(false)
                .run(args);
    }
}

@Component
class DiscoveryClientExample implements CommandLineRunner {

    @Autowired
    private DiscoveryClient discoveryClient;

    @Override
    public void run(String... strings) throws Exception {
        discoveryClient.getInstances("photo-service").forEach((ServiceInstance s) -> {
            System.out.println(ToStringBuilder.reflectionToString(s));
        });
        discoveryClient.getInstances("bookmark-service").forEach((ServiceInstance s) -> {
            System.out.println(ToStringBuilder.reflectionToString(s));
        });
    }
}

@Component
class RestTemplateExample implements CommandLineRunner {

    @Autowired
    private RestTemplate restTemplate;

    @Override
    public void run(String... strings) throws Exception {
        // use the "smart" Eureka-aware RestTemplate
        ResponseEntity<List<Bookmark>> exchange =
                this.restTemplate.exchange(
                        "http://bookmark-service/{userId}/bookmarks",
                        HttpMethod.GET,
                        null,
                        new ParameterizedTypeReference<List<Bookmark>>() {
                        },
                        (Object) "mstine");

        exchange.getBody().forEach(System.out::println);
    }

}

@Component
class FeignExample implements CommandLineRunner {

    @Autowired
    private BookmarkClient bookmarkClient;

    @Override
    public void run(String... strings) throws Exception {
        this.bookmarkClient.getBookmarks("jlong").forEach(System.out::println);
    }
}

@FeignClient("bookmark-service")
interface BookmarkClient {

    @RequestMapping(method = RequestMethod.GET, value = "/{userId}/bookmarks")
    List<Bookmark> getBookmarks(@PathVariable("userId") String userId);
}

class Bookmark {
    private Long id;
    private String href, label, description, userId;

    @Override
    public String toString() {
        return "Bookmark{" +
                "id=" + id +
                ", href='" + href + '\'' +
                ", label='" + label + '\'' +
                ", description='" + description + '\'' +
                ", userId='" + userId + '\'' +
                '}';
    }

    public Bookmark() {
    }

    public Long getId() {
        return id;
    }

    public String getHref() {
        return href;
    }

    public String getLabel() {
        return label;
    }

    public String getDescription() {
        return description;
    }

    public String getUserId() {
        return userId;
    }
}
```


The DiscoveryClientExample 演示了使用 Spring Cloud common DiscoveryClient 来查询服务信息. 结果包含了每个服务的域名端口等信息.

The RestTemplateExample 演示了自动配置的 Ribbon-aware RestTemplate 实例.URI 使用了service ID, 而不是一个具体的域名.Eureka注册器会通过这ID找到域名然后给到Ribbon做负载均衡。

The FeignExample 演示如何使用  Spring Cloud Feign 组件. Feign 是 Netflix一个非常便利的项目，可以在接口上使用注释去声明一个 REST API client

可以参考官网的[example-github](https://github.com/OpenFeign/feign)了解feign;

 
## Review

- Spring Cloud supports 支持 Eureka and Consul service registries (and perhaps more!)
- The DiscoveryClient API 可以用来查询 Eureka 里面的  service ID信息.
- Ribbon 是一个 client-side load balancer
- The RestTemplate 可以在URI中使用 service IDs 来代替 hostnames ，以及可以使用 Ribbon 来选择 service.
- The Netflix Spring Cloud Feign 组件可以快速的创建一个，灵活的、Eureka-aware 的 REST clients  ；

## 后续

- Consul有很多特性是 Eureka不具备的，可以去了解一下
- Round-robin load-balancing 是一种选项，还有其他的策略可以使用。
- 除了服务发现，我们还可以去关注 single-sign on and security, distributed locks and leadership election, reliability patterns like the circuit breaker, and much more.



## 参考源码

[https://github.com/joshlong/service-registration-and-discovery](https://github.com/joshlong/service-registration-and-discovery)

[Microservice Registration and Discovery with Spring Cloud and Netflix's Eureka](https://spring.io/blog/2015/01/20/microservice-registration-and-discovery-with-spring-cloud-and-netflix-s-eureka)