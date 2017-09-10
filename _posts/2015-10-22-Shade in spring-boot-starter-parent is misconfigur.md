## Shade in spring-boot-starter-parent is misconfigured

##### 原配置

```
<plugin>
	<groupId>org.apache.maven.plugins</groupId>
	<artifactId>maven-shade-plugin</artifactId>
	<version>2.3</version>
	<executions>
		<!-- Run shade goal on package phase -->
		<execution>
			<phase>package</phase>
			<goals>
				<goal>shade</goal>
			</goals>
			<configuration>
				<transformers>
					<transformer
						implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
						<mainClass>cn.yeamoney.ws.core.Application</mainClass>
					</transformer>
				</transformers>
			</configuration>
		</execution>
	</executions>
</plugin>
```

##### 执行`mvn install`报错：

```
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-shade-plugin:2.1:shade (default) on project spring-boot-example: 
Unable to parse configuration of mojo org.apache.maven.plugins:maven-shade-plugin:2.1:shade for parameter transformers: 
Cannot load  XXX 
-> [Help 1]
```


##### 修改配置如下

```
<plugin>
	<groupId>org.apache.maven.plugins</groupId>
	<artifactId>maven-shade-plugin</artifactId>
	<version>2.3</version>
	<executions>
		<!-- Run shade goal on package phase -->
		<execution>
			<phase>package</phase>
			<goals>
				<goal>shade</goal>
			</goals> 
			<configuration>
				<transformers>
					<transformer
						implementation="org.apache.maven.plugins.shade.resource.AppendingTransformer">
						<resource>META-INF/spring.handlers</resource>
					</transformer>
					<transformer
						implementation="org.springframework.boot.maven.PropertiesMergingResourceTransformer">
						<resource>META-INF/spring.factories</resource>
					</transformer>
					<transformer
						implementation="org.apache.maven.plugins.shade.resource.AppendingTransformer">
						<resource>META-INF/spring.schemas</resource>
					</transformer>
					<transformer
						implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer" />
					<transformer
						implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
						<mainClass>cn.yeamoney.ws.core.Application</mainClass>
					</transformer>
				</transformers>
			</configuration>
		</execution>
	</executions>
</plugin>
```

##### 分析

The Spring resource transformer class name changed  (at least once) since the parent was originally created.


##### 原网址
[Shade in spring-boot-starter-parent is misconfigured](https://github.com/spring-projects/spring-boot/issues/384)