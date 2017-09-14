---
layout:     post
title:      "Ebean使用maven配置的加载流程"
date:       2015-02-22 12:00:00
author:     "zhida.liao"
header-img: "img/post-bg-2015.jpg"
tags:
    - ebean
    - 数据库相关
---

> This document is not completed and will be updated anytime.

## Ebean使用maven配置的加载流程

Ebean相对于其他的ORM框架，显得更轻量级和简便，没有很多复杂的配置文件(mybatis)和难懂难驾驭的特性(hibernate),解放了程序员的开发效率，但也将很多特性隐藏了起来

#### 准备工作

##### pom中依赖的jar包

```
<dependency>
	<groupId>org.avaje.ebeanorm</groupId>
	<artifactId>avaje-ebeanorm-spring</artifactId>
	<version>3.3.1</version>
	<exclusions>
		<exclusion>
			<artifactId>avaje-ebeanorm</artifactId>
			<groupId>org.avaje.ebeanorm</groupId>
		</exclusion>
	</exclusions>
</dependency>
<dependency>
	<groupId>org.avaje.ebeanorm</groupId>
	<artifactId>avaje-ebeanorm-agent</artifactId>
	<version>4.5.3</version>
</dependency>
<dependency>
	<groupId>org.avaje</groupId>
	<artifactId>avaje-agentloader</artifactId>
	<version>2.1.1</version>
</dependency>
```

##### pom中依赖的插件

```
<plugin>
	<groupId>org.avaje.ebeanorm</groupId>
	<artifactId>avaje-ebeanorm-mavenenhancer</artifactId>
	<version>4.5.3</version>
	<executions>
		<execution>
			<id>process-classes</id>
			<phase>process-classes</phase>
			<configuration>
				<classSource>target/classes</classSource>
				<classDestination>target/classes</classDestination>
				<packages>cn.yeamoney.rest.domain.**,cn.yeamoney.rest.service.**</packages>
				<transformArgs>debug=1</transformArgs>
			</configuration>
			<goals>
				<goal>enhance</goal>
			</goals>
		</execution>
	</executions>
</plugin>
```

##### ebean的配置文件

```
#Created by JInto - www.guh-software.de
#Wed Jan 13 16:35:00 CST 2016
datasource.default=pg
datasource.pg.databaseDriver=org.postgresql.Driver
datasource.pg.databaseUrl=jdbc\:postgresql\://192.168.99.100\:5432/yea
datasource.pg.heartbeatsql=select 1
datasource.pg.password=
datasource.pg.username=postgres
ebean.ddl.generate=false
ebean.ddl.run=false
ebean.debug.lazyload=false
ebean.debug.sql=true
ebean.logging=all
ebean.logging.directory=logs
ebean.logging.iud=sql
ebean.logging.logfilesharing=all
ebean.logging.query=sql
ebean.logging.sqlquery=sql
ebean.logging.txnCommit=none
```

#### 启动流程

##### 增强插件
根据官网的提示 ： http://ebean-orm.github.io/docs/setup/enhancement
我们可以知道，Ebean对Model的增强是在pom中使用avaje-ebeanorm-mavenenhancer插件实现的，在这个插件里面可以配置需要增强的包(package),在4.7.1以上的版本不需要指定，将会自动寻找需要增强的类

##### 代理
使用***avaje-ebeanorm-agent***,引入代理将普通bean变成实体bean

##### 代理加载器

使用***avaje-agentloader***,加载指定的代理，在启动运行jvm的时候装载代理，普通bean变成实体bean有极低的机率会失败

源码如下
```
import org.avaje.agentloader;
...
public void someApplicationBootupMethod() {
  // Load the agent into the running JVM process
  if (!AgentLoader.loadAgentFromClasspath("avaje-ebeanorm-agent","debug=1;packages=org.example.model.**")) {
    logger.info("avaje-ebeanorm-agent not found in classpath - not dynamically loaded");
  }
}
```

##### ServerConfig

在org.avaje.ebeanorm包中有一个类ServerConfig,专门保存Ebean的配置信息,
EbeanServerFactory会通过ServerConfig配置文件创建EbeanServer
ServerConfig的loadFromProperties方法会加载默认配置文件ebean.properties，当然也能指定想要加载的配置文件

###### 注册属性

通过设置 ServerConfig.setRegister(true)可以开启注册功能，默认为true
开启该功能之后,就可以使用Ebean 单例实例化 EbeanServer

```
config.setName("pg");
EbeanServer server = EbeanServerFactory.create(config);
EbeanServer server = Ebean.getServer("pg");
```

##### 默认的server

```java
ServerConfig config = new ServerConfig();
config.setName("pg");
config.setDefaultServer(true);
EbeanServer server = EbeanServerFactory.create(config);
EbeanServer server = Ebean.getDefaultServer();
// 实现效果和上面的代码一样
EbeanServer server = Ebean.getServer(null);
```

#### 结合spring使用




`转载请注明出处  来源:`[paraller's blog](http://www.paraller.com)

