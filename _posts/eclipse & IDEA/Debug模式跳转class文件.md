Debug模式跳转class文件

[https://blog.csdn.net/wqc19920906/article/details/78652234][1]


今天团队一小伙伴调试项目时，一不小心选错了源文件目录(maven分模块项目)，选到了顶层父项目下的文件，结果调试时发现无法查看调试过程中的变量值，要解决这个问题，其实很简单，稍稍配置一下就可以了，为了方便其他小伙伴查阅，就简单记录一下。
步骤：找到调试小虫子--\>选择‘Debug Configurations‘--\>弹出框内左侧找到对应的工程--\>选择右侧的Source 配置--\>修改‘Source Lookup Path‘为‘WorkSpace‘--\>勾选‘Search for duplicate source files on the path‘--\>‘Apply‘  就ok了

[1]:	https://blog.csdn.net/wqc19920906/article/details/78652234 "解决：eclipse 断点调试进入到class文件，无法查看变量值问题"