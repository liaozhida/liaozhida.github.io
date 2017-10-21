---
layout:     post
title:      "lib_mysqludf_json 64位安装以及使用"
date:       2015-02-01 12:00:00
author:     "zhida.liao"
header-img: "img/post-bg-2015.jpg"
tags:
    - mysql
    - 数据库相关
---


下载配置:给出32位的下载地址: http://mysql-udf-http.googlecode.com/files/lib_mysqludf_json-i386.tar.gz

但是现在大家的服务器都基本是64位的系统，使用32位系统在执行创建函数的操作`create function lib_mysqludf_json_info`会报错。
```
returns string soname 'lib_mysqludf_json.so'; 的时候会报错：Can't open shared library 'lib_mysqludf_json.so' (errno: 22 /usr/lib64/mysql/plugin/lib_mysqludf_json.so: wrong ELF class: ELFCLASS32)
```

这个问题是使用版本的位数不一致造成的
谷歌找不到lib_mysqludf_json 64的压缩包，找了很久在一个网站上面看到一个大神的回复：just compile it yourself

```
gcc $(/your/mysql/bin/path/mysql_config --cflags) -shared -fPIC -o lib_mysqludf_json.so lib_mysqludf_json.c
```

根据提示进行了一番尝试，首先，我们要去下载lib_mysqludf_json的源码包，一般网上下载的压缩包里面只有lib_mysqludf_json.so 文件，如果要自己编译肯定是不够的，这个时候大家可以谷歌github上面的源代码，地址给出：https://github.com/mysqludf/lib_mysqludf_json 失效了自己搜索一下就有了

下载压缩包，解压，进入解压的文件夹执行:

```
gcc $(/your/mysql/bin/path/mysql_config --cflags) -shared -fPIC -o lib_mysqludf_json.so lib_mysqludf_json.c 
```

得到的lib_mysqludf_json.so就是64位的，复制 cp 到mysql/pulgin/ 即可，

简单使用
1. 第一步当然是创建函数：如下
```
create function lib_mysqludf_json_info returns string soname 'lib_mysqludf_json.so';
create function json_array returns string soname 'lib_mysqludf_json.so';
create function json_members returns string soname 'lib_mysqludf_json.so';
create function json_object returns string soname 'lib_mysqludf_json.so';
create function json_values returns string soname 'lib_mysqludf_json.so'; 
```

2. 写在函数的语句：drop function function_Name;

3. 查看是否安装成功(上面四行是mysql-http-udf的)
```
mysql>  select * from mysql.func;
+------------------------+-----+----------------------+----------+
| name                   | ret | dl                   | type     |
+------------------------+-----+----------------------+----------+
| http_get               |   0 | mysql-udf-http.so    | function |
| http_post              |   0 | mysql-udf-http.so    | function |
| http_put               |   0 | mysql-udf-http.so    | function |
| http_delete            |   0 | mysql-udf-http.so    | function |
| lib_mysqludf_json_info |   0 | lib_mysqludf_json.so | function |
| json_array             |   0 | lib_mysqludf_json.so | function |
| json_members           |   0 | lib_mysqludf_json.so | function |
| json_object            |   0 | lib_mysqludf_json.so | function |
| json_values            |   0 | lib_mysqludf_json.so | function |
+------------------------+-----+----------------------+----------+
```

4. 接下来用已有的user表进行json_array函数的测试，其他函数类似，就不给出测试用例了，关于lib_mysqludf_json的详细用法可以查看文末给出的参考博文
```
mysql> select json_array(name) from user;
+------------------+
| json_array(name) |
+------------------+
| ["liao"]         |
| ["zhi"]          |
| ["da"]           |
+------------------+
```



对于lib_mysqludf_json的实际项目使用可以参考《利用mysql-http-udf同步数据到Solr服务器》这篇文章


## 参考博客
http://www.ttlsa.com/mysql/mysqludf_json-relational-data-to-json-code/

`转载请注明出处  来源:`[paraller's blog](http://www.paraller.com)





