# docker-compose 限制内存 CPU大小.md

#### docker-compose 3

```
version: "3"
services:
  node:
    image: USER/You-Pre-Build-Image
    environment:
      - VIRTUAL_HOST=localhost
    volumes:
      - logs:/app/out/
    command: ["npm","start"]
    cap_drop:
      - NET_ADMIN
      - SYS_ADMIN
    deploy:
      resources:
        limits:
          cpus: '0.001'
          memory: 50M
        reservations:
          cpus: '0.0001'
          memory: 20M

volumes:
  - logs

networks:
  default:
    driver: overlay
```


####  docker-compose 1


```
repository:
  image: myregistry/my_nginx_image
  mem_limit: 60m
  volumes:
    - /etc/localtime:/etc/localtime
  ports:
    - "80:80"

```
mem_limit" & "cpu_shares" 


### 参考网站
[Limit a container's resources](https://docs.docker.com/engine/admin/resource_constraints/)
[Resource management in Docker](https://goldmann.pl/blog/2014/09/11/resource-management-in-docker/#_example_managing_the_memory_shares_of_a_container)

