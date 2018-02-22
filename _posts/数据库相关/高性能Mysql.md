---
layout:     post
title:      "高性能MySQL学习笔记"
subtitle:	""
date:       2016-10-23 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-snow.jpg"
tags:
    - 数据库相关
    - MySQL
---


MySQL  架构、事务、并发、引擎 介绍

架构设计特点：将查询处理以及其他任务系统  和  数据的储存、提取 相分离

架构分层：
- 连接、线程管理
- 查询缓存 、 解析器 、 内置函数 、 所有跨储存引擎的功能都在这一层实现
- 储存引擎：负责数据的存储和提取，服务器通过API与引擎进行交互，引擎执行底层函数




