### 大量的jar引入失败

- 解决最前面的几个jar的错误，后面就会自动好
- 查看maven仓库是否有这个包
- 删除本地仓库的包。重新下载
- 引入第三方的jar包
- 更新远程仓库的索引

### Solve “Plugin execution not covered by lifecycle configuration” for Spring Data Maven Builds

- <build>标签中增加pluginManagement

```
<pluginManagement>
	<plugins>
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
									org.codehaus.mojo
								</groupId>
								<artifactId>
									build-helper-maven-plugin
								</artifactId>
								<versionRange>
									[1.9.1,)
								</versionRange>
								<goals>
									<goal>add-resource</goal>
								</goals>
							</pluginExecutionFilter>
							<action>
								<ignore />
							</action>
						</pluginExecution>
					</pluginExecutions>
				</lifecycleMappingMetadata>
			</configuration>
		</plugin>
	</plugins>
</pluginManagement>
```

- 修改环境配置
```
mvn -Declipse.workspace=/Users/zhidaliao/git  eclipse:add-maven-repo -e -X
```