# 监听SpringBoot的生命周期.md

application.properties中，添加：

```
context.listener.classes=com.example.listener.ApplicationEventListener
```

实现ApplicationListener接口：

```
public class ApplicationEventListener implementsApplicationListener {

    @Override
    public voidonApplicationEvent(ApplicationEvent event) {
       // 在这里可以监听到Spring Boot的生命周期
      if (eventinstanceof ApplicationEnvironmentPreparedEvent){ // 初始化环境变量 }
      else if (eventinstanceof ApplicationPreparedEvent){ // 初始化完成 }
      else if (eventinstanceof ContextRefreshedEvent) { // 应用刷新 }
      else if (eventinstanceof ApplicationReadyEvent) {// 应用已启动完成}
      else if (eventinstanceof ContextStartedEvent) { //应用启动，需要在代码动态添加监听器才可捕获 }
      else if (eventinstanceof ContextStoppedEvent) { // 应用停止 }
      else if(event instanceof ContextClosedEvent) { // 应用关闭 }
      else{}
    }

}
```


[在Web项目中，启动Spring容器的方式有三种...](http://www.cnblogs.com/duanxz/p/5074584.html)