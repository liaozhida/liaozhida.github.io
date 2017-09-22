---
layout:     post
title:      "Java并发编程实战笔记-总结"
date:       2016-01-29 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-2015.jpg"
tags:
    - 并发编程
---

> This document is not completed and will be updated anytime.
> Java并发编程实战这本书用到的类库都比较旧，需要及时更新
> 增加对线程安全类的源码研究



编写线程安全代码的核心在于:对`共享` `可变的`状态访问操作进行管理，同时注意迭代器模式中的并发修改异常

线程安全类的定义: 多个线程访问某个类时,类始终表现出正确的行为

方法： 
- 不共享（线程封闭）
- 可变的 (final)
- 多个线程访问： 同步、内存可见性




List  | Vector/ Collections.synchronizedList | CopyOnWriteArrayList 
HashMap | HashTable / Collections.synchronizedMap | ConcurrentHashMap
Set | Collections.synchronizedSet | CopyOnWriteArraySet
queue | concurrentLinkQueue 