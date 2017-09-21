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


编写线程安全代码的核心在于:对`共享` `可变的`状态访问操作进行管理

线程安全类的定义: 多个线程访问某个类时,类始终表现出正确的行为

方法： 
- 不共享（线程封闭）
- 可变的 (final)
- 多个线程访问： 同步、内存可见性



