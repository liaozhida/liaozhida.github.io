# zookeeper integer

## 特性
Spring Cloud Zookeeper 只完成这几个功能，不涵盖所有的zookeeper特性

- 发现服务：实例可以注册到zookeeper中，使用Spring-managed beans去发现实例
- 支持 Ribbon, 通过 Spring Cloud Netflix实现客户端的负载均衡
- 支持 Zuul, 通过 Spring Cloud Netflix实现动态路由和过滤
- 分布式配置: using Zookeeper as a data store




Supports Zuul, a dynamic router and filter via Spring Cloud Netflix
Distributed Configuration: using Zookeeper as a data store

## info

### 发现服务 && 统一命名服务（Name Service）

#### pom.xml

```
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>


	<artifactId>spring-cloud-zookeeper-sample</artifactId>
	<packaging>jar</packaging>
	<name>Spring Cloud Zookeeper Sample</name>
	<description>Spring Cloud Zookeeper Sample</description>

	<parent>
		<groupId>org.springframework.cloud</groupId>
		<artifactId>spring-cloud-zookeeper</artifactId>
		<version>1.0.4.RELEASE</version>
		<relativePath>..</relativePath>
	</parent>

	<yml>
		<sonar.skip>true</sonar.skip>
	</yml>

	<dependencies>
		<dependency>
			<groupId>org.springframework.cloud</groupId>
			<artifactId>spring-cloud-starter-zookeeper-all</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-web</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-actuator</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.cloud</groupId>
			<artifactId>spring-cloud-starter-feign</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.apache.curator</groupId>
			<artifactId>curator-test</artifactId>
			<scope>test</scope>
		</dependency>
	</dependencies>

	<build>
		<plugins>
			<plugin>
				<groupId>org.springframework.boot</groupId>
				<artifactId>spring-boot-maven-plugin</artifactId>
			</plugin>
			<plugin>
				<!--skip deploy -->
				<artifactId>maven-deploy-plugin</artifactId>
				<configuration>
					<skip>true</skip>
				</configuration>
			</plugin>
		</plugins>
		
		 
	</build>
</project>

```

#### 服务端

**Code:**
```
@SpringBootApplication  
@EnableDiscoveryClient  
public class AppServer {  
    public static void main(String[] args) {  
        SpringApplication.run(AppServer.class, args);  
    }  
}  
```

**Server**

application.yml
```
server:
  port: 6080

logging.level:
  org.apache.zookeeper.ClientCnxn: WARN
```

bootstrap.yml
```
spring:
  application:
    name: serverA
```


**Server**

application.yml
```
server:
  port: 6081

logging.level:
  org.apache.zookeeper.ClientCnxn: WARN
```

bootstrap.yml
```
spring:
  application:
    name: serverA
```

**Server**

application.yml
```
server:
  port: 6082

logging.level:
  org.apache.zookeeper.ClientCnxn: WARN
```

bootstrap.yml
```
spring:
  application:
    name: serverB
```

启动3个server程序；
进入zookeeper 
```
[zk: 127.0.0.1:2181(CONNECTED) 52] ls /services
[serverB, serverA]

[zk: 127.0.0.1:2181(CONNECTED) 53] ls /services/serverA
[20f54509-e4cd-4bb7-9ed2-ca84940b9eff, f9c6f73a-64f5-4208-b68e-281216909c3c]
```

#### 客户端

**Code**
```
@Configuration
@EnableAutoConfiguration
@EnableDiscoveryClient
@RestController
@EnableFeignClients
public class SampleZookeeperApplication {

	@Value("${spring.application.name}")
	private String appName;

	@Autowired
	private LoadBalancerClient loadBalancer;

	@Autowired
	private DiscoveryClient discovery;

	@Autowired
	private Environment env;

	@Autowired
	private AppClient appClient;

	@Autowired
	RestTemplate rest;

	public static void main(String[] args) {
		SpringApplication.run(SampleZookeeperApplication.class, args);
	}

	@RequestMapping("/choose/{name}")
	public ServiceInstance lb(@PathVariable("name") String name) {
		
		ServiceInstance si =  this.loadBalancer.choose(name);
		
		System.out.println(si.getServiceId()+"--"+si.getUri());
		
		return si;
				
	}

	@RequestMapping("/myenv")
	public String env(@RequestParam("prop") String prop) {
		return new RelaxedPropertyResolver(this.env).getProperty(prop, "Not Found");
	}

	@RequestMapping("/all")
	public String all() {

		List<ServiceInstance> list = discovery.getInstances("application");
		System.out.println(list + "-->" + list.size());

		if (list != null && list.size() > 0) {

			System.out.println(list.get(0).getUri().toString());
			return list.get(0).getUri().toString();
		}

		System.out.println(discovery.getServices());

		return "all";

	}

	@FeignClient("serverA")
	interface AppClient {
		@RequestMapping(path = "/serverA", method = RequestMethod.GET)
		String hi();
	}

	public String rt() {
		return this.rest.getForObject("http://" + this.appName + "/hi", String.class);
	}

	@Bean
	@LoadBalanced
	RestTemplate loadBalancedRestTemplate() {
		return new RestTemplate();
	}

	@RequestMapping("/serverA")
	public String hi() {

		return "Hello World! from " + this.discovery.getLocalServiceInstance();
	}

}

```

application.yml
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

# 这块不定义 就使用默认的轮询方式
spring.cloud.zookeeper:
  dependencies:
    serverA:
        path: /serverA
        loadBalancerType: ROUND_ROBIN
        contentTypeTemplate: application/vnd.newsletter.$version+json
        version: v1
        required: true	#是否必须要依赖这个服务  没有这个服务spring将无法启动

spring:
  cloud:
    zookeeper:
      discovery:
        register: false

```

bootstrap.yml
```
spring:
  cloud:
    zookeeper:
      connect-string: localhost:2181
```

*使用：*访问http://127.0.0.1:8080/ 系统会返回一个可用的serverA服务，默认使用轮询的方法返回一个服务

### 监听事件

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

启动两个ServerA程序，然后随之结束
```
2017-04-12 17:13:45.197  INFO 13531 --- [-ServiceCache-0] .w.DependencyStateChangeListenerRegistry : Service cache state change for '/serverA' instances, current service state: CONNECTED
~~~~~~~~~~~~> /serverA--CONNECTED
2017-04-12 17:13:49.323  INFO 13531 --- [-ServiceCache-0] .w.DependencyStateChangeListenerRegistry : Service cache state change for '/serverA' instances, current service state: CONNECTED
~~~~~~~~~~~~> /serverA--CONNECTED
2017-04-12 17:15:49.722  INFO 13531 --- [-ServiceCache-0] .w.DependencyStateChangeListenerRegistry : Service cache state change for '/serverA' instances, current service state: CONNECTED
~~~~~~~~~~~~> /serverA--CONNECTED
2017-04-12 17:16:00.776  INFO 13531 --- [-ServiceCache-0] .w.DependencyStateChangeListenerRegistry : Service cache state change for '/serverA' instances, current service state: DISCONNECTED
~~~~~~~~~~~~> /serverA--DISCONNECTED

```

Note：如果zookeeper服务没有添加这个属性，spring.cloud.zookeeper:dependencies:  将不会被监听到

### 分布式配置文件

**pom.xml**需要引入依赖包
```
org.springframework.cloud:spring-cloud-starter-zookeeper-config
```

**bootstrap.yml**
```
spring:
  cloud:
    zookeeper:
      config:
        enabled: true
        root: configuration
        defaultContext: apps
        profileSeparator: '::'
```

enabled setting this value to "false" disables Zookeeper Config

root sets the base namespace for configuration values

defaultContext sets the name used by all applications

profileSeparator sets the value of the separator used to separate the profile name in property sources with profiles

#### 实战部分

**curl http://localhost:8080/env | python -mjson.tool**, 可以查看所有的环境变量，善用这个网址
spring clond zookeeper 可以将所有的节点信息，放进spring 的环境变量中

截取部分
```
"zookeeper:configuration/apps": {},
"zookeeper:configuration/clientA": {
    "name": "Mark"
}
```

写入配置
```
bin/zkCli.sh -server 127.0.0.1:2181
create /configuration ""
create /configuration/clientA ""
create /configuration/clientA/name Mark1
```

代码读取
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

### 集群管理
zookeeper的自身特性  



## QA

- Consider defining a bean of type 'org.springframework.web.client.RestTemplate' in your configuration.
```
@LoadBalanced
@Bean
public RestTemplate restTemplate() {
	return new RestTemplate();
}
```




[Spring Cloud Zookeeper](http://cloud.spring.io/spring-cloud-zookeeper/spring-cloud-zookeeper.html)