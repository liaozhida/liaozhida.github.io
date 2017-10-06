---
layout:     post
title:      "GPG error repo.mysql.com jessie InRelease"
date:       2015-02-02 12:00:03
author:     "zhida"
header-img: "img/post-bg-unix-linux.jpg"
tags:
    - linux
    - mysql
    - 数据库相关
---


# docker linux W: GPG error: http://repo.mysql.com jessie InRelease: The following signatures were invalid.md

```
sudo apt-key adv --keyserver pgp.mit.edu --recv-keys A4A9406876FCBD3C456770C88C718D3B5072E1F5
```

or


```
Workaround: (run as root)

apt-key del A4A9406876FCBD3C456770C88C718D3B5072E1F5 # Delete the old key
export GNUPGHOME=$(mktemp -d) # This just sets it up so the key isn't added to your actual user
gpg --keyserver ha.pool.sks-keyservers.net --recv-keys A4A9406876FCBD3C456770C88C718D3B5072E1F5 # Download the new one
gpg --export A4A9406876FCBD3C456770C88C718D3B5072E1F5 /etc/apt/trusted.gpg.d/mysql.gpg # Add it to the list of apt keys
apt-key list # This should now show the updated key

```
无效 ，继续执行
```
sudo apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 5072E1F5
```
无效，继续执行
```
sudo apt-key adv --keyserver pgp.mit.edu --recv-keys 5072E1F5
```


## 参考链接
[APT GPG Key Expired](https://bugs.mysql.com/bug.php?id=85029)