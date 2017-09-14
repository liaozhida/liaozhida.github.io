# enhance class.md


## 没有第三方包：

#### pom.xml
```
<!-- 将model的包和 引用它的service包一起 enhance-->
<plugin>
	<groupId>org.avaje.ebeanorm</groupId>
	<artifactId>avaje-ebeanorm-mavenenhancer</artifactId>
	<version>4.5.3</version>
	<executions>
		<execution>
			<id>process-classes</id>
			<phase>process-classes</phase>
			<configuration>
				<classSource>${project.build.outputDirectory}</classSource>
				<classDestination>${project.build.outputDirectory}</classDestination>
				<packages>cn.yeamoney.ticket.service.**,cn.yeamoney.ticket.bean.**</packages>
				<transformArgs>debug=1</transformArgs>
			</configuration>
			<goals>
				<goal>enhance</goal>
			</goals>
		</execution>
	</executions>
</plugin>
```


#### ebean.properties 
```
## ebean.search.packages 增加这个属性
#Created by JInto - www.guh-software.de
#Mon May 22 19:06:12 CST 2017
datasource.default=mysql
datasource.mysql.databaseDriver=com.mysql.jdbc.Driver
datasource.mysql.databaseUrl=jdbc\:mysql\://127.0.0.1\:3306/yea?characterEncoding\=UTF-8
datasource.mysql.heartbeatsql=select 1
datasource.mysql.maxConnections=1000
datasource.mysql.password=mysqlpwd
datasource.mysql.username=root
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
ebean.search.packages=cn.yeamoney.ticket.bean

```

## 第三包

### yea-model

#### pom.xml
```
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>

	<groupId>cn.yeamoney.model</groupId>
	<artifactId>yea-model</artifactId>
	<version>3.2.1</version>
	<packaging>jar</packaging>

	<name>yea-model</name>

	<properties>
		<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
		<jdk.version>1.7</jdk.version>
	</properties>

	<dependencies>
		<dependency>
			<groupId>junit</groupId>
			<artifactId>junit</artifactId>
			<version>4.12</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>com.google.code.gson</groupId>
			<artifactId>gson</artifactId>
			<version>2.3.1</version>
		</dependency>

		<!-- 数据库 -->
		<dependency>
			<groupId>javax.persistence</groupId>
			<artifactId>persistence-api</artifactId>
			<version>1.0.2</version>
		</dependency>
		<dependency>
			<groupId>mysql</groupId>
			<artifactId>mysql-connector-java</artifactId>
			<version>5.1.38</version>
		</dependency>
		<dependency>
			<artifactId>avaje-ebeanorm</artifactId>
			<groupId>org.avaje.ebeanorm</groupId>
			<version>4.7.2</version>
		</dependency>
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

		<dependency>
			<groupId>commons-beanutils</groupId>
			<artifactId>commons-beanutils</artifactId>
			<version>1.9.3</version>
		</dependency>

	</dependencies>


	<distributionManagement>
		<repository>
			<id>nexus</id>
			<name>Release Repository</name>
			<url>http://m2.umiit.cn/content/repositories/releases/</url>
		</repository>
		<snapshotRepository>
			<id>nexus</id>
			<name>Snapshot Repository</name>
			<url>http://m2.umiit.cn/content/repositories/snapshots/</url>
		</snapshotRepository>
	</distributionManagement>


	<build>
		<plugins>
			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-compiler-plugin</artifactId>
				<version>3.0</version>
				<configuration>
					<source>${jdk.version}</source>
					<target>${jdk.version}</target>
					<encoding>${project.build.sourceEncoding}</encoding>
				</configuration>
			</plugin>
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
							<packages>cn.yeamoney.model.**</packages>
							<transformArgs>debug=1</transformArgs>


							<!-- 
							<configuration>
								<packages>cn.yeamoney.service.**</packages>
								<transformArgs>debug=1</transformArgs>
								<project.jar.name>yea-model.jar</project.jar.name>
							</configuration> 
							-->
						</configuration>
						<goals>
							<goal>enhance</goal>
						</goals>
					</execution>
				</executions>
			</plugin>

			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-compiler-plugin</artifactId>
				<version>3.0</version>
				<configuration>
					<source>${jdk.version}</source>
					<target>${jdk.version}</target>
					<encoding>${project.build.sourceEncoding}</encoding>
				</configuration>
			</plugin>


		</plugins>
		<pluginManagement>
			<plugins>
				<!--This plugin's configuration is used to store Eclipse m2e settings 
					only. It has no influence on the Maven build itself. -->
				<plugin>
					<groupId>org.eclipse.m2e</groupId>
					<artifactId>lifecycle-mapping</artifactId>
					<version>1.0.0</version>
					<configuration>
						<lifecycleMappingMetadata>
							<pluginExecutions>
								<pluginExecution>
									<pluginExecutionFilter>
										<groupId>
											org.avaje.ebeanorm
										</groupId>
										<artifactId>
											avaje-ebeanorm-mavenenhancer
										</artifactId>
										<versionRange>
											[4.5.3,)
										</versionRange>
										<goals>
											<goal>enhance</goal>
										</goals>
									</pluginExecutionFilter>
									<action>
										<ignore />
									</action>
								</pluginExecution>
								<pluginExecution>
									<pluginExecutionFilter>
										<groupId>
											org.mybatis.generator
										</groupId>
										<artifactId>
											mybatis-generator-maven-plugin
										</artifactId>
										<versionRange>
											[1.3.2,)
										</versionRange>
										<goals>
											<goal>generate</goal>
										</goals>
									</pluginExecutionFilter>
									<action>
										<ignore></ignore>
									</action>
								</pluginExecution>
							</pluginExecutions>
						</lifecycleMappingMetadata>
					</configuration>
				</plugin>
			</plugins>
		</pluginManagement>
	</build>
</project>

```

### yea-service

#### ebean.properties
```
#Created by JInto - www.guh-software.de
#Sun Dec 11 10:17:56 CST 2016
datasource.default=mysql
datasource.mysql.databaseDriver=com.mysql.jdbc.Driver
datasource.mysql.databaseUrl=jdbc\:mysql\://127.0.0.1\:3306/yea?characterEncoding\=UTF-8
datasource.mysql.heartbeatsql=select 1
datasource.mysql.maxConnections=1000
datasource.mysql.password=mysqlpwd
datasource.mysql.username=root
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
ebean.search.jars=yea-model 
你说你是不是欠  
```

pom.xml
```
<plugin>
	<groupId>org.avaje.ebeanorm</groupId>
	<artifactId>avaje-ebeanorm-mavenenhancer</artifactId>
	<version>4.8.1</version>
	<executions>
		<execution>
			<id>process-classes</id>
			<phase>process-classes</phase>
			<configuration>
				<packages>cn.yeamoney.service.core**</packages>
				<transformArgs>debug=1</transformArgs>
				<project.jar.name>yea-model.jar</project.jar.name>
			</configuration>
			<goals>
				<goal>enhance</goal>
			</goals>
		</execution>
	</executions>
</plugin>
```