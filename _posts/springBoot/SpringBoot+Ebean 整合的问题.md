## SpringBoot 整合的问题


### Ebean
SpringBoot会自动检测ebean的jar包，生成配置文件


### QA
Error trying to create the default EbeanServer java.lang.RuntimeException: Error in classpath search (looking for entities etc)

修改ebean.properties文件 

原配置:

```
ebean.search.jars = yea-model
```

新配置:
```
ebean.search.packages = cn.yeamoney.model 
```

springboot 打包之后， 所有的class文件都会以包结构的形式整合进去，不存在打包依赖jar的情况。
所以必须修改寻找依赖类的方式


### Redis

自动搜寻redis.properties




[spring boot reference](http://docs.spring.io/spring-boot/docs/current/reference/html/common-application-properties.html)