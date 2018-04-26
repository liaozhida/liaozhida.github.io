MySQL慢日志查询.md



```
wget https://www.percona.com/downloads/percona-toolkit/3.0.7/source/tarball/percona-toolkit-3.0.7.tar.gz

perl -MCPAN -e "install DBI" $ perl -MCPAN -e "install DBD::mysql"

perl Makefile.PL

make 

make install
```



[linux下开启mysql慢查询，分析查询语句](http://blog.51yip.com/mysql/972.html)