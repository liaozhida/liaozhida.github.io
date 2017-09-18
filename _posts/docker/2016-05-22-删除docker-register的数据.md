---
layout:     post
title:      "删除docker-register的镜像& none无效镜像讲解"
subtitle:   "不同类型的 none 镜像以及物理删除"
date:       2017-09-12 12:00:00
author:     "zhida.liao"
header-img: "img/post-bg-2015.jpg"
tags:
    - docker
---
  
## 背景介绍

在服务器上搭建了docker registry,所有的构建镜像都会集中在一个服务器上，久而久之硬盘就被塞满了。本文会着重介绍两种清理方式。一是`<none>`标签的镜像，二是删除docker物理镜像。


#### docker`<none>`镜像

##### 有效的 none 镜像

为了理解 `<none>` 镜像，我们先要理解 Docker镜像系统的工作机制，以及 layers是如何组织起来的。

当我拉取一个stresser镜像的时候，运行 `docker images -a`命令，会发现我凭空多出来一个< none>:< none> 镜像。

```
➜   docker images -a
REPOSITORY                TAG                 IMAGE ID            CREATED             SIZE
stresser                  latest              68ee9b96793e        9 days ago          242MB
<none>                    <none>              dbcff8952263        9 days ago          242MB
```

当我要删除这个< none>镜像的时候，执行下面的命令，会提示失败，我要删除stresser镜像才能顺带把`<none>`镜像删除。

```
➜   docker rmi dbcff8952263
Error response from daemon: conflict: unable to delete dbcff8952263 (cannot be forced) - image has dependent child images

➜   docker rmi 68ee9b96793e
Untagged: stresser:latest
Deleted: sha256:68ee9b96793e0a3b3a77ec713f1bf4eb19446bd13fb933557dc401e452ca04c4
Deleted: sha256:dbcff895226371eba2640c178414f5828aa5e6f417978b63ffa490d3865dc79a
Deleted: sha256:875a0b6d28d1f52fc980a0948055d3ec3a38158ff7aa6a1a2c19c4243b96a57a

➜   docker rmi dbcff8952263
Error response from daemon: No such image: dbcff8952263:latest
```


`<none>:<none> 镜像`是干嘛的？我们先看看Docker文件系统的组成，docker镜像是由很多 layers组成的，每个 layer之间有父子关系，所有的docker文件系统层默认都存储在`/var/lib/docker/graph`目录下，docker称之为图层数据库，在这个例子中 stresser 由两层(layer)组成，我们可以在`/var/lib/docker/graph`目录下找到层。

当我们pull stresser镜像的时候，最先下载的是 dbcff8952263 < none>父层，接下来才会下载stresser:latest,stresser由两层组成。
我们可以进入 cat /car/lib/docker/graph/${containerId}/json ,查看镜像的元数据来了解详细信息(下面样例是其他的容器信息)

```
{"id":"37dd4150474449629e8a7b576eed26cb8583d2fe5a3edf10fd84323dfd538678","parent":"5cf74bcb1bde2e2249824a682f45235954543a5d57081db22c96402342db49e9","created":"2017-04-06T16:28:35.51523979Z","container_config":{"Hostname":"","Domainname":"","User":"","Memory":0,"MemorySwap":0,"CpuShares":0,"Cpuset":"","AttachStdin":false,"AttachStdout":false,"AttachStderr":false,"PortSpecs":null,"ExposedPorts":null,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":null,"Cmd":["/bin/sh -c set -e; \u0009NGINX_GPGKEY=573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62; \u0009found=''; \u0009for server in \u0009\u0009ha.pool.sks-keyservers.net \u0009\u0009hkp://keyserver.ubuntu.com:80 \u0009\u0009hkp://p80.pool.sks-keyservers.net:80 \u0009\u0009pgp.mit.edu \u0009; do \u0009\u0009echo \"Fetching GPG key $NGINX_GPGKEY from $server\"; \u0009\u0009apt-key adv --keyserver \"$server\" --keyserver-options timeout=10 --recv-keys \"$NGINX_GPGKEY\" \u0026\u0026 found=yes \u0026\u0026 break; \u0009done; \u0009test -z \"$found\" \u0026\u0026 echo \u003e\u00262 \"error: failed to fetch GPG key $NGINX_GPGKEY\" \u0026\u0026 exit 1; \u0009exit 0"],"Image":"","Volumes":null,"WorkingDir":"","Entrypoint":null,"NetworkDisabled":false,"MacAddress":"","OnBuild":null,"Labels":null},"author":"NGINX Docker Maintainers \"docker-maint@nginx.com\"","Size":4901}
```

最后做一个总结：<none>:<none>镜像是一种中间镜像，我们可以使用`docker images -a`来看到，他们不会造成硬盘空间占用的问题（因为这是镜像的父层，必须存在的），但是会给我们的判断带来迷惑。


##### 无效的 none 镜像

另一种类型的 < none>:< none> 镜像是dangling images ，这种类型会造成磁盘空间占用问题。

像Java和Golang这种编程语言都有一个内存区，这个内存区不会关联任何的代码。这些语言的垃圾回收系统优先回收这块区域的空间，将他返回给堆内存，所以这块内存区对于之后的内存分配是有用的

docker的`悬挂(dangling)文件系统`与上面的原理类似，他是没有被使用到的并且不会关联任何镜像，因此我们需要一种机制去清理这些悬空镜像。

我们在上文已经提到了有效的< none>镜像，他们是一种中间层，那无效的< none>镜像又是怎么出现的？这些 dangling镜像主要是我们触发 `docker build` 和 `docker pull`命令产生的。

用一个例子来讲解：

假设我们要构建一个新的镜像，Dockerfile 文件如下

```
FORM Ubuntu:latest
RUN echo 'hello world'
```

当我们构建 `docker build -t hello-world ./ ` 的时候，会生成一个新的镜像。

可是过了一个月之后，Ubuntu发布了新的镜像，这个时候我们再次构建一个 hello world镜像，会依赖于最新的 Ubuntu

问题来了，我们引用旧的Ubuntu的hello-world镜像，这个时候就会成为没有标签的 dangling镜像！使用下面的命令可以清理

```
docker rmi $(docker images -f "dangling=true" -q)
```

docker没有自动垃圾回收处理机制，未来可能会有这方面的改进，但是目前我们只能这样手动清理（写个脚本就好）。



#### 删除本地硬盘的镜像

当我们registry服务器存在很多tag标签的镜像，但是硬盘空间不够用的时候，我们会希望删除存量的镜像给服务器腾出空间，registry自带了API接口删除镜像，但是即使我们调用了，他也只是逻辑层面的删除，软删除（soft delete），只是把二进制和镜像的关系解除罢了，实际上镜像一直存在我们的硬盘中，我们需要一种方式彻底物理删除存量空间。网上有第三方的解决方案：`delete-docker-registry-image`,接下来列出操作步骤，操作之前先把 registry服务停掉。

**安装:**

```
curl https://raw.githubusercontent.com/burnettk/delete-docker-registry-image/master/delete_docker_registry_image.py | sudo tee /usr/local/bin/delete_docker_registry_image >/dev/null
sudo chmod a+x /usr/local/bin/delete_docker_registry_image
```

**设置环境变量：数据存放地址:**

我服务器上registry的配置如下：

```
  volumes:
    - /root/docker-data/registry/data:/var/lib/registry
```

```
root@iZ94ft8hgzqZ:~/docker-data/registry/data/docker/registry/v2/repositories# ls -al
total 108
drwxr-xr-x 27 root root 4096 Aug 21 18:29 .
drwxr-xr-x  4 root root 4096 Oct 30  2015 ..
drwxr-xr-x  5 root root 4096 Mar 27  2016 example
drwxr-xr-x  5 root root 4096 Mar 20 19:25 gitlab_ansible
drwxr-xr-x  5 root root 4096 Mar 22  2016 hlpays-job
drwxr-xr-x  5 root root 4096 Jan 26  2016 hlpays-oa
drwxr-xr-x  5 root root 4096 Mar 24  2016 hlpays-portal
drwxr-xr-x  5 root root 4096 Mar 27 18:32 ifex-crm
```

```
export REGISTRY_DATA_DIR=/root/docker-data/registry/data/docker/registry/v2
```

**逻辑删除:**

delete_docker_registry_image --image tickets --dry-run ; 只是逻辑删除，没什么用，演示一下而已。。。
```
root@iZ94ft8hgzqZ:~/docker-data/registry/data/docker/registry/v2/repositories# delete_docker_registry_image --image tickets --dry-run


INFO     [2017-09-13 18:21:04,505]  DRY_RUN: would have deleted /root/docker-data/registry/data/docker/registry/v2/blobs/sha256/27/27dedd9200ff607e76eb9d0e10beb103f53551e4ed39829d767cfbc208b79581
INFO     [2017-09-13 18:21:04,506]  DRY_RUN: would have deleted /root/docker-data/registry/data/docker/registry/v2/blobs/sha256/1b/1b2aade332a7133b1a03cae7695a3dcf9413dd017ff41f35a1bb1506becbacf3

```

**物理数据删除:**

删除物理内存，能看到硬盘空间已经空出来了。

```
delete_docker_registry_image --image tickets

df -h    
```


**删除指定标签:**

```
delete_docker_registry_image --image testrepo/awesomeimage:supertag
```

其他用法请参照官网

`转载请注明出处 作者:zhida  来源:`[paraller's blog](http://www.paraller.com)


## 参考网站

[What are Docker <none>:<none> images](https://www.projectatomic.io/blog/2015/07/what-are-docker-none-none-images/)

[delete-docker-registry-image](https://github.com/burnettk/delete-docker-registry-image)

[删除Docker Registry里的镜像怎么那么难](http://qinghua.github.io/docker-registry-delete/)



