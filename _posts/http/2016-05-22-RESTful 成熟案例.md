---
layout:     post
title:      "RESTful 成熟案例"
date:       2015-05-22 12:00:00
author:     "zhida"
header-img: "img/post-bg-1.jpg"
tags:
    -  http 
---



Leonard Richardson（注：与本文作者 Chris 无任何关系）为 REST 定义了一个成熟度模型，具体包含以下四个层次：

Level 0：本层级的 Web 服务只是使用 HTTP 作为传输方式，实际上只是远程方法调用（RPC）的一种具体形式。SOAP 和 XML-RPC 都属于此类。
Level 1：Level 1 层级的 API 引入了资源的概念。要执行对资源的操作，客户端发出指定要执行的操作和任何参数的 POST 请求。
Level 2：Level 2 层级的 API 使用 HTTP 语法来执行操作，譬如 GET 表示获取、POST 表示创建、PUT 表示更新。如有必要，请求参数和主体指定操作的参数。这能够让服务影响 web 基础设施服务，如缓存 GET 请求。
Level 3：Level 3 层级的 API 基于 HATEOAS（Hypertext As The Engine Of Application State）原则设计，基本思想是在由 GET请求返回的资源信息中包含链接，这些链接能够执行该资源允许的操作。例如，客户端通过订单资源中包含的链接取消某一订单，GET 请求被发送去获取该订单。HATEOAS 的优点包括无需在客户端代码中写入硬链接的 URL。此外，由于资源信息中包含可允许操作的链接，客户端无需猜测在资源的当前状态下执行何种
操作。



Level 3范例：

```
package photos;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.EnableEurekaClient;
import org.springframework.core.io.Resource;
import org.springframework.data.mongodb.gridfs.GridFsTemplate;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.IOException;
import java.io.InputStream;
import java.net.URI;

@SpringBootApplication
@EnableEurekaClient
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

@RestController
@RequestMapping("/{userId}/photo")
class PhotoRestController {

    @Autowired
    private GridFsTemplate gridFsTemplate;

    @RequestMapping(method = {RequestMethod.POST, RequestMethod.PUT})
    ResponseEntity<?> set(String userId,
                          @RequestParam MultipartFile multipartFile,
                          UriComponentsBuilder uriBuilder) throws IOException {

        try (InputStream inputStream = multipartFile.getInputStream()) {
            this.gridFsTemplate.store(inputStream, userId);
        }
        URI uri = uriBuilder.path("/{userId}/photo").buildAndExpand(userId).toUri();
        HttpHeaders headers = new HttpHeaders();
        headers.setLocation(uri);
        return new ResponseEntity<>(headers, HttpStatus.CREATED);
    }

    @RequestMapping(method = RequestMethod.GET)
    ResponseEntity<Resource> get(String userId) {
        HttpHeaders httpHeaders = new HttpHeaders();
        httpHeaders.setContentType(MediaType.IMAGE_JPEG);
        return new ResponseEntity<>(
                this.gridFsTemplate.getResource(userId), httpHeaders, HttpStatus.OK);
    }
}
```

## 参考网站

[「Chris Richardson 微服务系列」微服务架构中的进程间通信](http://blog.daocloud.io/microservices-3/)