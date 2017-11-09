## nodejs

编程规范与指南，对于有疑问的地方请提问和百度，觉得文档有必要完善，请提交issue

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Style](#style)
- [Rule](#rule)
- [Notice](#notice)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

[grunt-init-umi-node]: http://gitlab.umiit.cn/tool/grunt-init-umi-node.git
[grunt-init-umi-web]: http://gitlab.umiit.cn/tool/grunt-init-umi-web.git
[路由规则]: http://www.tuicool.com/articles/YnqUZjY
[express-enrouten]: http://www.npmjs.org/package/express-enrouten

### Introduction
目前Nodejs的应用分为2种: Web应用和非Web应用，两者的初始化目录结构都可以使用grunt-init来创建，详细的请参考 [grunt-init-umi-node][] 和 [grunt-init-umi-web][] ,以下将分别介绍两种应用的目录结构:

+ Web应用(grunt-init-umi-web)

```
example  	 	  	// 项目名称
  |- bin   	 	  	// 脚本目录，存放不同环境下启动的脚本，文件都是可执行文件
  |- config	 	  	// 配置文件目录，存放不同环境下的系统配置文件和日志配置文件
  |- controllers  	// Express的路由文件夹，请参考下面的 路由规则 和 express-enrouten
  |- lib		  	// 这里主要是一些公用代码
  |- logs		  	// 日志目录，所有的日志文件会存储在这个文件夹里，该目录会被提交到远程服务器，但里面的日志文件不会
  |- models		    // 定义mongo的文档(类似表结构)，如果应用没有使用到mongodb，这个文件夹可以删除掉
  |- node_modules 	// npm install生成的目录，不能加入git管理
  |- public		  	// 定义网站ico、robot(搜索引擎爬虫)配置文件
  |- site		  	// 网站编译后的页面，不能加入git管理，自动生成的
  |- src 		    // 网站html、css、js的目录，该目录的内容通过编译会生成上面的site目录
  |- .gitignore     // 定义哪些文件不需要git管理，通常不允许更改
  |- .gitlab-ci.yml // 不一定有，如果有gitlab会自动执行一些工作，可能会自动测试或者生成docker image，通常不需要更改
  |- .jshintrc    	// jshint的配置文件，用来对代码进行静态检查，不需要进行更改
  |- Dockerfile	  	// 定义该项目生成docker image，通常不需要更改
  |- Gruntfile.js 	// 定义Grunt的信息
  |- index.js 	  	// 启动文件，不需要进行修改
  |- package.json 	// 定义依赖的库和项目基础信息，建议百度了解所有字段的意义
  |- README.md    	// 项目安装、使用、更新等说明信息
```

+ 非Web应用(grunt-init-umi-node)

```
example  	 	  	// 项目名称
  |- lib		  	// 项目的代码目录
  |- test		  	// 测试脚本目录，里面的文件以`_test.js`结尾的文件会被当测试脚本执行
  |- node_modules 	// npm install生成的目录，不能加入git管理
  |- .gitignore   	// 定义哪些文件不需要git管理，通常不允许更改
  |- .gitlab-ci.yml // 不一定有，如果有gitlab会自动执行一些工作，可能会自动测试或者生成docker image，通常不需要更改
  |- .jshintrc    	// jshint的配置文件，用来对代码进行静态检查，不需要进行更改
  |- Gruntfile.js 	// 定义Grunt的信息
  |- package.json 	// 定义依赖的库和项目基础信息，建议百度了解所有字段的意义
  |- README.md    	// 项目安装、使用、更新等说明信息
```

参考链接:

+ [路由规则][]
+ [express-enrouten][]

### Style

### Rule

### Notice