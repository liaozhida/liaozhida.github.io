# 基础入门.md

## 介绍

Feign is a handy project from Netflix that lets you describe a REST API client declaratively with annotations on an interface.

Feign中对 Hystrix有依赖关系。Feign只是一个便利的rest框架，简化调用，最后还是通过ribbon在注册服务器中找到服务实例，然后对请求进行分配。 

Each feign client is part of an ensemble of components that work together to contact a remote server on demand, and the ensemble has a name that you give it as an application developer using the @FeignClient annotation. Spring Cloud creates a new ensemble as an ApplicationContext on demand for each named client using FeignClientsConfiguration. This contains (amongst other things) an feign.Decoder, a feign.Encoder, and a feign.Contract.

## 实际项目

##### Application.java 

```
@EnableFeignClients
```

##### TicketClient.java

```
@FeignClient(value = "ticket-service", configuration = YeaFeignConfiguration.class,fallback = TicketClientHystrix.class)
interface TicketClient {

	@RequestMapping(method = RequestMethod.POST, value = "/create")
	Message<String> create(
			@RequestParam(value = "Type") Integer Type, 
			@RequestParam(value = "amount") String amount,
			@RequestParam(value = "userId") String userId, 
			@RequestParam(value = "mobile") String mobile,
			@RequestParam(value = "status") Integer status, 
			@RequestParam(value = "belong") Integer belong,
			@RequestParam(value = "useProfit")String useProfit,
			@RequestParam(value = "useCounter")String useCounter);
}

```

##### YeaFeignConfiguration.java

```
@Configuration
public class YeaFeignConfiguration {

	public static final int CONNECT_TIMEOUT_MILLIS = 5000;
	public static final int READ_TIMEOUT_MILLIS = 5000;

	@Bean
	public Logger.Level feignLogger() {
		return Logger.Level.FULL;
	}

	@Bean
	public Request.Options options() {
		return new Request.Options(CONNECT_TIMEOUT_MILLIS, READ_TIMEOUT_MILLIS);
	}
}

```



## Feign 原生示例

获取URL的代码，然后封装成对象返回

##### Java Code
```
public class GitHubExample {

	interface GitHub {

		class Repository {
			String name;
		}

		class Contributor {
			String login;
		}

		@RequestLine("GET /users/{username}/repos?sort=full_name")
		List<Repository> repos(@Param("username") String owner);

		@RequestLine("GET /repos/{owner}/{repo}/contributors")
		List<Contributor> contributors(@Param("owner") String owner, @Param("repo") String repo);

		/** Lists all contributors for all repos owned by a user. */
		default List<String> contributors(String owner) {
			return repos(owner).stream().flatMap(repo -> contributors(owner, repo.name).stream()).map(c -> c.login)
					.distinct().collect(Collectors.toList());
		}

		static GitHub connect() {
			Decoder decoder = new GsonDecoder();
			return Feign.builder().decoder(decoder).errorDecoder(new GitHubErrorDecoder(decoder))
					.logger(new Logger.ErrorLogger()).logLevel(Logger.Level.BASIC)
					.target(GitHub.class, "https://api.github.com");
		}
	}

	static class GitHubClientError extends RuntimeException {
		private String message; // parsed from json

		@Override
		public String getMessage() {
			return message;
		}
	}

	static class GitHubErrorDecoder implements ErrorDecoder {

		final Decoder decoder;
		final ErrorDecoder defaultDecoder = new ErrorDecoder.Default();

		GitHubErrorDecoder(Decoder decoder) {
			this.decoder = decoder;
		}

		@Override
		public Exception decode(String methodKey, Response response) {
			try {
				return (Exception) decoder.decode(response, GitHubClientError.class);
			} catch (IOException fallbackToDefault) {
				return defaultDecoder.decode(methodKey, response);
			}
		}
	}

	public static void main(String... args) {

		GitHub github = GitHub.connect();

		System.out.println("Let's fetch and print a list of the contributors to this org.");
		List<String> contributors = github.contributors("netflix");
		for (String contributor : contributors) {
			System.out.println(contributor);
		}

		System.out.println("Now, let's cause an error.");
		try {
			github.contributors("netflix", "some-unknown-project");
		} catch (GitHubClientError e) {
			System.out.println(e.getMessage());
		}
	}
}

```

##### pom.xml

```
<dependency>
  <groupId>io.github.openfeign</groupId>
  <artifactId>feign-core</artifactId>
  <version>${project.version}</version>
</dependency>
<dependency>
  <groupId>io.github.openfeign</groupId>
  <artifactId>feign-gson</artifactId>
  <version>${project.version}</version>
</dependency>
```

## FEIGN CLIENT WITH HYSTRIXOBSERVABLE WRAPPER

With Hystrix on the classpath, you can also return a HystrixComman

##### base

```
@FeignClient("http://notification-service")
public interface NotificationVersionResource {  
    @RequestMapping(value = "/version", method = GET)
    String version();
}
```

##### integer

```
@FeignClient("http://notification-service")
public interface NotificationVersionResource {  
    @RequestMapping(value = "/version", method = GET)
    HystrixObservable<String> version();
}
```

## FEIGN CLIENT WITH HYSTRIX FALLBACK

使用fallback的特性有两种方式：

- feign属性中指定 fallback = TicketClientHystrix.class   ，TicketClientHystrix实现接口的方法。
- Feign Clients have direct support for fallbacks. Simply implement the interface with the fallback code, which will then be used when the actual call to the endpoint delivers an error.

第二种：
```
@FeignClient("http://notification-service")
public interface NotificationResource {  
    @RequestMapping(value = "/notifications", method = GET)
    List<Notification> findAll();
}

public class NotificationResourceImpl implements NotificationResource {  
    @Override
    public List<Notification> findAll() {
        return new ArrayList<>();
    }
}

```

## 使用外部链接

之前的示例都是在服务发现中，使用service的Name 去访问，但是同样的也支持使用外部链接去访问。
```
@FeignClient(name = "reddit-service", url = "${com.deswaef.reddit.url}")
public interface RedditResource {  
    @RequestMapping(method = RequestMethod.GET, value = "/java.json")
    RedditResponse posts();
}
```


## 可选配置项

##### Spring Cloud Netflix provides the following beans by default for feign (BeanType beanName: ClassName):

`Decoder` feignDecoder: ResponseEntityDecoder
`Encoder` feignEncoder: SpringEncoder
`Logger` feignLogger: Slf4jLogger
`Contract` feignContract: SpringMvcContract
`Feign.Builder` feignBuilder: HystrixFeign.Builder

The OkHttpClient and ApacheHttpClient feign clients can be used by setting feign.okhttp.enabled or feign.httpclient.enabled to true, respectively, and having them on the classpath.

##### Spring Cloud Netflix does not provide the following beans by default for feign, but still looks up beans of these types from the application context to create the feign client:

`Logger.Level`
`Retryer`
`ErrorDecoder`
`Request.Options`
`Collection`

Creating a bean of one of those type and placing it in a @FeignClient configuration (such as FooConfiguration above) allows you to override each one of the beans described. Example:

```
@Configuration
public class FooConfiguration {
    @Bean
    public Contract feignContract() {
        return new feign.Contract.Default();
    }

    @Bean
    public BasicAuthRequestInterceptor basicAuthRequestInterceptor() {
        return new BasicAuthRequestInterceptor("user", "password");
    }
}
```

##### 使用bean的形式覆盖fegin的属性

```
@FeignClient(
    name = "reddit-service", 
    url = "${com.deswaef.reddit.url}", 
    configuration = RedditFeignConfiguration.class
)
```

```
@Configuration
public class RedditFeignConfiguration {  
    public static final int FIVE_SECONDS = 5000;
    @Bean
    public Logger.Level feignLogger() {
        return Logger.Level.FULL;
    }
    @Bean
    public Request.Options options() {
        return new Request.Options(FIVE_SECONDS, FIVE_SECONDS);
    }
}
```

## Feign中不依赖 Hystrix

If you need to use ThreadLocal bound variables in your RequestInterceptor`s you will need to either set the thread isolation strategy for Hystrix to `SEMAPHORE or disable Hystrix in Feign.

```
# To disable Hystrix in Feign
feign:
  hystrix:
    enabled: false

# To set thread isolation to SEMAPHORE
hystrix:
  command:
    default:
      execution:
        isolation:
          strategy: SEMAPHORE
```

`PS:` 
if this configuration class is on the component scan path, it'll be also picked up as general configuration. This means that a configuration class like this, when also scanned by our automatic component scan, will override all of the beans for each and every FeignClient, not just the one which defined it as configuration.
也就是说，要是被 automatic component扫描到了，所有的FeignClient都会按照这个class的配置项去生效，而不是仅仅configuration = RedditFeignConfiguration.class 这个显示声明的接口，

As a result, you should place it inside a package that isn't a candidate for a component scan
不要放在能被扫描到的包中。

最简单的做法，就是不要标记 @Configuration 注释。


## 手动调用Feign 


两个示例：
```
@Import(FeignClientsConfiguration.class)
class FooController {

	private FooClient fooClient;

	private FooClient adminClient;

    @Autowired
	public FooController(
			Decoder decoder, Encoder encoder, Client client) {
		this.fooClient = Feign.builder().client(client)
				.encoder(encoder)
				.decoder(decoder)
				.requestInterceptor(new BasicAuthRequestInterceptor("user", "user"))
				.target(FooClient.class, "http://PROD-SVC");
		this.adminClient = Feign.builder().client(client)
				.encoder(encoder)
				.decoder(decoder)
				.requestInterceptor(new BasicAuthRequestInterceptor("admin", "admin"))
				.target(FooClient.class, "http://PROD-SVC");
    }
}

## In the above example FeignClientsConfiguration.class is the default configuration provided by Spring Cloud Netflix.
```

```
interface GitHub {

		class Repository {
			String name;
		}

		class Contributor {
			String login;
		}

		@RequestLine("GET /users/{username}/repos?sort=full_name")
		List<Repository> repos(@Param("username") String owner);

		@RequestLine("GET /repos/{owner}/{repo}/contributors")
		List<Contributor> contributors(@Param("owner") String owner, @Param("repo") String repo);

		/** Lists all contributors for all repos owned by a user. */
		default List<String> contributors(String owner) {
			return repos(owner).stream().flatMap(repo -> contributors(owner, repo.name).stream()).map(c -> c.login)
					.distinct().collect(Collectors.toList());
		}

		static GitHub connect() {
			Decoder decoder = new GsonDecoder();
			return Feign.builder().decoder(decoder).errorDecoder(new GitHubErrorDecoder(decoder))
					.logger(new Logger.ErrorLogger()).logLevel(Logger.Level.BASIC)
					.target(GitHub.class, "https://api.github.com");
		}
	}
```

## Feign Hystrix Support

Hystrix is on the classpath and feign.hystrix.enabled=true, Feign will wrap all methods with a circuit breaker. 
Returning a com.netflix.hystrix.HystrixCommand is also available. 
This lets you use reactive patterns (with a call to .toObservable() or .observe() or asynchronous use (with a call to .queue()).

`Note:`Prior to the Spring Cloud Dalston release, if Hystrix was on the classpath Feign would have wrapped all methods in a circuit breaker by default. This default behavior was changed in Spring Cloud Dalston in favor for an opt-in approach.

To disable Hystrix support on a per-client basis create a vanilla Feign.Builder with the "prototype" scope, e.g.:

```
@Configuration
public class FooConfiguration {
    @Bean
	@Scope("prototype")
	public Feign.Builder feignBuilder() {
		return Feign.builder();
	}
}
```

## Feign Hystrix Fallbacks

常规的降级方式：

```
@FeignClient(name = "hello", fallback = HystrixClientFallback.class)
protected interface HystrixClient {
    @RequestMapping(method = RequestMethod.GET, value = "/hello")
    Hello iFailSometimes();
}

static class HystrixClientFallback implements HystrixClient {
    @Override
    public Hello iFailSometimes() {
        return new Hello("fallback");
    }
}
```

如果想要在测试的时候触发降级操作，可以使用fallbackFactory

```
@FeignClient(name = "hello", fallbackFactory = HystrixClientFallbackFactory.class)
protected interface HystrixClient {
	@RequestMapping(method = RequestMethod.GET, value = "/hello")
	Hello iFailSometimes();
}

@Component
static class HystrixClientFallbackFactory implements FallbackFactory<HystrixClient> {
	@Override
	public HystrixClient create(Throwable cause) {
		return new HystrixClientWithFallBackFactory() {
			@Override
			public Hello iFailSometimes() {
				return new Hello("fallback; reason was: " + cause.getMessage());
			}
		};
	}
}
```

`Note:`	
There is a limitation with the implementation of fallbacks in Feign and how Hystrix fallbacks work. 
Fallbacks are currently not supported for methods that return com.netflix.hystrix.HystrixCommand and rx.Observable.

通过接口实现的方式去实现降级存在一些局限性。
Fallbacks 当前不支持 在方法中返回com.netflix.hystrix.HystrixCommand and rx.Observable.的情况。


## Feign and @Primary

When using Feign with Hystrix fallbacks, there are multiple beans in the ApplicationContext of the same type. This will cause @Autowired to not work because there isn’t exactly one bean, or one marked as primary. To work around this, Spring Cloud Netflix marks all Feign instances as @Primary, so Spring Framework will know which bean to inject. In some cases, this may not be desirable. To turn off this behavior set the primary attribute of @FeignClient to false.

```
@FeignClient(name = "hello", primary = false)
public interface HelloClient {
	// methods here
}
```


## Feign request/response compression

You may consider enabling the request or response GZIP compression for your Feign requests. You can do this by enabling one of the properties:

```
feign.compression.request.enabled=true
feign.compression.response.enabled=true
Feign request compression gives you settings similar to what you may set for your web server:
```

```
feign.compression.request.enabled=true
feign.compression.request.mime-types=text/xml,application/xml,application/json
feign.compression.request.min-request-size=2048
```

These properties allow you to be selective about the compressed media types and minimum request threshold length.

## Feign logging

A logger is created for each Feign client created. By default the name of the logger is the full class name of the interface used to create the Feign client. Feign logging only responds to the DEBUG level.

##### application.yml

```
logging.level.project.user.UserClient: DEBUG
```

The Logger.Level object that you may configure per client, tells Feign how much to log. Choices are:

NONE, No logging (DEFAULT).

BASIC, Log only the request method and URL and the response status code and execution time.

HEADERS, Log the basic information along with request and response headers.

FULL, Log the headers, body, and metadata for both requests and responses.

For example, the following would set the Logger.Level to FULL:

@Configuration
public class FooConfiguration {
    @Bean
    Logger.Level feignLoggerLevel() {
        return Logger.Level.FULL;
    }
}

## QA

## 参考网站

[Feign-github](https://github.com/OpenFeign/feign)

[The Netflix stack, using Spring Boot - Part 3: Feign](https://blog.de-swaef.eu/the-netflix-stack-using-spring-boot-part-3-feign/)

[http://cloud.spring.io/spring-cloud-netflix/spring-cloud-netflix.html#spring-cloud-feign](http://cloud.spring.io/spring-cloud-netflix/spring-cloud-netflix.html#spring-cloud-feign)

