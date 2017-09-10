## Docker Machine 

** 用途 **

- 在Mac和Windows系统上安装和运行Docker
- 对多个远程的Docker主机提供支持和管理
- 支持Swarm集群


### 什么是 Docker Machine?

Docker Machine 是一个工具， 将 Docker Engine 安装在虚拟主机中 , 可以使用 docker-machine 命令管理虚拟主机. 你可以在Mac和Windows中使用 machine创建docker主机，或者在公司内网，数据中心，或者云服务器上。

使用 docker-machine 命令, 你可以 start, inspect, stop, and restart 一个主机, 升级 Docker client 和 daemon, 配置clinet以便和daemon进行通讯

Machine CLI 在running, managed 主机,你可以在主机上直接使用docker命令，举个例子，执行`docker-machine env default`可以查看主机上名字为defalut的主机，你还可以执行 docker ps, docker run hello-world, 等等其他命令。

Docker v1.12版本之前，在Mac和Windows上运行docker的唯一办法就是借助Machine,v1.12及以上版本，你可以像使用原生应用程序一样，建议使用最新版本，安装好Docker之后，会内置安装好Docker Machine和Docker Compose。 

### 为什么要使用 Docker Machine

使用它的两种场景分别是

- 在Mac和Windows上运行旧版本的docker
- 想在远程服务器上运行Docker主机

Docker Engine 可以运行在原生的 Linux systems.想要在Linux上尝试运行docker，只需要 download and install Docker Engine. 但是,  你如果想在内网、云服务器或者本地中运行多个docker主机,  你需要 Docker Machine.

无论你使用的系统是什么，你都可以安装docker machine然后使用`docker-machine`命令去帮助你创建和管理大量的docker主机， machine会自动创建 虚拟主机，安装docker engine在里面，配置一个docker client， 每一个machine都是由docker 主机和配置好的client组成的 

### Docker Engine 和 Docker Machine 的区别

当我们说 Docker 的时候，说的是**Docker engine**，他是一个client-server应用程序，是由 Docker daemon 和 client组成的，client是一个提供了很多REST API ，和daemon交流的接口。Docker Engine 从 CLI,接收命令然后执行。 

```
----------------------------------------------
|	client:Docker CLI				         |
|											 |
|	--------------------------------- 		 |	
|	|  REST API					  	|		 |	
|   |   -----------------------     |		 |	
|	| 	|server:Docker daemon |	  	|	     |
|   |   ----------------------- 	|		 |
|	|								|  		 |
|	--------------------------------- 		 |
|											 |	
----------------------------------------------
```

**Docker Machine**是一个工具，用来运行和管理虚拟化的主机，它有自己的命令，你可以创建一或多个虚拟系统，用来安装docker engine，这些虚拟系统可以是本地的，也可以是远程的，这些虚拟化的主机将会被machine管理起来。

```
---------------------------------------------------------
|                       Docker Machine                  |
|	----------------------------------------------      |
|	|	client:Docker CLI				         |      |
|	|											 |      |
|	|	--------------------------------- 		 |	    |
|	|	|  REST API					  	|		 |	    |
|	|   |   -----------------------     |		 |	    |
|	|	| 	|server:Docker daemon |	  	|	     |      |
|	|   |   ----------------------- 	|		 |      |
|	|	|								|  		 |      |
|	|	--------------------------------- 		 |      |
|	|											 |	    |
|	----------------------------------------------      |
|												        |
---------------------------------------------------------
```

### 安装
参考链接 [Install Docker Machine](https://docs.docker.com/machine/install-machine/)

[Docker Machine command-line reference](https://docs.docker.com/machine/reference/)
[Machine concepts and getting help](https://docs.docker.com/machine/concepts/)
[Daoclound 安装起步](https://get.daocloud.io/#install-docker)