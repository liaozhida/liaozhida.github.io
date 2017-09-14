# history相关.md

### 使用

在输入命令前 Crtl/control + R ，可以打开历史命令提示

### history命令的记录如何删除？

```
vim /etc/profile
HISTSIZE=1   // 或者0
```
```
echo '' > ~/.bash_history
```


### 立即清空里的history当前历史命令的记录  

```
history -c  
```

### 立即更新历史命令

bash执行命令时不是马上把命令名称写入history文件的，而是存放在内部的buffer中，等bash退出时会一并写入。  
不过，可以调用'history -w'命令要求bash立即更新history文件。  

```
history -w
```

