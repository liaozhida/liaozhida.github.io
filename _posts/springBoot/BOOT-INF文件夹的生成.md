BOOT-INF文件夹的生成.md


使用这个插件生成的文件夹
```
<plugin>
	<groupId>org.springframework.boot</groupId>
	<artifactId>spring-boot-maven-plugin</artifactId>
</plugin>



```

如果什么也不配置，这个项目的源代码将不会打包到进去
可能会报错：main class is not found

需要配置
<start-class>cn.yeamoney.service.ipc.Application</start-class>


```
<plugin>
	<groupId>org.springframework.boot</groupId>
	<artifactId>spring-boot-maven-plugin</artifactId>
	<!-- defined in spring-cloud-starter-parent pom (as documentation hint), 
		but needs to be repeated here -->
	<configuration>
		<requiresUnpack>
			<dependency>
				<groupId>com.netflix.eureka</groupId>
				<artifactId>eureka-core</artifactId>
			</dependency>
			<dependency>
				<groupId>com.netflix.eureka</groupId>
				<artifactId>eureka-client</artifactId>
			</dependency>
		</requiresUnpack>
	</configuration>
</plugin>
```

上面的配置将会把源码打包进去


#### BOOT-INF文件夹的生成会造成Ebean的 springboot jar 项目找不到需要enhance的类

因为他会把所有的依赖包放在 和classes并排的lib文件夹下面，里面都是jar包
否则都是源文件 。








