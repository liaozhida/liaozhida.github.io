```

<properties>
	<docker.registry>docker.umiit.cn:5043</docker.registry>
</properties>

<profiles>
	<profile>
		<id>dev</id>
		<properties>
			<env>dev</env>
		</properties>
		<activation>
			<activeByDefault>true</activeByDefault>
		</activation>
	</profile>
	<profile>
		<id>prod</id>
		<properties>
			<env>prod</env>
			<docker>latest</docker>
		</properties>
	</profile>
	<profile>
		<id>prep</id>
		<properties>
			<env>prep</env>
			<docker>prep</docker>
		</properties>
	</profile>
</profiles>


<plugin>
	<groupId>com.spotify</groupId>
	<artifactId>docker-maven-plugin</artifactId>
	<version>0.2.11</version>
	<configuration>
		<serverId>docker-hub</serverId>

		<!-- <dockerHost>${docker.host}</dockerHost> <dockerCertPath>${docker.cert.path}</dockerCertPath> -->
		<dockerDirectory>src/main/resources/docker</dockerDirectory>
		<!-- <imageTags> <imageTag>${project.version}</imageTag> </imageTags> -->
		<pushImage>true</pushImage>
		<imageName>
			${docker.registry}/v3/${project.artifactId}:${docker}
		</imageName>

		<resources>
			<resource>
				<targetPath>/</targetPath>
				<directory>${project.build.directory}</directory>
				<include>*.war</include>
				<!--							<include>${project.build.finalName}.jar</include>
-->
			</resource>
		</resources>
	</configuration>
</plugin>


```


