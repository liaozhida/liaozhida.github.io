telnet.md


其实 telnet 的源码包并不叫 telnet ，而是叫 inetutils 。

```
Hzzs-MacBook-Pro:~ hzz$ brew install inetutils
Updating Homebrew...
```




------




在linux/unix下使用telnet hostname port连接上主机后会提示Escape character is '^]'

这个提示的意思是按Ctrl + ] 会呼出telnet的命令行，出来telnet命令好之后就可以执行telnet命令，例如退出出telnet是quit.

其他常用的telnet命令功能描述：

close关闭当前连接
logout强制退出远程用户并关闭连接
display显示当前操作的参数
mode试图进入命令行方式或字符方式
open连接到某一站点
quit退出
telnetsend发送特殊字符
set设置当前操作的参数
unset复位当前操作参数
status打印状态信息
toggle对操作参数进行开关转换
slc改变特殊字符的状态
auth打开/关闭确认功能z挂起
telnetenviron更改环境变量?显示帮助信息