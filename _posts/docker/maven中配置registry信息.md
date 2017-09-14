# maven中配置registry信息.md

### vim settings.xml

```
<servers>
	<server>
	  <id>nexus</id>
	  <username>**</username>
	  <password>**</password>
	</server>
	<server>
	  <id>docker-hub</id>
	  <username>**</username>
	  <password>**</password>
	  <configuration>
	    <email>ci@**.cn</email>
	  </configuration>
	</server>
</servers>
```


### vim pom.xml

```
<plugin>
	<groupId>com.spotify</groupId>
	<artifactId>docker-maven-plugin</artifactId>
	<version>0.4.14</version>
	<configuration>
		<serverId>docker-hub</serverId>
		<pushImage>true</pushImage>
		<imageName>
			${docker.registry}/v3/${project.artifactId}:${docker}
		</imageName>

		<dockerDirectory>src/main/resources/docker</dockerDirectory>
		<resources>
			<resource>
				<targetPath>/</targetPath>
				<directory>${project.build.directory}</directory>
				<include>${project.build.finalName}.jar</include>
			</resource>
		</resources>
	</configuration>
</plugin>
```

## 参考网站

[https://github.com/spotify/docker-maven-plugin](https://github.com/spotify/docker-maven-plugin)