mysql 知识点.md

- [怎么查看和修改 MySQL 的最大连接数？](http://blog.csdn.net/chengjiangbo/article/details/11898019)

- [mysql 慢查询分析工具：pt-query-digest 在mac 上的安装使用](http://www.itboth.com/d/fqINru/pt-query-mac-mysql)

- [linux下开启mysql慢查询，分析查询语句](http://blog.51yip.com/mysql/972.html)

- 查看配置文件 

```
root@bb6a149f4aa3:/# which mysqld
/usr/sbin/mysqld

root@bb6a149f4aa3:/# /usr/sbin/mysqld --verbose --help | grep -A 1 'Default options'
2018-03-14 10:59:07 0 [Note] /usr/sbin/mysqld (mysqld 5.6.36) starting as process 3395 ...
2018-03-14 10:59:07 3395 [Note] Plugin 'FEDERATED' is disabled.
Default options are read from the following files in the given order:
/etc/my.cnf /etc/mysql/my.cnf ~/.my.cnf
2018-03-14 10:59:07 3395 [Note] Binlog end
2018-03-14 10:59:07 3395 [Note] Shutting down plugin 'MyISAM'
2018-03-14 10:59:07 3395 [Note] Shutting down plugin 'CSV'

OR 


```
