搭建python开发环境.md


### Python环境

现在主流的Linux 版本和Mac 机子都是自带python不需要额外安装；
```
➜  ~ python
Python 2.7.10 (default, Oct 23 2015, 19:19:21)
[GCC 4.2.1 Compatible Apple LLVM 7.0.0 (clang-700.0.59.5)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

sudo easy_install pip



### 集成sublime开发环境

##### SublimeREPL

`shift + command + p` 打开面板输入 `install packages` ,安装 `SublimeREPL`

安装成功之后：Tools -> SublimeREPL -> python -> run current file 即可运行

键位绑定

当然每次通过Tools 这样的方式比较繁琐,将这样的操作和一个按键如`F1`绑定后，就会方便很多啦

打开Preferences->Key Bindings-User，复制一下代码：
```
{"keys":["f1"],
"caption": "SublimeREPL: Python",
"command": "run_existing_window_command", "args":
{"id": "repl_python",
"file": "config/Python/Main.sublime-menu"}}
```

ps 如果还想编译下热乎乎的py代码，可以复制以下代码：
```
{"keys":["f2"],
"caption": "SublimeREPL: Python - RUN current file",
"command": "run_existing_window_command", "args":
{"id": "repl_python_run",
"file": "config/Python/Main.sublime-menu"}}
```


##### command + B 

直接在sublime中使用`command + B ` 就可以看到输出结果





## 参考网址


[https://www.zhihu.com/question/22904994/answer/87527103](https://www.zhihu.com/question/22904994/answer/87527103)