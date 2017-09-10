docker 加速器的配置/内网registry配置

加速器的配置目前是直接使用 Dao clound的服务，提供了官方的镜像地址
类似于： http://58f8b602.m.daocloud.io

docker for Mac:
直接在Advanced中配置镜像地址


Linux : 
1.12 版本及以上

创建或修改 /etc/docker/daemon.json
```
{
    "registry-mirrors": [
        "http://58f8b602.m.daocloud.io"
    ],
    "insecure-registries": ["docker.umiit.cn:5043"]  // 亲测这个不能再这里配置，会启动失败 ,可以在docker配置文件中指定
}


{
    "registry-mirrors": [
        "http://58f8b602.m.daocloud.io"
    ],
    "insecure-registries": ["docker.umiit.cn:5043"]   
}

docker login -u 'umiit' -p 'umi1234'   docker.umiit.cn:5043


```

{
    "registry-mirrors": [
        "http://58f8b602.m.daocloud.io"
    ],
}


1.12 版本及以下

```
vim /etc/default/docker 

DOCKER_OPTS="$DOCKER_OPTS --insecure-registry=docker.yourdomain.cn:5043 --registry-mirror='http://58f8b602.m.daocloud.io' "

```