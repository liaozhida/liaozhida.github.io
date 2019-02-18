设置Mac环境变量.md



```
st ~/.bash_profile
```


```
export M2_HOME=/Users/zhidaliao/apache-maven-3.5.3
export PATH=$PATH:$M2_HOME/bin


export M2_HOME=/Users/zhida.lzd/apache-maven-3.5.3
export PATH=$PATH:$M2_HOME/bin
```


```
mvn -v
```


```
Mac配置环境变量的地方

 1./etc/profile   （建议不修改这个文件 ）

 全局（公有）配置，不管是哪个用户，登录时都会读取该文件。

 

 2./etc/bashrc    （一般在这个文件中添加系统级环境变量）

 全局（公有）配置，bash shell执行时，不管是何种方式，都会读取此文件。

 

 3.~/.bash_profile  （一般在这个文件中添加用户级环境变量）

 每个用户都可使用该文件输入专用于自己使用的shell信息,当用户登录时,该文件仅仅执行一次!


```
