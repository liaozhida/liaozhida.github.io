# 运行jetty容器项目.md

#### 指定虚拟机大小
```
MAVEN_OPTS='-Xmx850m -Xms500m' mvn clean compile  jetty:run -Pdev
```