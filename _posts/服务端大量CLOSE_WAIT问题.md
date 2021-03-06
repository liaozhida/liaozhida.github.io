服务端大量CLOSE_WAIT问题.md

### 现象描述：

服务端使用了quartz框架之后，刚开始启动jetty容器的时候，请求正常，大概几个请求完了之后，部分Mac机子出现客户端一直在请求，但是返回给客户端的信息是异常，服务端压根没有收到请求,或者收到请求代码执行的非常慢
使用命令 lsof -i:8080查看进程数，发现大量进程存在，并且状态是CLOSE_WAIT；正常情况下是在执行客户端请求的时候进程数增加，但随之会关闭。

CLOSE_WAIT：客户端关闭了socket连接，发送了FIN报文，服务端也发送了ACK报 文，此时客户端处于FIN_WAIT_2状态，服务端处于CLOSE_WAIT状态，问题的原因是服务端没有发送第二个FIN报文导致的。

可能的原因TCP请求：

- mongo
- redis
- mq
- mysql

因为quartz引入了新的mysql连接，所以估计是连接超上限的问题

#### 解决方案

- msyql 数据库的processList表，设置全局的超时时间100ms,得到验证，问题解决
- 设置连接池，以及空闲连接释放时间
- 设置增加JVM最大内存

### 参考网站

[服务端大量CLOSE_WAIT问题的解决](http://www.liuhaihua.cn/archives/45802.html)