## 如何正确编写docker-compose.yml

docker-compose目前有两种编写规范，两种编写风格的区别：

- 特点是在文件的顶格删除了 version 标签。
- 比较推荐的格式是 在文件的顶部增加version:X 标签

> 不能在同一个项目中混合使用两种风格

不同版本之间会有以下的不同

- 文件结构和允许使用的关键字
- 对docker engine最低版本使用要求
- 关于网络部分的不同表现形式

### Version 1

不会定义 version 这种格式，所有的service都会在顶层被定义

Version 1 一直支持到 Compose 1.6.x版本. 在未来新的版本中将不再被支持

Version 1 文件不能定义以下的关键字 volumes, networks or build arguments.

示例:

```
web:
  build: .
  ports:
   - "5000:5000"
  volumes:
   - .:/code
  links:
   - redis
redis:
  image: redis
```

### Version 2

文件必须在顶部使用version关键字表明版本信息，所有的service必须在service关键字下面进行声明。

所需要的版本信息：
- Compose 1.6.0+ 
- Docker Engine of version 1.10.0+.

Named volumes can be declared under the volumes key, and networks can be declared under the networks key.

示例:

```
version: '2'
services:
  web:
    build: .
    ports:
     - "5000:5000"
    volumes:
     - .:/code
  redis:
    image: redis
```

```
version: '2'
services:
  web:
    build: .
    ports:
     - "5000:5000"
    volumes:
     - .:/code
    networks:
      - front-tier
      - back-tier
  redis:
    image: redis
    volumes:
      - redis-data:/var/lib/redis
    networks:
      - back-tier
volumes:
  redis-data:
    driver: local
networks:
  front-tier:
    driver: bridge
  back-tier:
    driver: bridge

```

### 如何升级

在大多数案例中，可以很简单的将version1迁移到version2。

在所有的service之前增加`service`关键字
在文件的最顶部增加 `version:'2'`

如果使用了比较复杂的配置特性，修改起来会比较复杂：

- dockerfile: This now lives under the build key:

```
build:
  context: .
  dockerfile: Dockerfile-alternate
```

- log_driver, log_opt: These now live under the logging key:

```
logging:
  driver: syslog
  options:
    syslog-address: "tcp://192.168.0.42:123"
```

- links和environment环境变量：

使用links标签来创建环境变量，然后在environment标签中使用，这种做法已经被废弃了，在新的Docker网络系统中，他们已经被移除。
你应该直接链接他们的域名或者设置一个系统环境变量以便被引用

```
web:
  links:
    - db
  environment:
    - DB_PORT=tcp://db:5432
```

- external_links: 

当运行 version 2项目的时候Compose会使用Docker networks,所以链接方式有一些区别，特别是两个容器必须链接到至少一个网络中，即使明确地链接在一起。
> Compose uses Docker networks when running version 2 projects, so links behave slightly differently. In particular, two containers must be connected to at least one network in common in order to communicate, even if explicitly linked together.

在你的应用的默认网络中链接外部的容器，或者两个容器一起链接到一个外部网络中。
> Either connect the external container to your app’s default network, or connect both the external container and your service’s containers to an external network.

- net: This is now replaced by network_mode:

```
net: host    ->  network_mode: host
net: bridge  ->  network_mode: bridge
net: none    ->  network_mode: none
```

If you’re using `net: "container:[service name]"`, you must now use network_mode: "service:[service name]" instead.

```
net: "container:web"  ->  network_mode: "service:web"
```

If you’re using `net: "container:[container name/id]"`, the value does not need to change.

```
net: "container:cont-name"  ->  network_mode: "container:cont-name"
net: "container:abc12345"   ->  network_mode: "container:abc12345"
```

- volumes with named volumes:  这个标签将会出现在文件的一级目录，如果一个service 挂载了一个键值为data的volume，你必须如下所示，在一级目录声明。

```
version: '2'
services:
  db:
    image: postgres
    volumes:
      - data:/var/lib/postgresql/data
volumes:
  data: {}
```

默认情况下，Compose创建了一个以项目名称命名的Volume，如果你想只要使用data变量就行，使用external声明
> By default, Compose creates a volume whose name is prefixed with your project name. If you want it to just be called data, declared it as external:

```
volumes:
  data:
    external: true
```
