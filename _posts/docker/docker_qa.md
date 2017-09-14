- sh: 1: ./bin/start.sh: Permission denied

RUN ["chmod", "+x", "/usr/src/app/bin/start.sh"]


- ERROR: client and server don't have same version (client : 1.19, server: 1.18)
1、echo 'export COMPOSE_API_VERSION=1.18' >> ~/.bash_profile
2、升级docker 版本


- 各种奇葩问题 不知道原因

1、docker-compose stop ; docker-compose rm ; docker-compose  up -d 
2、重启主机 reboot
3、修改镜像的版本 ，重启
4、升级docker 版本




- Error response from daemon: Get https://docker.umiit.cn:5043/v1/users/: x509: certificate is valid for umiit, not docker.umiit.cn

创建或修改 /etc/docker/daemon.json 

```
{
    "registry-mirrors": [
        "http://58f8b602.m.daocloud.io"
    ],
    "insecure-registries": ["docker.umiit.cn:5043"]   
}
```

- "getsockopt: connection refused" when execute "docker 

vim /etc/hosts  写错了


- no basic auth credentials

pom.xml 中的 docker plugin ,没有正确的配置 serverId,serverId是maven的settings中配置的。

image: docker.umiit.cn:5043/maven_docker:latest
