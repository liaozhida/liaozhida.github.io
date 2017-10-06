---
layout:     post
title:      "Java程序员修炼之道学习笔记"
date:       2016-10-25 12:00:00
author:     "zhida"
header-img: "img/post-bg-1.jpg"
tags:
    -  Java
    -  学习笔记
---


控制反转
- 非IOC编程，程序的逻辑流程通常是由一个 “功能中心” 来控制的
- 反转， 调用者的代码 处理程序的 执行顺序，而`程序逻辑`则被封装在接受调用的 子流程中。

场景：
- 命令行程序：用户输入指令；游戏的主应用逻辑调用恰当的事件处理器来处理这些指令；关键点是`应用逻辑要控制调用哪个事件处理器`
- GUI程序：GUI界面来控制调用事件处理器；`应用逻辑重点放在处理动作上`

IOC的几种实现：
- 工厂模式
- 服务定位模式
- DI：依赖注入

依赖注入：寻找依赖项的工作不在当前代码下，而是通过第三方注入。

工厂模式的缺点：
- 代码中注入的是一个 引用凭据，而不是一个真正的对象
- 代码中还是有一部分在处理对象的获取问题，而不是专注在业务流程的处理

不同的IOC框架标准不一致，会造成迁移的成本过高。Guide和Spring推出了`JSR-330`标准,JavaSE的JSR-299构建在JSR-330标准上
JSR-330标准如下：
@Inject
@Named
@Qualifier
@Scope
@Singleton
Provider

@Inject注解：因为JRE无法决定构造器的优先级，所以@inject使用在构造器中，只能有一个

分支合并框架
locks
quciksort & TimSort

JVM 知识  、 类加载知识

Scala 知识

TDD

## 参考网站

[JSR330](https://github.com/google/guice/wiki/JSR330)
