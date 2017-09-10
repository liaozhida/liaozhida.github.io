# 生命周期内执行代码 & 获取IP地址.md


```
<plugin>
	<groupId>org.codehaus.groovy.maven</groupId>
	<artifactId>gmaven-plugin</artifactId>

	<executions>
		<execution>
			<phase>initialize</phase>
			<goals>
				<goal>execute</goal>
			</goals>
			<configuration>
				<source>
					List interfaces = ["eth0", "en0", "eth1", "en1", "eth2", "en2", "eth3", "en3", "wlan0"]
                    Enumeration nets = NetworkInterface.getNetworkInterfaces();
                    for (NetworkInterface netint : Collections.list(nets)) {
                        println netint;
                        if (interfaces.contains(netint.getName())) {
                            Enumeration inetAddresses = netint.getInetAddresses();
                            for (InetAddress inetAddress : Collections.list(inetAddresses)) {
                                if (!inetAddress.isAnyLocalAddress()) {
                                    println("InetAddress: " + inetAddress);
                                    project.properties["hostname"] = inetAddress.getHostAddress().replace("/","")
                                }
                            }
                        }
                    }
                    println "Using the IP: "+project.properties["hostname"];
				</source>
			</configuration>
		</execution>
	</executions>
</plugin>
```