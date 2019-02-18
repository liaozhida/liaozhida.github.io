svn 常用操作.md

> 整理成章

PS:
- svn没有本地操作，每次操作都是远程的服务器



### 设置忽略文件路径
```
svn propset svn:ignore 'plutus-api/target' .
	
svn update

svn commit -m "add a ignore dir"
(svn ci -m "")
```

- 最后的 . 不能忽略
- svn status --no-ignore  查看被忽略的文件
- 忽略文件夹，千万不要加斜杠。
- 使用 —R 递归属性配置
- 通过配置文件来忽略： `svn propset svn:ignore -R -F .svnignore .`


[使用svn进行文件和文件夹的忽略](https://www.jianshu.com/p/c02d8b335495)


### 删除已添加的文件
```
svn delete plutus-service/target --force
```

### 拉取项目

svn checkout url -username 

关于export命令：导出一个干净的不带.svn文件夹的目录树


### 移除已添加的文件，文件还存在，不再加入版本控制

已经加入版本控制的文件夹
```
svn delete --keep-local [path]
```


### 添加文件

把忽略中的文件也添加到仓库
```
svn add *
```

排查忽略的文件
```
svn add --force .
```

### 恢复

不受SVN 版本控制

```
svn revert  targe
```

文件夹
```
svn revert --depth=targe .
```






---


暂时未添加到版本控制的文件或者文件夹
打开终端 执行 `vi ~/.subversion/config`
修改 global-ignore , 保存退出即可


如果已经添加进入了版本控制，那么要先将其从版本控制中删除才会生效
```
eg ：删除 UserInterfaceState.xcuserstate 文件
svn rm --force UserInterfaceState.xcuserstate
svn commit -m "忽略该死的UserInterfaceState.xcuserstate"
注：也可以使用绝对的路径进行rm
```



#### 常见问题

###### eclipse 插件subclipse 错误 This client is too old to work with working copy

升级eclipse插件 http://subclipse.tigris.org/update_1.8.x

###### The working copy needs to be upgraded svn: Working copy 'C:\.... is too old (format 10, created by Subversion 1.6)

`svn upgrade`


#### 参考网站

[给SVN控制的项目添加忽略文件/文件夹](http://yansu.org/2013/04/22/add-svn-ignore-file.html)

[svn 配置忽略文件](https://www.jianshu.com/p/1b183aeaf077)

[SVN常用命令](https://blog.csdn.net/ithomer/article/details/6187464)

[eclipse 插件subclipse 错误 This client is too old to work with working copy](https://blog.csdn.net/cuidiwhere/article/details/26863811)