## git

本文会提供一些git的比较好的学习资料、一些常用命令和开发流程的使用场景

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Command](#command)
- [Git-flow](#git-flow)
- [Skill](#skill)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

[写好 Git Commit 信息的 7 个建议]: http://blog.jobbole.com/92713/

### Introduction

首先对git要有基本的认识，这里不做太多的介绍，仅提供一些较好的资料，请 **认真** 一篇一篇阅读和理解，欢迎提问

+ [Pro Git（中文版）](http://git.oschina.net/progit/)
	重点章节(**必看**): 
	- [1.3 Git 基础](http://git.oschina.net/progit/1-起步.html#1.3-Git-基础)
	- [2 Git 基础](http://git.oschina.net/progit/2-Git-基础.html)
	- [3 Git 分支](http://git.oschina.net/progit/3-Git-分支.html)
	- [5 分布式 Git](http://git.oschina.net/progit/5-分布式-Git.html) **了解一下即可**
	- [6 Git 工具](http://git.oschina.net/progit/6-Git-工具.html) **重点看(6.1-6.4)章节**

+ [GitLab Flow](http://www.15yan.com/topic/yi-dong-kai-fa-na-dian-shi/6yueHxcgD9Z/)
	这篇是使用git工作的流程，请 **认真** 阅读和理解，会比较深奥一点，希望能及时提问

+ [团队使用Git和Git-Flow手记](http://www.tuicool.com/articles/QfYju2)
	这篇是git-flow的使用日志，结合上一篇理解

+ [写好 Git Commit 信息的 7 个建议][]
	很重要，请 **认真** 阅读和实际

### Command

在对git有基本的认识和理解后，我们重点了解一些常用的命令，前面也已经提到了大部分的命令。标准的命令是 `git xxx` 方式，但是我们使用了oh-my-zsh的插件，它会采用alias的方式简化命令，从而不用每次都输入很长的命令，比如 `git status` 查看状态，使用oh-my-zsh后，命令可以直接使用 `gst` 。更多的命令简写方式可以在命令行输入 `alias` 来查看。

+ 查看状态

	`git status` 或者 `gst` 这是最常用的命令，**做任何其他操作时，都应该执行该命令来看看状态，以确保接下来的命令是符合期望的**


+ git初始化

	`git init` 对于一个项目一般只会执行一次，把一个非git管理的文件夹(项目)使用git管理起来

	`git flow init` 或者 `gfl init` 使用该命令会完成上一命令的工作，同时还会新建一些分支，请在了解git-flow之后进行实践


+ 远程仓库定义

	`git remote -v` 或者 `grv` 查看当前项目的远程仓库地址，一个项目可以有多个远程仓库地址的，默认会有一个叫`origin`

	`git remote add [名称] [地址]` 或者 `gra  [名称] [地址]` 给当前项目添加一个远程仓库地址，这样就可以将代码提交到添加的远程仓库中了

	`git remote rename|remove ` 可以添加，同样可以修改和删除


+ 从远处仓库迁出代码

	`git clone [远处仓库地址]` 或者 `gcl [远处仓库地址]` 该命令会在当前目录下迁出代码,通常迁出的代码会在 `master分支`

	`git checkout -t origin/develop` 或者 `gco -t origin/develop` 如果需要跟踪其他分支的时候，使用该命令，`origin/develop`就代表远程仓库的develop分支


+ 将修改的内容加入跟踪管理

	`git add [文件]` 或者 `ga [文件]` 指定需要加入跟踪的文件

	`git add --all` 或者 `gaa` 通常在一个目录下，可能需要把所有修改的文件都加入跟踪，不需要一个一个文件加入，就可使用该命令


+ 提交到本地仓库(除了以下两个命令，请少用其他commit命令)

	`git commit -v` 或者`gc` 注意是提交到**本地仓库**，不是**远程仓库**，使用该命令后，会在sublime弹出一个文件，在该文件里面写相关的message，message的写法请参考 [写好 Git Commit 信息的 7 个建议][]，写好后保存关闭即可(`command + s` 然后 `command + w`)

	`git commit -v --amend` 或者`gc!` 当你发现commit之后message写错了，可以使用该命令重新写！


+ 获取最新的分支和数据

	`git fetch -p` 或者 `gf -p` 


+ 查看和操作所有分支情况

	`git branch -a -v` 或者 `gba -v`

	`git branch -d|-D [分支名]` 或者 `gb -d|-D [分支名]` 只能删除本地分支 -D为强制删除


+ 新建分支和切换分支

	`git checkout -b [分支名]` 或者`gcb` 以当前分支为基准，创建一个一样的分支

	`git checkout [分支名]` 切换到指定分支，常用的有: 

	- `gcm` : master分支
	- `gcd` : develop分支


+ 拉取和推送到远程仓库

	`git pull origin $(git_current_branch)` 或者 `ggpull` 从远程仓库拉取代码并且何必到当前分支

	`git push origin $(git_current_branch)` 或者 `ggpush` 推送当前分支到远处仓库
	

+ 查看commit日志
	
	`git log` 或者 `glg` 或者 `glgg` 或者 `glgga` 区别是日志的详细程度


## Git-flow

在gitlab中，master分支是受保护的分支，意思就是你无法将代码提交这个分支中，这个分支只能通过在gitlab中进行合并。工作流程如下:

+ 如果本地无项目，请在对应的目录(注意:**所有代码必须存在git文件对应的路径**)从远程分支签下项目

+ 如果没有issue，不能修改任何代码，意思就是必须有问题了才需要修改代码，可以在issues页面查看确定要解决哪一个问题，比如确定要解决issues #2问题

+ 不能在master分支上修改任何代码，需要新建分支来开发，使用命令`gcb 2-xxx`,其中的2是相应的issues编号，这样就已经在相应的分支下了

+ 修改完代码后，确保测试等环节都没有问题，使用`gc`来commit到本地，commit message的标题必须写`fix #2 , xxxx`

+ 确认完毕后，使用`ggpush`将当前分支提交到远程仓库等待code review

+ 所有的分支**最好**都基于master分支去创建，但是有可能上一个issue的代码还未被何必到master，这个时候你可以从其他分支创建，在创建之前最好使用`ggpull`来确保分支的一致性


## Skill

一些实用的技巧

+ 因为不允许在master分支上修改代码，但是如果修改了，不可能重新还原再写一遍吧，怎么办？

	```
	gsta 	//在master分支下将当前的修改进入缓存区
	gcb xxx //切换到应该修改的分支下
	gstaa   //将缓存区的内容应用到当前分支下，完成
	```

+ 当你commit到本地之后，发现上一次的提交中还少了一些修改内容，那你需要把上一次的提交取消，然后重新commit

	```
	git reflog //查看需要回滚的commit号，例如98ad499
	git reset 98ad499
	```

+ TOOD，等遇到问题，再来添加，请大家发现问题及时提问，以便完善文档

