---
layout:     post
title:      "Netty学习笔记"
subtitle:	""
date:       2016-10-23 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-snow.jpg"
tags:
    - 
---

## 出现的原因

传统的方式

client- TCP - Socket - Socket Server - accept 

一个请求一个线程 ， 线程会持续堵塞。 线程数量有限


线程池的方式

固定数量的线程，封装任务处理  依然是阻塞 伪异步 新的请求会被拒绝


netty的两种场景 ： 文件处理 网络传输处理


## 基础知识

###### [处理并发之一：LINUX Epoll机制介绍](https://www.ezlippi.com/blog/2014/08/linux-epoll.html) | [Epoll 模型简介](http://www.jianshu.com/p/0fb633010296)

2.2 select模型

最大并发数限制，因为一个进程所打开的FD（文件描述符）是有限制的，由FD_SETSIZE设置，默认值是1024/2048，因此Select模型的最大并发数就被相应限制了。自己改改这个FD_SETSIZE？想法虽好，可是先看看下面吧…

效率问题，select每次调用都会线性扫描全部的FD集合，这样效率就会呈现线性下降，把FD_SETSIZE改大的后果就是，大家都慢慢来，什么？都超时了？？！！

内核/用户空间 内存拷贝问题，如何让内核把FD消息通知给用户空间呢？在这个问题上select采取了内存拷贝方法。

2.3 poll模型

基本上效率和select是相同的，select缺点的2和3它都没有改掉。

3.Epoll的提升

select的缺点之一就是在网络IO流到来的时候，线程会轮询监控文件数组，并且是线性扫描，还有最大值的限制。相比select，epoll则无需如此。服务器主线程创建了epoll对象，并且注册socket和文件事件即可。当数据抵达的时候，也就是对于事件发生，则会调用此前注册的那个io文件。

把其他模型逐个批判了一下，再来看看Epoll的改进之处吧，其实把select的缺点反过来那就是Epoll的优点了。

3.1. Epoll没有最大并发连接的限制，上限是最大可以打开文件的数目，这个数字一般远大于2048, 一般来说这个数目和系统内存关系很大，具体数目可以cat /proc/sys/fs/file-max察看。

3.2. 效率提升，Epoll最大的优点就在于它只管你“活跃”的连接，而跟连接总数无关，因此在实际的网络环境中，Epoll的效率就会远远高于select和poll。

3.3. 内存拷贝，Epoll在这点上使用了“共享内存”，这个内存拷贝也省略了。

## Tour

直接看英文文档学习，效果最佳，包括源码可以下载

[User guide for 4.x](http://netty.io/wiki/user-guide-for-4.x.html)









