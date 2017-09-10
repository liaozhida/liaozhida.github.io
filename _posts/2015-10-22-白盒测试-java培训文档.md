java后台项目运行机制介绍
===================

目录
-------------

----------

[TOC]

----------

背景
-------------
为了让测试人员能够更好的做白盒测试，特说写了该文档介绍java项目的运行机制

----------

文档说明
-------------
####  <i class="icon-pencil"></i> 阅读对象
本文阅读对象：研发工程师，测试工程师。
#### <i class="icon-pencil"></i>  版本说明
2017.4.26
:   发布新建版本，本文档适用于测试于测试工程师，研发工程师)。

----------

项目部署流程时序图
-------------
项目部署流程时序图:

```sequence
docker服务器->本地项目: 1. 从gitlab拉取项目到本地进行功能开发
本地项目->docker服务器: 2. 开发需求功能，完成之后推送到gitlab仓库
docker服务器->docker服务器: 3. 推送构建的镜像
（测试/正式服）服务器->docker服务器: 4. 服务器从docker服务器push镜像到本地
docker服务器->>（测试/正式服）服务器: 5. docker服务器返回镜像给服务器
```

> **Note:** 

> - 1 根据git flow流程，拉取项目代码，并进行开发，docker服务器上面搭建了gitlab
> - 2 当推送到gitlab的时候，会根据配置文件，确认是否进行docker构建，创建镜像
> - 3 (测试/正式服)服务器启动的时候，会去拉取docker服务器的镜像到本地，并进行启动

----------

项目运行流程时序图
-------------

```sequence

客户端->node: 1. IOS，Android，PC点击发起请求
node->node: 2.做数据交验，保存用户登录基础信息，数据交互过滤，页面展示
node->java服务: 3. 请求操作数据库相关逻辑
java服务->mysql: 4. 增删改查数据库操作
java服务->>node: 5. 封装业务数据
node->>客户端: 6. 展示给用户

```
> **Note:** 


----------

java运行流程图
-------------
java运行流程，以app支付订单为场景

```sequence
resource层->core/service层: 1. 接受node层发送过来的订单数据，做数据交验，过滤等工作
core/service层->数据库: 2. 根据业务逻辑操作数据库，查询，更新等操作
core/service层->yeamsg: 3. 发送订单的MQ消息
yeamsg->yeamsg: 4. 处理订单的MQ消息，做相关的业务场景
core/service层->>resource层: 5. 把返回数据结果封装起来，返回结果

```




----------

项目框架结构图
-------------
项目框架结构:

![](http://icard-img.golf2win.com/2017-04-26-7bd75947-f0dc-4d01-a72f-36c607ef8151.jpg)


----------
技术／平台说明
-------------

介绍下平台所有运用到的技术／平台，以及彼此之间的配合

#### <i class="icon-pencil"></i> Gitlab 
一个开源的版本管理系统，实现一个自托管的Git项目仓库，可通过Web界面进行访问公开的或者私人项目。它拥有与Github类似的功能，能够浏览源代码，管理缺陷和注释。可以管理团队对仓库的访问，它非常易于浏览提交过的版本并提供一个文件历史库。它还提供一个代码片段收集功能可以轻松实现代码复用，便于日后有需要的时候进行查找。
:   公司所有的项目都托管在上面以及构建的docker镜像


#### <i class="icon-pencil"></i> Docker
Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的容器中，然后发布到任何流行的 Linux 机器上去运行。
服务器的docker配置
:   git配置文件：ssh://git@gitlab.umiit.cn:2222/yeamoney/aliyun.git
:  公共镜像部分：nginx,redis,mysql,mongo,logstash
:  项目应用:  java项目，node项目镜像，会从docker服务器上面拉取

优点
:   可以做到测试服和正式服的环境一致性，不用去手动改变配置变量
:   快速部署应用

#### <i class="icon-pencil"></i> Mysql

数据库，系统所有的数据都会储存在mysql中，可以通过navicat图形化工具去做查询，测试，修改数据等操作

#### <i class="icon-pencil"></i> Redis

数据缓存，会针对一些频繁等查询的数据放入到redis中，以减少mysql查询压力。

#### <i class="icon-pencil"></i> Mongo

数据缓存，会针对一些频繁等查询的数据放入到mongo中，以减少mysql查询压力。
主要运用于node.js，主要针对用户的行为，比如登录的seesion，token，用户协议等方面，大部分不会涉及到数据库表的存储


#### <i class="icon-pencil"></i> nginx

反向代理服务器，可以根据客户的情况，反向代理到不同的项目。
其它的可以配置负载均衡等

#### <i class="icon-pencil"></i> node.js

略


----------


Java
-------------------

java后台服务采用spring，ebean框架集成

#### <i class="icon-pencil"></i> 项目介绍
yea-model
:   基础项目，主要是对数据库实体类的操作以及一些公共方法，以供其它的项目使用

yea-msg
:   配置了阿里云的MQ，主要用来进行消息推送和定时任务/活动处理，短信发送，邮件发送等；

yea-console
:   控制台（处理控制台的业务流程）
:   例如：企业组分配、APP版本控制、银行卡额度限制、邀请好友、体验金发放、运营数据查询
:   风控部对资产的审核、客服部数据查询等等操作

yea-service
:   对业务的基本操作（不涉及资金业务操作）
:   例如：用户基本信息、银行卡信息（只查）、体验金、投资产品列表机及其交易、活动列表等的增删查改

yea-core
:   主要对资金业务操作（充值、提现、投资、银行卡绑定等），是主要业务核心范围

#### <i class="icon-pencil"></i> 项目框架目录
![](http://img.golf2win.com/1.pic.jpg)

以yea-service项目为例子

- src/main/java/cn.yeamoney.service.resource : 接受客户端请求参数，做数据交验，过滤等
- src/main/java/cn.yeamoney.service.core : 从resource层接受数据后，做业务请求，数据库操作增删改查等
- src/main/java/cn.yeamoney.service.redis : redis缓存操作，增删改查
- src/main/java/cn.yeamoney.service.bean : 返回数据的结构类
- src/main/resources_xxx : 本地，测试服，正式服对应等数据库，email，mongo，redis，redis，mq等配置文件
- src/main/resources : htmls证书，dockerfile构建文件等配置文件
- pom.xml: maven配置文件，jar依赖，jetty，docker插件等
-  README.md : 对应项目等接口文档，目前里面的内容未完善，待以后更新完善

#### <i class="icon-pencil"></i> 运行机制
yea-model项目通过maven打包成jar包，以供其它项目使用
yea-msg启动了类MsgApplication，去监听yea-core,yea-service,yea-console发送的消息队列，邮件，短信通知，并进行及时处理
yea-core,yea-service,yea-console项目通过maven运行打包成war包，然后以maven配置的jetty插件容器去启动，开放对应的端口，运行，提供服务

----------

白盒测试
-------------

#### <i class="icon-pencil"></i> 动态测试
可以针对接口文档中的接口说明，模拟实例数据来动态运行程序

#### <i class="icon-pencil"></i> 静态测试
主要分析代码结构，设计等缺陷
推荐工具：Sonar，Fidbugs

----------


其它
-------------

#### <i class="icon-pencil"></i> 开发流程

- feature -> develop -> release -> hotfix(可选) -> master
- 根据issue创建对应的feature分支，命名格式为 issue-author-desc
- feature分支开发完成(经过自己的测试)，在issue下通知测试人员进行完整性的测试
- 开发者在收到测试人员的问题回复后，在feature分支进行修改。完整性测试通过之后会在issue中@开发人员，此时可以发起develope分支的合并请求
- 开发组的负责人对feature分支进行review，确认代码风格和业务逻辑没有问题，合并进develop分支中，并@测试人员
- 测试人员在测试服进行第二次测试，确认没有问题在issue下@志达 对代码进行release打包处理
- hotfix分支： 在线上代码存在严重问题的时候，从master上直接切 issue-hotfix 分支，经过测试后@志达 进行release打包，然后合并入master和develop中
- (参考文档)[http://www.ituring.com.cn/article/56870]



