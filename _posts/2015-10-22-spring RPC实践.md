## spring RPC 实践 - http invoker

Spring支持多种不同的RPC模型，包括RMI、Hessian/Burlap以及Spring自带的Http Invoker。下面我将简单介绍一下它们之间的异同点：

- RMI：不考虑网络限制时使用（PS：因为RMI使用任意端口来交互，有时无法穿越防火墙）
- Hessian/Burlap：考虑网络限制时，通过HTTP访问/发布基于Java的服务。Hessian是基于二进制的远程调用技术；而Burlap是基于XML的远程调用技术
- Spring的HttpInvoker：跟Hessian/Burlap实现的调用技术类似，但是不同的是Hessian/Burlap使用了私有的对象序列化机制，而Spring的Http Invoker则使用的是Java的序列化机制
- WebService : 

但是，不管选择哪种远程调用模型我们都会发现Spring提供了风格一致的支持。这意味着一旦理解了如何在Spring中配置和使用其中一种模型。那么当我们想要使用另外一种模型的话，将会变得非常容易

在所有的模型中，服务都作为Spring所管理的bean配置到我们的应用中。这是通过一个代理工厂bean实现的，这个bean能够把远程服务像本地对象一样装配到其他bean的属性中去。客户端向代理发起调用，就像代理提供了这些服务一样。代理代表客户端与远程服务进行通信，由它负责处理连接的细节并向远程服务发起调用。最后代理再返回远程服务执行完成之后的结果，至此整个调用过程完成

无论我们开发的是使用远程服务的代码，还是实现这些服务的代码，或者两者兼而有之。在Spring中，使用远程服务纯粹是一个配置问题。我们不需要编写任何Java代码就可以支持远程调用。我们的服务bean也不需要关心它们是否参与了一个RPC(PS：任何传递给远程调用的bean或从远程调用返回的bean可能需要实现java.io.Serializable 接口）


### 服务端项目


初始化项目，然后导入eclipse中

```
spring init -dredis,web rpc-demo
```

定义service接口和实现类

```
public interface ITicketService {
	
	public Message<String> test();

}


@Service
public class TicketService implements ITicketService{

	@Override
	public Message<String> test() {
		
		int counter = Ticket.find.where().findRowCount();		
		return new Message<String>("hello world" + counter);

	}
}
```

使用@Bean发布远程服务
```
@SpringBootApplication
public class Application {
	
	public static void main(String[] args) {
		SpringApplication.run(Application.class, args);
	}

	/**
	 * 发布产品类
	 * 
	 * @param myServiceImpl
	 * @return
	 */
	@Bean(name = "/ticket.service")
	public HttpInvokerServiceExporter myHttpInvokerServiceExporter(ITicketService service) {
	    HttpInvokerServiceExporter exporter = new HttpInvokerServiceExporter();
	    exporter.setServiceInterface(ITicketService.class);
	    exporter.setService(service);
	    return exporter;
	}
	
	/**
	 * 发布产品的缓存类
	 * 
	 * @param productRedisServiceImp
	 * @return
	 */
	@Bean(name = "/ticket.redisService")
	public HttpInvokerServiceExporter myHttpInvokerRedisServiceExporter(ITicketRedisService service) {
	    HttpInvokerServiceExporter exporter = new HttpInvokerServiceExporter();
	    exporter.setServiceInterface(ITicketRedisService.class);
	    exporter.setService(service);
	    return exporter;
	}
}

```

#### 多环境Profie

- 使用常规的maven环境配置
- 使用 application-{env} , 可以查看配置属性 附录

#### 打包

- 使用常规的maven打包

#### 异常处理


#### 解决**超时**重复操作的问题

- 不使用第三方架构的处理方式： 客户端调用时生成一个随机字符串key，服务端接收key之后保存在内存中，以乐观锁的形式避免多次重复调用。


#### 日志

在类目录下增加logback.xml ,增加相应的jar包即可

```
<!-- 日志记录 -->
<dependency>
	<groupId>ch.qos.logback</groupId>
	<artifactId>logback-classic</artifactId>
	<version>${logback.version}</version>
</dependency>
<dependency>
	<groupId>org.logback-extensions</groupId>
	<artifactId>logback-ext-spring</artifactId>
	<version>0.1.2</version>
</dependency>
<dependency>
	<groupId>net.logstash.logback</groupId>
	<artifactId>logstash-logback-encoder</artifactId>
	<version>4.3</version>
</dependency>
<dependency>
	<groupId>org.slf4j</groupId>
	<artifactId>jcl-over-slf4j</artifactId>
	<version>1.7.12</version>
</dependency>
<dependency>
	<groupId>org.slf4j</groupId>
	<artifactId>log4j-over-slf4j</artifactId>
	<version>1.7.12</version>
</dependency>
<dependency>
	<groupId>org.slf4j</groupId>
	<artifactId>jul-to-slf4j</artifactId>
	<version>1.7.12</version>
</dependency>
<dependency>
	<groupId>org.aspectj</groupId>
	<artifactId>aspectjweaver</artifactId>
	<version>1.8.1</version>
</dependency>
```

### 测试客户端



