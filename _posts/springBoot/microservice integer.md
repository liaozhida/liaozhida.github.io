microservice integer.md


## QA

- .ReplicationTaskProcessor   : Network level connection to peer localhost; retrying after delay

```
1

$ cat /etc/hosts
127.0.0.1       peer1
127.0.0.1       peer2
2

$ cat configs/eureka-replica.properties
server.port=8761
eureka.datacenter=peer1
eureka.instance.hostname=peer1
eureka.client.serviceUrl.defaultZone=http://peer2:8762/eureka/
3

$ cat configs/eureka.properties
server.port=8762
eureka.datacenter=peer2
eureka.instance.hostname=peer2
eureka.client.serviceUrl.defaultZone=http://peer1:8761/eureka/
4

$ cat configs/application.properties
eureka.server.registry-sync-retry-wait-ms=500
eureka.server.a-sgcache-expiry-timeout-ms=60000
eureka.server.eviction-interval-timer-in-ms=30000
eureka.server.peer-eureka-nodes-update-interval-ms=15000
eureka.server.renewal-threshold-update-interval-ms=300000

eureka.client.healthcheck.enabled=true
eureka.client.prefer-same-zone-eureka=true
eureka.client.region=zone2
eureka.client.availability-zones.zone1='peer1,peer2'
eureka.client.availability-zones.zone2='peer2,peer1'
eureka.client.serviceUrl.peer1=http://peer1:8761/eureka/
eureka.client.serviceUrl.peer2=http://peer2:8762/eureka/
eureka.client.serviceUrl.defaultZone=http://peer2:8762/eureka/
# seems like defaultZone must be configured
# so defaultZone peer will use all clients on start up registration if it will not specify
eureka.instance.appname=${spring.application.name}
eureka.instance.instanceId=${spring.application.name}-${spring.cloud.client.ipAddress}-${INSTANCE_ID:${random.value}}
eureka.instance.statusPageUrlPath=${management.contextPath}/info
eureka.instance.healthCheckUrlPath=${management.contextPath}/health
eureka.instance.preferIpAddress=true
# and other out of topic options
management.contextPath=/admin
endpoints.health.sensitive=false
spring.cloud.config.discovery.enabled=true
when not first peer will start, you'll find logs like these:

...PeerAwareInstanceRegistryImpl    : Got <some numbers of> instances from neighboring DS node
...PeerAwareInstanceRegistryImpl    : Renew threshold is: <some other number>
...PeerAwareInstanceRegistryImpl    : Changing status to UP
when peer1 go down, you will see log like this:

ERROR ... [-target_peer1-1] ...cluster.ReplicationTaskProcessor   : Network level connection to peer peer1; retrying after delay
as soon it will restore you'll see common instance registeration log message

- 打包成jar包的形式，代码内部无法加载文件


```

- cannot find 'resource' in class manifestresourcetransformer

```
springboot项目不需要用maven-shade-plugin打jar包啊, 就用spring-boot-maven-plugin
<start-class>cn.yeamoney.ticket.core.Application</start-class>

<plugin>
				<groupId>org.springframework.boot</groupId>
				<artifactId>spring-boot-maven-plugin</artifactId>

				<configuration>
					<executable>true</executable>
				</configuration>
				<executions>
					<execution>
						<goals>
							<goal>repackage</goal>
						</goals>
					</execution>
				</executions>
			</plugin>

```


