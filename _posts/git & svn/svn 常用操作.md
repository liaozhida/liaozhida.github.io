svn 常用操作.md

> 整理成章

PS:
- svn没有本地操作，每次操作都是远程的服务器



设置忽略文件路径
```
svn propset svn:ignore 'plutus-api/target' .

svn update

svn commit -m "add a ignore dir"
```


删除已添加的文件
```
svn delete plutus-service/target --force
svn delete plutus-api/target --force
svn delete plutus-coverage/target --force
svn delete plutus-test/target --force
```

拉取项目

svn checkout url -username 

关于export命令：导出一个干净的不带.svn文件夹的目录树


###### 忽略文件改动

未加入控制的文件夹
```
svn propset svn:ignore 'test' .
svn update
svn commit -m "add a ignore dir"
```

已经加入版本控制的文件夹
```
svn export test test_bak
svn rm test
svn commit -m "delete test"
mv test_bak test
svn propset svn:ignore 'test' .
svn update
svn commit -m "add a ignore dir"
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