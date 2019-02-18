eclipse远程调试两种模式(java)




eclipse远程调试两种模式：
一、服务端监听
(1)服务器端需执行程序前加参数  -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8000
   说明：server=y 是指目标应用程序作为服务监听将要连接的远程调试器（常用）；
         suspend=y 是指目标VM将暂停，直到调试器应用程序进行连接（若需要调试启动错误，很有用）；
         suspend=n 是指目标VM不暂停；
         address=8000 监听端口。
(2)运行服务端程序，程序将暂停
(3)eclipse ==\> Debug Configurations ==\> Remote Java Application 新建测试工程
(4)选择工程 ==\> 模式 Socket Attach ==\>  调试服务器IP ==\> 调试端口(这里假设8000)
(5)运行debug



二、调试端监听（不常用）
(1)eclipse ==\> Debug Configurations ==\> Remote Java Application 新建测试工程
(2)选择工程 ==\> 模式 Socket Listen ==\> 调试监听端口(这里假设8000) ==\> Allow termination of remote VM 打勾
(3)运行debug，程序将暂停，左上显示 Waiting for vm to connect at port 8000...
(4)服务器端需执行程序前加参数  -Xdebug -Xrunjdwp:transport=dt_socket,address=172.16.7.34:8000
   说明：address=172.16.7.34:8000 发送连接的地址和端口。
(5)运行服务端程序


[][1]

[1]:	https://my.oschina.net/heguangdong/blog/14556 "eclipse远程调试两种模式(java) 原"