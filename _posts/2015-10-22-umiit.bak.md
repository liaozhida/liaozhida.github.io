umiit.bak.md

```
/data/docker-data/jenkins/workspace/hlpays(common)/app/docker-compose.yml

nginx:
  image: nginx:1.9
  ports:
    - "5043:443"
  links:
    - registry:registry
  volumes:
    - /root/docker-data/registry/auth:/etc/nginx/conf.d
registry:
  restart: always
  image: registry:2.2.0
  ports:
    - "127.0.0.1:5000:5000"
  environment:
    REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY: /var/lib/registry
  volumes:
    - /root/docker-data/registry/data:/var/lib/registr
```


```
/data/docker-data/jenkins/workspace/hlpays(common)/common/docker-compose.yml

logstash:
  image: logstash:latest
  links:
    - elasticsearch:elasticsearch
    - redis:redis
  command: logstash -f /config-dir/logstash.conf
  volumes:
    - ./dockerfiles/logstash:/config-dir
kibana:
  image: kibana:latest
  links:
    - elasticsearch:elasticsearch
  ports:
    - "127.0.0.1:5601:5601"
  volumes:
    - /etc/localtime:/etc/localtime:ro
    - /etc/timezone:/etc/timezone:ro
  environment:
    VIRTUAL_HOST: log.umiit.cn
elasticsearch:
  image: elasticsearch:latest
  command: -Des.network.host=0.0.0.0
  volumes:
    - /root/docker-data/elasticsearch/data:/usr/share/elasticsearch/data
redis:
  image: redis:latest
  ports:
    - "6379:6379"
  volumes:
    - ./dockerfiles/redis.conf:/usr/local/etc/redis/redis.conf
  command: redis-server /usr/local/etc/redis/redis.conf
```