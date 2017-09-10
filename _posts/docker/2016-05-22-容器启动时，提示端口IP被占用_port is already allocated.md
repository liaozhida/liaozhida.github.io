容器启动时，提示端口IP被占用_Cannot start containers: port is already allocated.md


** reproduction **

发现其中一个docker mongo 容器有问题， docker stop mongo , docker rm mongo ,然后重新启动 docker start mongo , 提示：annot start containers: port is already allocated


** Solution **

尝试使用 docker kill & restart 

docker ps -a , 找出contanier id xxxx

进入 /var/lib/docker/containers/xxxx

```
[root testServer ]$  ls -al
total 52
drwx------  4 root root  4096 Aug 28 18:30 .
drwxr-xr-x 15 root root  4096 Aug 28 17:01 ..
-rw-r-----  1 root root 12643 Aug 29 03:40 1d3dbd5ac708b9330a1fde131ba1af01c5cb698045f51a46eaf0ed450d9dd20c-json.log
drwx------  2 root root  4096 Aug 28 11:54 checkpoints
-rw-r--r--  1 root root  3844 Aug 28 18:30 config.v2.json
-rw-r--r--  1 root root  1350 Aug 28 18:30 hostconfig.json
-rw-r--r--  1 root root    13 Aug 28 18:30 hostname
-rw-r--r--  1 root root   230 Aug 28 18:30 hosts
-rw-r--r--  1 root root   237 Aug 28 18:30 resolv.conf
-rw-r--r--  1 root root    71 Aug 28 18:30 resolv.conf.hash
drwxrwxrwt  2 root root    40 Aug 28 18:30 shm
```

这个目录下面都是一些该容器的配置信息,编辑 hostconfig.json

```
{"Binds":["/etc/localtime:/etc/localtime:ro","/etc/timezone:/etc/timezone:ro","/mnt/docker-data/logstash/y-activity:/usr/src/app/logs:rw"],"ContainerIDFile":"","LogConfig":{"Type":"json-file","Config":{}},"NetworkMode":"default","PortBindings":{"3909/tcp":[{"HostIp":"10.170.48.177","HostPort":"3909"}]},"RestartPolicy":{"Name":"","MaximumRetryCount":0},"AutoRemove":false,"VolumeDriver":"","VolumesFrom":[],"CapAdd":null,"CapDrop":null,"Dns":[],"DnsOptions":[],"DnsSearch":[],"ExtraHosts":null,"GroupAdd":null,"IpcMode":"","Cgroup":"","Links":["common_nginx2_1:nginxProxy"],"OomScoreAdj":0,"PidMode":"","Privileged":false,"PublishAllPorts":false,"ReadonlyRootfs":false,"SecurityOpt":null,"UTSMode":"","UsernsMode":"","ShmSize":67108864,"Runtime":"runc","ConsoleSize":[0,0],"Isolation":"","CpuShares":0,"Memory":0,"NanoCpus":0,"CgroupParent":"","BlkioWeight":0,"BlkioWeightDevice":null,"BlkioDeviceReadBps":null,"BlkioDeviceWriteBps":null,"BlkioDeviceReadIOps":null,"BlkioDeviceWriteIOps":null,"CpuPeriod":0,"CpuQuota":0,"CpuRealtimePeriod":0,"CpuRealtimeRuntime":0,"CpusetCpus":"","CpusetMems":"","Devices":null,"DeviceCgroupRules":null,"DiskQuota":0,"KernelMemory":0,"MemoryReservation":0,"MemorySwap":0,"MemorySwappiness":-1,"OomKillDisable":false,"PidsLimit":0,"Ulimits":null,"CpuCount":0,"CpuPercent":0,"IOMaximumIOps":0,"IOMaximumBandwidth":0}
```

删除相应的IP和端口号，然后重新 docker start mongo

如果最后还不能解决，只有一个办法，service docker stop & start  ,问题解决

[https://github.com/moby/moby/issues/20486](https://github.com/moby/moby/issues/20486)