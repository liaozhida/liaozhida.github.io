## using Compose with Swarm

Docker Compose 和 Docker Swarm 高度集成，意味着你可以在swarm集群中使用 Compose应用程序，就好像在一部docker主机上一样。

实际的集成程度，取决于你的Compose风格版本。参见《如何正确的编写docker-compose》

1. 如果你使用的是风格1的links,你的应用程序能正常运行，但swarm会在一个主机上运行所有的容器，因为在旧的网络系统中，链接的两个容器不能在不同的主机中。

2. 如果使用的是风格2，不会有任何的不同。

- 关于限制会在接下来的段落中描述
- 只要在swarm中配置使用overlay网络，或者使用了支持多主机网络的驱动

Read the Getting started with multi-host networking to see how to set up a Swarm cluster with Docker Machine and the overlay driver. Once you’ve got it running, deploying your app to it should be as simple as:

$ eval "$(docker-machine env --swarm <name of swarm master machine>)"
$ docker-compose up



[using Compose with Swarm](https://docs.docker.com/v1.10/compose/swarm/)	