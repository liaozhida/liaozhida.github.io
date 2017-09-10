### 安装springBoot-cli
```
brew tap pivotal/tap
brew install springboot
```

Homebrew will install spring to /usr/local/bin.

### 测试小程序

#### 创建 app.groovy

```
@RestController
class ThisWillActuallyRun {

    @RequestMapping("/")
    String home() {
        "Hello World!"
    }

}
```

#### 启动 

```
spring  run app.groovy
```

#### 测试
```
localhost:8080
```

第一次下载依赖，启动够速度比较慢
后续将会跳过这一步

### 构建一个正式的应用

#### 检查java maven的环境变量是否正常

```
java -version
mvn -v
```

#### 添加pom.xml

```
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>jar</packaging>

    <name>demo</name>
    <description>Demo project for Spring Boot</description>


    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <java.version>1.7</java.version>
    </properties>

    <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>1.4.3.RELEASE</version>
</parent>
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
</dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>


</project>
```

#### 检查mvn是否正常

mvn package & mvn dependency:tree

#### Add java code 

src/main/java/Example.java

```
import org.springframework.boot.*;
import org.springframework.boot.autoconfigure.*;
import org.springframework.stereotype.*;
import org.springframework.web.bind.annotation.*;

@RestController
@EnableAutoConfiguration
public class Example {

    @RequestMapping("/")
    String home() {
        return "Hello Wo2rld!";
    }

    public static void main(String[] args) throws Exception {
        SpringApplication.run(Example.class, args);
    }

}
```
#### java code 注解

- @EnableAutoConfiguration：这个注释告知spring boot ,应该要怎么去配置spring 通过pom的spring-boot-starter-web配置，添加tomcat和springMVC
- SpringApplication 启动spring，并且自动配置相关的依赖信息，比如：tomcat的web服务

#### 启动

spring run *.java

http://localhost:8080/

### 构建一个可执行的jar包

(springboot样例)[https://github.com/spring-projects/spring-boot]



