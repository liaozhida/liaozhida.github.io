#### 官网

https://github.com/burnettk/delete-docker-registry-image

#### 安装

```
curl https://raw.githubusercontent.com/burnettk/delete-docker-registry-image/master/delete_docker_registry_image.py | sudo tee /usr/local/bin/delete_docker_registry_image >/dev/null
sudo chmod a+x /usr/local/bin/delete_docker_registry_image
```


#### 运行

```
export REGISTRY_DATA_DIR=镜像存放地址(查找docker-compose.yml)
```

##### 逻辑删除

```
delete_docker_registry_image --image testrepo/awesomeimage --dry-run
```

##### 物理数据删除

```
delete_docker_registry_image --image testrepo/awesomeimage
```

##### 删除指定标签

```
delete_docker_registry_image --image testrepo/awesomeimage:supertag
```

其他用法请参照官网


export REGISTRY_DATA_DIR=/root/docker-data/registry/data/docker/registry/v2

delete_docker_registry_image --image docker.umiit.cn:5043/v3/mq-email --dry-run
