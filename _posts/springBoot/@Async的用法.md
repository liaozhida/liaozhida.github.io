@Async的用法.md


```
@Configuration
public class ContactsExecutor {

    @Value("${contacts.thread.core-pool}")
    private int corePoolSize;

    @Value("${contacts.thread.max-pool}")
    private int maxPoolSize;

    @Value("${contacts.queue.capacity}")
    private int queueCapacity;

    @Value("${contacts.thread.timeout}")
    private int threadTimeout;

    @Bean
    @Qualifier("contactsExecutor")
    public ThreadPoolTaskExecutor threadPoolTaskExecutor() {
        ThreadPoolTaskExecutor threadPoolTaskExecutor = new ThreadPoolTaskExecutor();
        threadPoolTaskExecutor.setCorePoolSize(corePoolSize);
        threadPoolTaskExecutor.setMaxPoolSize(maxPoolSize);
        threadPoolTaskExecutor.setQueueCapacity(queueCapacity);
        threadPoolTaskExecutor.setKeepAliveSeconds(threadTimeout);

        return threadPoolTaskExecutor;
    }
}
```


```
# thread pool and queue size for processing contacts data
contacts.thread.timeout=2
contacts.thread.core-pool=10
contacts.thread.max-pool=25
contacts.queue.capacity=25

```


```
@EnableAsync
@ComponentScan
@EnableAutoConfiguration
public class Application {
.......
}

```

Java

```
@Async("mainExecutor")
public void methodA(){}
```

[Configure queue and thread pool for async execution](http://yysource.com/2016/05/spring-boot-executing-asynchronous-method-backed-with-a-queue/)

