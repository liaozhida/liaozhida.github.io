nginx动态访问.md

vi blockips.conf

```
allow 58.250.169.6;
allow 180.150.176.46;
allow 123.59.115.118;
deny all;
```

vi nginx.conf
```
include /etc/nginx/conf.d/blockips.conf;
```

vi docker-compose.yml 
```
nginx:
  restart: always
  image: jwilder/nginx-proxy:latest
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - /etc/localtime:/etc/localtime:ro
    - /root/docker/common/nginx_conf:/etc/nginx/conf.d
    - /etc/timezone:/etc/timezone:ro
    - /var/run/docker.sock:/tmp/docker.sock:ro
```

jwilder/nginx-proxy:latest 会自动加载conf.d下面的所有配置文件


### Custom Nginx Configuration

If you need to configure Nginx beyond what is possible using environment variables, you can provide custom configuration files on either a proxy-wide or per-VIRTUAL_HOST basis.

Replacing default proxy settings

If you want to replace the default proxy settings for the nginx container, add a configuration file at /etc/nginx/proxy.conf. A file with the default settings would look like this:

```
# HTTP 1.1 support
proxy_http_version 1.1;
proxy_buffering off;
proxy_set_header Host $http_host;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $proxy_connection;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $proxy_x_forwarded_proto;
proxy_set_header X-Forwarded-Ssl $proxy_x_forwarded_ssl;
proxy_set_header X-Forwarded-Port $proxy_x_forwarded_port;

# Mitigate httpoxy attack (see README for details)
proxy_set_header Proxy "";
```

`NOTE`: If you provide this file it will replace the defaults; you may want to check the .tmpl file to make sure you have all of the needed options.