# Ribbon 基础入门


## 介绍
ribbon 是一个客户端负载均衡器，可以简单的理解成类似于 nginx的负载均衡模块的功能。

Ribbon is a client side load balancer which gives you a lot of control over the behaviour of HTTP and TCP clients. Feign already uses Ribbon, so if you are using @FeignClient then this section also applies.

## 使用方法

##### application.yml

```
ribbon: 
  eureka:
    enabled: true
  MaxAutoRetries: 0
  MaxAutoRetriesNextServer: 0
```

`ps:`有一些属性是在feign中使用的 ， 在配置文件中配置不生效； springboot中的feign集成了ribbon

##### pom.xml 

因为是在feign中集成的 ，所以参考feign的依赖

##### Application.java 

```

@RibbonClient(name = "yea-ribbon", configuration = YeaRibbonConfiguration.class)
public class Application {

	public static void main(String[] args) {feign
		SpringApplication.run(Application.class, args);
	}

}

```

##### YeaRibbonConfiguration.java 

```
public class YeaRibbonConfiguration {
	
	@Autowired
	IClientConfig ribbonClientConfig;

	@Bean
	public IPing ribbonPing(IClientConfig config) {
		return new PingUrl();
	}

	@Bean
	public IRule ribbonRule(IClientConfig config) {
		return new AvailabilityFilteringRule();
	}
}

```

## 其他知识点

### 自定义 Ribbon client

可以使用 `<client>.ribbon.*` 外部配置文件进行自定义, 和使用 原生的Netflix APIs 没有区别。

Spring Clound 可以让你完全控制 Ribbon client , 通过使用 @Ribbon Client来声明额外的配置。

```
@Configuration
@RibbonClient(name = "foo", configuration = FooConfiguration.class)
public class TestConfiguration {
}
```

```
@Configuration
public class FooConfiguration {
    @Bean
    public IPing ribbonPing(IClientConfig config) {
        return new PingUrl();
    }
}
```

`Note:`同样的 ，不能被Compose sacn 扫描到，不然就变成全局了，或者不要 @Configuration

##### Spring Cloud Netflix provides the following beans by default for ribbon (BeanType beanName: ClassName):

- `IClientConfig1 ribbonClientConfig: DefaultClientConfigImpl
- `IRule` ribbonRule: ZoneAvoidanceRule
- `IPing` ribbonPing: NoOpPing
- `ServerList<Server>` ribbonServerList: ConfigurationBasedServerList
- `ServerListFilter<Server>` ribbonServerListFilter: ZonePreferenceServerListFilter
- `ILoadBalancer` ribbonLoadBalancer: ZoneAwareLoadBalancer
- `ServerListUpdater` ribbonServerListUpdater: PollingServerListUpdater

##### 使用文件的属性值自定义Ribbon Client 

Starting with version 1.2.0, Spring Cloud Netflix now supports customizing Ribbon clients using properties to be compatible with the [Ribbon documentation](https://github.com/Netflix/ribbon/wiki/Working-with-load-balancers#components-of-load-balancer)

This allows you to change behavior at start up time in different environments.

The supported properties are listed below and should be prefixed by <clientName>.ribbon.:

```
NFLoadBalancerClassName: should implement ILoadBalancer

NFLoadBalancerRuleClassName: should implement IRule

NFLoadBalancerPingClassName: should implement IPing

NIWSServerListClassName: should implement ServerList

NIWSServerListFilterClassName should implement ServerListFilter
```

`NOTE:`
属性值的定义  > @RibbonClient(configuration=MyRibbonConfig.class) >  默认值

application.yml 

```
users:
  ribbon:
    NFLoadBalancerRuleClassName: com.netflix.loadbalancer.WeightedResponseTimeRule
```

### Using Ribbon with Eureka

当Eurela使用Ribbon的时候，ribbonServerList将会被 DiscoveryEnabledNIWSServerList覆盖，用来填充服务列表。
同样的使用NIWSDiscoveryPing 这个属性替代 IPing这个属性，如果服务是启动的将由 eureka去分配。

The ServerList that is installed by default is a DomainExtractingServerList and the purpose of this is to make physical metadata available to the load balancer without using AWS AMI metadata (which is what Netflix relies on). By default the server list will be constructed with "zone" information as provided in the instance metadata (so on the remote clients set eureka.instance.metadataMap.zone), and if that is missing it can use the domain name from the server hostname as a proxy for zone (if the flag approximateZoneFromHostname is set). Once the zone information is available it can be used in a ServerListFilter. By default it will be used to locate a server in the same zone as the client because the default is a ZonePreferenceServerListFilter. The zone of the client is determined the same way as the remote instances by default, i.e. via eureka.instance.metadataMap.zone.

### Example: How to Use Ribbon Without Eureka
Eureka is a convenient way to abstract the discovery of remote servers so you don’t have to hard code their URLs in clients, but if you prefer not to use it, Ribbon and Feign are still quite amenable. Suppose you have declared a @RibbonClient for "stores", and Eureka is not in use (and not even on the classpath). The Ribbon client defaults to a configured server list, and you can supply the configuration like this

##### application.yml

```
stores:
  ribbon:
    listOfServers: example.com,google.com
Example: Disable Eureka use in Ribbon
```

Setting the property ribbon.eureka.enabled = false will explicitly disable the use of Eureka in Ribbon.

##### application.yml

```
ribbon:
  eureka:
   enabled: false
```

### Using the Ribbon API Directly
You can also use the LoadBalancerClient directly. Example:

```
public class MyClass {
    @Autowired
    private LoadBalancerClient loadBalancer;

    public void doStuff() {
        ServiceInstance instance = loadBalancer.choose("stores");
        URI storesUri = URI.create(String.format("http://%s:%s", instance.getHost(), instance.getPort()));
        // ... do something with the URI
    }
}
```

### Caching of Ribbon Configuration
Each Ribbon named client has a corresponding child Application Context that Spring Cloud maintains, this application context is lazily loaded up on the first request to the named client. This lazy loading behavior can be changed to instead eagerly load up these child Application contexts at startup by specifying the names of the Ribbon clients.

```
application.yml
ribbon:
  eager-load:
    enabled: true
    clients: client1, client2, client3
```


## 参考网站
[Ribbon documentation](https://github.com/Netflix/ribbon/wiki/Working-with-load-balancers#components-of-load-balancer)













