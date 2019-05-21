MYSLQ必学必会.md

## 索引

#### InnoDB的索引类型

InnoDB的索引有两类索引，聚集索引(Clustered Index)与普通索引(Secondary Index)。

###### 两种索引类型的区别

在索引结构中，非叶子节点存储key，叶子节点存储value；

**聚集索引：**，叶子节点存储行记录(row)，包括所有列字段；

画外音：所以，InnoDB索引和记录是存储在一起的，而MyISAM的索引和记录是分开存储的。

**普通索引：**叶子节点存储了PK的值；

###### 普通索引的扫描过程

InnoDB的普通索引，实际上会扫描两遍：

- 由其他字段的普通索引找到PK值；

- 根据PK的聚集索引，找到行记录；


###### 聚集索引分布

InnoDB的每一个表都会有聚集索引：

- 如果表定义了PK，则PK就是聚集索引；

- 如果表没有定义PK，则第一个非空unique列是聚集索引；

- 否则，InnoDB会创建一个隐藏的row-id作为聚集索引；


#### 索引的创建类型

###### UNIQUE唯一索引

不可以出现相同的值，可以有NULL值。

###### INDEX普通索引

允许出现相同的索引内容。

###### PRIMARY KEY主键索引

不允许出现相同的值，且不能为NULL值，一个表只能有一个primary_key索引。

###### fulltext index 全文索引

上述三种索引都是针对列的值发挥作用，但全文索引，可以针对值中的某个单词，比如一篇文章中的某个词，然而并没有什么卵用，因为只有myisam以及英文支持，并且效率让人不敢恭维，但是可以用coreseek和xunsearch等第三方应用来完成这个需求。


--- 

#### 索引的CURD
 
###### ALTER TABLE

适用于表创建完毕之后再添加。

ALTER TABLE 表名 ADD 索引类型 (unique,primary key,fulltext,index)[索引名](字段名)

```
ALTER TABLE `table_name` ADD INDEX `index_name` (`column_list`) -- 索引名，可要可不要；如果不要，当前的索引名就是该字段名。 
ALTER TABLE `table_name` ADD UNIQUE (`column_list`) 
ALTER TABLE `table_name` ADD PRIMARY KEY (`column_list`) 
ALTER TABLE `table_name` ADD FULLTEXT KEY (`column_list`)
```

###### CREATE INDEX

CREATE INDEX可对表增加普通索引或UNIQUE索引。

```
--例：只能添加这两种索引 
CREATE INDEX index_name ON table_name (column_list) 
CREATE UNIQUE INDEX index_name ON table_name (column_list)
```

```
CREATE TABLE `test1` ( 
  `id` smallint(5) UNSIGNED AUTO_INCREMENT NOT NULL, -- 注意，下面创建了主键索引，这里就不用创建了 
  `username` varchar(64) NOT NULL COMMENT '用户名', 
  `nickname` varchar(50) NOT NULL COMMENT '昵称/姓名', 
  `intro` text, 
  PRIMARY KEY (`id`),  
  UNIQUE KEY `unique1` (`username`), -- 索引名称，可要可不要，不要就是和列名一样 
  KEY `index1` (`nickname`), 
  FULLTEXT KEY `intro` (`intro`) 
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COMMENT='后台用户表';
```

###### 索引的删除

```
DROP INDEX `index_name` ON `talbe_name`  
ALTER TABLE `table_name` DROP INDEX `index_name` 
-- 这两句都是等价的,都是删除掉table_name中的索引index_name; 

ALTER TABLE `table_name` DROP PRIMARY KEY -- 删除主键索引，注意主键索引只能用这种方式删除
```


###### 查看索引

```
show index from tablename;	
```

###### 索引的更改

删除重建。

--- 

#### 索引的选择

- 维度高的列创建索引: 数据列中不重复值出现的个数，这个数量越高，维度就越高。
- 对 where,on,group by,order by 中出现的列使用索引
- 对较小的数据列使用索引，这样会使索引文件更小，同时内存中也可以装载更多的索引键。
- 为较长的字符串使用前缀索引。
- 不要过多创建索引，除了增加额外的磁盘空间外，对于DML操作的速度影响很大，因为其每增删改一次就得从新建立索引。
- 使用组合索引，可以减少文件索引大小，在使用时速度要优于多个单列索引。


#### 索引技巧

组合索引与前缀索引


###### 组合索引

1： 单个索引

MySQL先根据索引返回一批数据，然后在服务层根据 where 条件进行筛选

2： 建立多个 单索引

MySQL 只能用到其中的那个它认为似乎是最有效率的单列索引，其他是用不到的，也就是说还是一个全表扫描的过程。

3：  组合索引

建立索引：vc_Name,vc_City,i_Age，相当于分别建立了：

- vc_Name,vc_City,i_Age
- vc_Name,vc_City
- vc_Name

mysql 组合索引 “最左前缀” 的结果， 简单的理解就是只从最左面的开始组合


###### 前缀索引

如果索引列长度过长，这种列索引时将会产生很大的索引文件，不便于操作，可以使用前缀索引方式进行索引前缀索引应该控制在一个合适的点，控制在0.31黄金值即可（大于这个值就可以创建）。

`SELECT COUNT(DISTINCT(LEFT(`title`,10)))/COUNT(*) FROM Arctic;` — 这个值大于0.31就可以创建前缀索引，Distinct去重复 

`ALTER TABLE `user` ADD INDEX `uname`(title(10));` — 增加前缀索引SQL，将人名的索引建立在10，这样可以减少索引文件大小，加快索引查询速度。

#### 索引不生效的场景

- 函数运算
- 全匹配模糊查询
- 正则表达式不使用索引，这应该很好理解，所以为什么在SQL中很难看到regexp关键字的原因 
- 字符串与数字比较 
- or条件，就是要求使用的所有字段，都必须建立索引，否则无一生效
- in 不会让索引失效

```
SELECT `sname` FROM `stu` WHERE `age`+10=30;-- 不会使用索引，因为所有索引列参与了计算 

SELECT `sname` FROM `stu` WHERE LEFT(`date`,4) <1990; -- 不会使用索引，因为使用了函数运算，原理与上面相同 

SELECT * FROM `houdunwang` WHERE `uname` LIKE'后盾%' -- 走索引 

SELECT * FROM `houdunwang` WHERE `uname` LIKE "%后盾%" -- 不走索引 


-- 字符串与数字比较不使用索引; 
CREATE TABLE `a` (`a` char(10)); 
EXPLAIN SELECT * FROM `a` WHERE `a`="1" -- 走索引 
EXPLAIN SELECT * FROM `a` WHERE `a`=1 -- 不走索引 

select * from dept where dname='xxx' or loc='xx' or deptno=45 --如果条件中有or，即使其中有条件带索引也不会使用。换言之，就是要求使用的所有字段，都必须建立索引，我们建议大家尽量避免使用or 关键字 

```


#### 索引的弊端

- 不要盲目的创建索引，只为查询操作频繁的列创建索引，创建索引会使查询操作变得更加快速，但是会降低**增加、删除、更新**操作的速度，因为执行这些操作的同时会对索引文件进行重新排序或更新。

- 但是，在互联网应用中，查询的语句远远大于DML的语句，甚至可以占到 80% - 90%，所以也不要太在意，只是在大数据导入时，可以先删除索引，再批量插入数据，最后再添加索引.


#### Explain 

mysql在执行一条查询之前，会对发出的每条SQL进行分析，决定是否使用索引或全表扫描

[MySQL EXPLAIN详解](https://cloud.tencent.com/developer/article/1371033)

###### select_type

- SIMPLE: 简单查询，标识查询不包含任何子查询或者UNION语句
- PRIMARY: 复杂查询的外层查询，一般都在第一行，代表这是一个复杂查询的最外层查询
- SUBQUERY: 复杂查询的子查询，指不在FROM子句中的那些
- DEPENDENT SUBQUERY: 复杂查询中，依赖外部查询的子查询
- DERIVED: 在FROM子句中的子查询

###### type

表示了Mysql究竟采取何种方法来访问数据，通常能够在一定程度上反映查询语句的性能。
可能出现的值有如下这些，性能从最差到最优（5.6版本）：

- ALL：全表扫描，最惨的性能，从数据表中逐行查找数据。除非使用了LIMIT或者在Extra列中有”Using distinct/not exists”字样

- index：全表扫描的进阶版，按索引顺序全表扫描，通常性能和全表扫描没什么区别，除非Extra列中有”Using index”字样，那说明使用了覆盖索引，这种情况下要快于ALL，因为直接扫描索引就能获取数据，而索引通常比表小的多。如果所要查询的列是某个索引的一部分，通常会出现这种查询。

- range：范围扫描，比index强一些，因为它是从索引的某个点开始的，用不着遍历全部索引。一些带有BETWEEN，各种比较符号的语句容易出现这种类型，但是要特别注意IN和OR，这也会显示成range，但是其性能跟index差不多。

- index_subquery：索引替换子查询，如果有这样的语句SELECT * FROM table WHERE value IN(SELECT key_column FROM table where xxx)，IN后面的语句会被索引直接代替，来提高效率。

- const：当查询唯一地匹配一条记录，并且使用主键等于常数或者唯一索引等于某常数作为查询条件时，Mysql会视查询出来的值为常数，这种类型非常快。比如：SELECT * FROM tbl_name WHERE primary_key = 1;

- system：表只有一行记录且为系统表，Mysql官方没有给出出现这个类型的例子

###### possible_keys

查询可能会用到的索引

###### key_len

最长的索引宽度。如果键是NULL，长度就是NULL。在不损失精确性的情况下，长度越短越好。


###### key 

显示查询最终使用到的索引，如果该索引没有出现在possible_key里，那么它可能是一个覆盖索引。

如果显示的是NULL，很遗憾没有任何索引被用到，说明查询的性能可能会很差。

###### ref 

显示哪些列或者常量被用来跟key中显示的索引进行比较，从而获取结果。


###### rows 

显示Mysql引擎认为它要获得结果预计要扫描的行数。这是一个估计值，可能不是很精确。注意这个值不是结果集的行数，还要知道有很多优化手段没能影响这个值，因此可能最终执行时不必读取这么多行记录。

如果有多行结果，将多行的rows相乘可以得到一条完整语句执行预计要扫描的行数。

###### filtered

filtered值只对index和all的扫描有效，比如全局扫描100万条数据，扫描到50万就命中了，也就是 50%

###### Extra


- Using index：代表使用了覆盖索引。
- Using where：代表使用了where条件句中的条件进一步地过滤，如果没有显示这个而且查询类型是ALL或者index，那说明SQL写的很差，需要优化。除非你真的就想要全表扫描。
- Using temporary：代表为了得到结果，Mysql不得不创建一个临时表，将结果放在临时表里，在GROUP BY和ORDER BY使用的时候经常出现这个。
- Using filesort：代表索引不能满足排序的需求，于是一种文件排序算法被使用，至于使用的是哪种算法（一共有3种算法），是在内存还是磁盘上进行排序（结果集比较小的情况下可能在内存中完成排序），这个字段不会告诉你这些信息。




#### 参考
[InnoDB，select为啥会阻塞insert？](https://mp.weixin.qq.com/s/y_f2qrZvZe_F4_HPnwVjOw)


---

## 连接

#### 连接类型

INNER JOIN : 交集

LEFT JOIN: 左集合

RIGHT JOIN: 右集合

FULL JOIN: 并集

UNION:  合并多个select 语句， 列数量、顺序、数据类型  必须一致。

#### 连接原理

- 假定AB两张表， 数据量为 m , n 
- 相对左边的称为驱动表，相对在右侧的为匹配表

###### Nested-Loop Join

1： 常规扫描

A表全表扫描m条数据， 每条数据依次在B表中进行数据库全表查询，一共需要扫描 `m*n` 次

2:  对关联字段增加索引，并且索引为主键

A表全表扫描m条数据， 每条数据依次在B表中进行数据库查询，每次索引查询(如果是主键，理解为常量扫描)， 一共需要扫描 `1+m`次


###### Block Nested-Loop Join

将外层循环的行/结果集存入join buffer, 内层循环的每一行与整个buffer中的记录做比较，从而减少内层循环的次数

举例:
- 外层循环的结果集是100行，使用NLJ 算法需要扫描内部表100次
- 如果使用BNL算法，先把对Outer Loop表(外部表)每次读取的10行记录放到join buffer
- 然后在InnerLoop表(内部表)中直接匹配这10行数据，内存循环就可以一次与这10行进行比较, 这样只需要比较10次


- join_buffer_size变量决定buffer大小。
- 只有在join类型为all, index, range的时候才可以使用join buffer。
- 能够被buffer的每一个join都会分配一个buffer, 也就是说一个query最终可能会使用多个join buffer。
- 第一个nonconst table不会分配join buffer, 即便其扫描类型是all或者index。
- 在join之前就会分配join buffer, 在query执行完毕即释放。
- join buffer中只会保存参与join的列, 并非整个数据行。

--- 

## 引擎

#### InnoDB、MyISAM 区别

###### 关于`count(*)`

知识点： MyISAM 会直接存储总行数， InnoDB 则不会，需要按行扫描。

潜台词是，对于`select count(*) from t;` 如果数据量大，MyISAM会瞬间返回，而InnoDB则会一行行扫描。

只有查询全表的总行数，MyISAM才会直接返回结果，当加了where条件后，两种存储引擎的处理方式类似。


###### 关于事务

MyISAM不支持事务，InnoDB支持事务。

事务是选择InnoDB非常诱人的原因之一，它提供了commit，rollback，崩溃修复等能力，事务也非常耗性能，会影响吞吐量，建议只对一致性要求较高的业务使用复杂事务。

###### 关于外键

知识点：MyISAM不支持外键，InnoDB支持外键。 在数据量大并发量大的情况下，都不应该使用外键，而建议由应用程序保证完整性。


###### 关于行锁与表锁

知识点：MyISAM只支持表锁，InnoDB可以支持行锁。

**分析：**

- MyISAM：执行读写SQL语句时，会对表加锁，所以数据量大，并发量高时，性能会急剧下降。

- InnoDB：细粒度行锁，在数据量大，并发量高时，性能比较优异。


**常见坑：**

- InnoDB的行锁是实现在索引上的，而不是锁在物理行记录上。潜台词是，如果访问没有命中索引，也无法使用行锁，将要退化为表锁。

- 画外音：Oracle的行锁实现机制不同。


**例子：**

t_user(uid, uname, age, sex) innodb;
uid PK
无其他索引

update t_user set age=10 where uid=1;
命中索引，行锁。

update t_user set age=10 where uid != 1;
未命中索引，表锁。

update t_user set age=10 where name='shenjian';
无索引，表锁。

启示：InnoDB务必建好索引，否则锁粒度较大，会影响并发。

#### 参考

[InnoDB，5项最佳实践，知其所以然？](https://mp.weixin.qq.com/s?__biz=MjM5ODYxMDA5OQ==&mid=2651961428&idx=1&sn=31a9eb967941d888fbd4bb2112e9602b&chksm=bd2d0d888a5a849e7ebaa7756a8bc1b3d4e2f493f3a76383fc80f7e9ce7657e4ed2f6c01777d&scene=21#wechat_redirect)


--- 

## 锁

除了粗粒度的划分为  细粒度行锁、表锁 之外

InnoDB可细分为七种锁

(1)共享/排它锁(Shared and Exclusive Locks)
(2)意向锁(Intention Locks)
(3)记录锁(Record Locks)
(4)间隙锁(Gap Locks)
(5)临键锁(Next-key Locks)
(6)插入意向锁(Insert Intention Locks)
(7)自增锁(Auto-inc Locks)


#### 1： 共享/排它锁

简单的锁住太过粗暴，连“读任务”也无法并行，任务执行过程本质上是串行的。

###### 共享锁与排他锁定义：

- 共享锁（Share Locks，记为S锁），读取数据时加S锁

- 排他锁（eXclusive Locks，记为X锁），修改数据时加X锁

###### 共享锁与排他锁的作用

- 共享锁之间不互斥，简记为：只有读读可以并行

- 排他锁与任何锁互斥，简记为：写读，写写不可以并行

可以看到，一旦写数据的任务没有完成，数据是不能被其他任务读取的，这对并发度有较大的影响。

###### 用法：

- 共享锁 ：（Share Locks，记为S锁）: 通过在执行语句后面加上 lock in share mode 就代表对某些资源加上共享锁了

- 排它锁: （eXclusive Locks，记为X锁）: update,insert,delete语句会自动加排它锁


#### 2：记录锁(Record Locks)

记录锁，封锁 索引记录，例如：

`select * from t where id=1 for update;`
 
它会在id=1的索引记录上加锁，以阻止其他事务插入，更新，删除id=1的这一行。


`select * from t where id=1;`

则是快照读(SnapShot Read)，它并不加锁

#### 3：间隙锁(Gap Locks)

间隙锁，它封锁索引记录中的间隔，或者第一条索引记录之前的范围，又或者最后一条索引记录之后的范围。

例子： t(id PK, name KEY, sex, flag);


表中有四条记录：

```
1, shenjian, m, A
3, zhangsan, m, A
5, lisi, m, A
9, wangwu, f, B
```


这个SQL语句

```
select * from t 
    where id between 8 and 15 
    for update;
```


会封锁区间，以阻止其他事务id=10的记录插入。

**画外音**：为什么要阻止id=10的记录插入？

如果能够插入成功，头一个事务执行相同的SQL语句，会发现结果集多出了一条记录，即幻影数据。

间隙锁的主要目的，就是为了防止其他事务在间隔中插入数据，以导致“不可重复读”。

如果把事务的隔离级别降级为读提交(Read Committed, RC)，间隙锁则会自动失效。



#### 4：临键锁(Next-Key Locks)

临键锁，是记录锁与间隙锁的组合，它的封锁范围，既包含索引记录，又包含索引区间。

#### 5： 意向锁

意向锁分为：

意向共享锁(intention shared lock, IS)，它预示着，事务有意向对表中的某些行加共享S锁

意向排它锁(intention exclusive lock, IX)，它预示着，事务有意向对表中的某些行加排它X锁

意向锁协议(intention locking protocol)并不复杂：

事务要获得某些行的S锁，必须先获得表的IS锁

事务要获得某些行的X锁，必须先获得表的IX锁

###### 例子

事务A： 修改一行数据，获取了排它锁。
事务B： 获取数据表的表锁。

过程： 事务A已经持有了排它锁，事务B要先遍历每一行，查看是否有行锁记录，如果有，则阻塞事务B对表锁的获取，效率低下

采用意向锁

过程： 事务A获取排它锁之前，先获取排他意向锁，事务B获取表锁前，判断是否存在排他意向锁，如果有，则阻塞表锁的获取，效率高。

PS ： 申请意向锁的动作是数据库完成的，就是说，事务A申请一行的行锁的时候，数据库会自动先开始申请表的意向锁，不需要我们程序员使用代码来申请。

###### 参考


[InnoDB 的意向锁有什么作用？ - 发条地精的回答 - 知乎](https://www.zhihu.com/question/51513268/answer/127777478)
[InnoDB并发插入，居然使用意向锁？](https://mp.weixin.qq.com/s?__biz=MjM5ODYxMDA5OQ==&mid=2651961461&idx=1&sn=b73293c71d8718256e162be6240797ef&chksm=bd2d0da98a5a84bfe23f0327694dbda2f96677aa91fcfc1c8a5b96c8a6701bccf2995725899a&scene=21#wechat_redirect)

#### 6：插入意向锁

插入意向锁，是间隙锁(Gap Locks)的一种（所以，也是实施在索引上的），它是专门针对insert操作的。

它的玩法是：多个事务，在同一个索引，同一个范围区间插入记录时，如果插入的位置不冲突，不会阻塞彼此。

#### 7：自增锁

自增锁是一种特殊的表级别锁（table-level lock），专门针对事务插入AUTO_INCREMENT类型的列。最简单的情况，如果一个事务正在往表中插入记录，所有其他事务的插入必须等待，以便第一个事务插入的行，是连续的主键值。

InnoDB提供了innodb_autoinc_lock_mode配置，可以调节与改变该锁的模式与行为。

**例子：**

事务A先执行，还未提交：

`insert into t(name) values(xxx);`

事务B后执行：

`insert into t(name) values(ooo);`

 

InnoDB在RR隔离级别下，能解决幻读问题，上面这个案例中：

(1)事务A先执行insert，会得到一条(4, xxx)的记录，由于是自增列，故不用显示指定id为4，InnoDB会自动增长，注意此时事务并未提交；

(2)事务B后执行insert，假设不会被阻塞，那会得到一条(5, ooo)的记录；

(3)事务A继续insert：

`insert into t(name) values(xxoo);` 会得到一条(6, xxoo)的记录。
 
(4)事务A再select：

`select * from t where id>3;`

得到的结果是：
```
4, xxx

6, xxoo
```

画外音：不可能查询到5的记录，再RR的隔离级别下，不可能读取到还未提交事务生成的数据。

对于AUTO_INCREMENT的列，连续插入了两条记录，一条是4，接下来一条变成了6，就像莫名其妙的幻影。

#### 参考
[InnoDB，select为啥会阻塞insert？](https://mp.weixin.qq.com/s/y_f2qrZvZe_F4_HPnwVjOw)

## 并发

通过并发控制保证数据一致性的常见手段有：

- 锁（Locking）
  - 悲观锁
    - 普通锁 
    - 读写锁
  - 乐观锁

- 数据多版本（Multi Versioning）

提高并发的演进思路：

- 普通锁，本质是串行执行

- 读写锁，可以实现读读并发

- 数据多版本，可以实现读写并发

#### 乐观锁

```
SELECT balance,version FROM user WHERE id=1 AND balance>10;
UPDATE user SET balance=balance-10,version=last_version+1 WHERE id=1 AND version=last_version;
```
注意到UPDATE里的last_version为SELECT获取的本次读写的版本号.

不需要数据库事务的支持,SELECT操作和UPDATE操作的时间跨度再大也没有问题.

上述版本号的方法借鉴了Memcached的CAS(Check And Set)冲突检测机制,这是一个乐观锁,能保证高并发下的数据安全.



#### 数据多版本

redo & undo

例如某一事务的事务序号为T1，其对数据X进行修改，设X的原值是5，修改后的值为15，

Undo日志为<T1, X, 5>，
Redo日志为<T1, X, 15>。


- **undo日志用于记录事务开始前的状态，用于事务失败时的回滚操作；**

- **redo日志记录事务执行后的状态，用来恢复未写入data file的已成功事务更新的数据。**

逻辑日志

物理日志


![image][redo]


###### MVCC

InnoDB的内核，会对所有row数据增加三个内部属性：

(1)DB_TRX_ID ，6字节，记录每一行最近一次修改它的事务ID；

(2)DB_ROLL_PTR，7字节，记录指向回滚段undo日志的指针；

(3)DB_ROW_ID，6字节，单调递增的行ID；


InnoDB为何能够做到这么高的并发？

回滚段里的数据，其实是历史数据的快照（snapshot），这些数据是不会被修改，select可以肆无忌惮的并发读取他们。

 

快照读（Snapshot Read），这种一致性不加锁的读（Consistent Nonlocking Read），就是InnoDB并发如此之高的核心原因之一。

 

这里的一致性是指，事务读取到的数据，要么是事务开始前就已经存在的数据（当然，是其他已提交事务产生的），要么是事务自身插入或者修改的数据。

 

什么样的select是快照读？

除非显示加锁，普通的select语句都是快照读，例如：

select * from t where id>2;

 

这里的显示加锁，非快照读是指：

select * from t where id>2 lock in share mode;

select * from t where id>2 for update;




通常是物理日志，记录的是数据页的物理修改，而不是某一行或某几行修改成怎样怎样，它用来恢复提交后的物理数据页(恢复数据页，且只能恢复到最后一次提交的位置)。

 
[InnoDB并发如此高，原因竟然在这？](https://mp.weixin.qq.com/s?__biz=MjM5ODYxMDA5OQ==&mid=2651961444&idx=1&sn=830a93eb74ca484cbcedb06e485f611e&chksm=bd2d0db88a5a84ae5865cd05f8c7899153d16ec7e7976f06033f4fbfbecc2fdee6e8b89bb17b&scene=21#wechat_redirect)

###### innodb_flush_log_at_trx_commit

0: 如果 innodb_flush_log_at_trx_commit 的值为0,log buffer每秒就会被刷写日志文件到磁盘，提交事务的时候不做任何操作。

1: 当设为默认值1的时候，每次提交事务的时候，都会将log buffer刷写到日志。

2: 如果设为2,每次提交事务都会写日志，但并不会执行刷的操作。每秒定时会刷到日志文件。要注意的是，并不能保证100%每秒一定都会刷到磁盘，这要取决于进程的调度。

默认值1是为了保证完整的ACID。当然，你可以将这个配置项设为1以外的值来换取更高的性能，但是在系统崩溃的时候，你将会丢失1秒的数据。设为0的话，mysqld进程崩溃的时候，就会丢失最后1秒的事务。设为2,只有在操作系统崩溃或者断电的时候才会丢失最后1秒的数据。InnoDB在做恢复的时候会忽略这个值。

刷写的概念
刷写其实是两个操作，刷（flush）和写（write），区分这两个概念（两个系统调用）是很重要的。在大多数的操作系统中，把Innodb的log buffer（内存）写入日志（调用系统调用write），只是简单的把数据移到操作系统缓存中，操作系统缓存同样指的是内存。并没有实际的持久化数据。

所以，通常设为0和2的时候，在崩溃或断电的时候会丢失最后一秒的数据，因为这个时候数据只是存在于操作系统缓存。之所以说“通常”，可能会有丢失不只1秒的数据的情况，比如说执行flush操作的时候阻塞了。

总结
设为1当然是最安全的，但性能页是最差的（相对其他两个参数而言，但不是不能接受）。如果对数据一致性和完整性要求不高，完全可以设为2,如果只最求性能，例如高并发写的日志服务器，设为0来获得更高性能。

[innodb_flush_log_at_trx_commit配置](https://blog.csdn.net/liqfyiyi/article/details/51137764)


## 事务

每一种级别都规定了： **一个事务中所做的修改，哪些在事务内和事务间是可见的，哪些是不可见的**

#### 隔离级别

###### READ UNCOMMITTED（读未提交）

对于事务未提交的数据，其他事务依然可以读取。


###### READ COMMITTED（读已提交）

- 大多数数据库系统默认的隔离级别都是 READ COMMITTED（但 MySQL 不是）。
- 一个事务所做的修改，在提交之前，对其他事务都是不可见的。

###### REPEATABLE READ（可重复读）

- 事务开启时，不允许其他事务进行 update 操作，这样事务A读取的数据都是一致的，称为可重复读
- MySQL默认的事务隔离级别

###### SERIALIZABLE（可串行化）

#### 错误场景

###### 不可重复读

事务A多次读取数据

事务B修改了数据 `Update`

事务A多次读取的数据不一致

###### 脏读

读取到其他事务未提交的数据

###### 幻读

A事务读取范围数据

B事务在该范围中插入数据 `Insert`

A事务读取范围数据出现之前没有看到的数据


[Mysql的默认的事务隔离级别是？脏读、幻读、不可重复读又是什么？](http://www.cainiaoxueyuan.com/sjk/5196.html)
[高性能MySQL读书笔记-事务](https://segmentfault.com/a/1190000011316642#articleHeader8)
[InnoDB并发如此高，原因竟然在这？](https://mp.weixin.qq.com/s?__biz=MjM5ODYxMDA5OQ==&mid=2651961444&idx=1&sn=830a93eb74ca484cbcedb06e485f611e&chksm=bd2d0db88a5a84ae5865cd05f8c7899153d16ec7e7976f06033f4fbfbecc2fdee6e8b89bb17b&scene=21#wechat_redirect)




---

redo补充

- 事务开启
- 数据修改
- 先写入日志文件
- 写入内存数据
- 事务提交
- 将日志文件数据刷入磁盘中 （可以设置刷盘的事件）



## 参考网站

[MYSQL性能优化的最佳20+条经验](https://coolshell.cn/articles/1846.html)
[《高性能Mysql》]
[MySQL 索引优化全攻略](https://www.runoob.com/w3cnote/mysql-index.html)
[MySQL Join的底层实现原理-分为三种](https://juejin.im/post/5bea59896fb9a049f23c49b8)	
[推荐：将原理分成两种类型性能优化之Block Nested-Loop Join(BNL)](https://cloud.tencent.com/developer/article/1181402)
[explain 详解](http://www.cnitblog.com/aliyiyi08/archive/2008/09/09/48878.html)



[redo]:data:image/jpeg;base64,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ZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/bAEMAAgICAgICAwICAwUDAwMFBgUFBQUGCAYGBgYGCAoICAgICAgKCgoKCgoKCgwMDAwMDA4ODg4ODw8PDw8PDw8PD//bAEMBAgICBAQEBwQEBxALCQsQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEP/dAAQARv/aAAwDAQACEQMRAD8A/fyiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9D9/KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/0f38ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//S/fyiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9P9/KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/1P38ooooAKKKKACiiigAooooAKKKKACivL/EnxS0rw18U/BXwpuLOaa/8bWur3dvOhXyYU0dbdpRJk7tz/aUCYBHDZI4z6hQAUUUUAFFFcH8Qfih8OvhRokniP4k+I7Hw3p0alvOvZ0hDAMqnYGO5zudRhQTlh6igDvKK+KLf9tC18cJFL8Afhd4w+JlnceSYdTh08aNpEqyruyl3qzWpbA6lYyvTLAMpa5P8Zf2xmimu9P/AGcrTylYeXDdeNbKK6dSByyxWk0KkZOQJm6HBPGQD7Lor4wb9pH49+Hbp5PiF+zf4jttKXaBc6Bqema/Lliq5NrFLDNtUsMkAnAYgEKTXefC39rX4G/FrW18H6LrcujeLvKjlfQNctZtJ1VPMXcFFvdInmkDkmEyLjnOKAPpOiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP//V/fyiiigAooooAKKKKACiiigAooooA+QPir/yeT8Av+wL44/9A0uvr+vkD4q/8nk/AL/sC+OP/QNLr6/oAKKK+MP2iPHHjXx94utv2UfgzdPp2ueIbI3PiXxBCSf+Ed0OVvLYoVDbb68UOlqCVK4MoI2hgAXPiJ8cviD438Yar8Fv2VYNN1LxPojCPX/EGq+a2i6AzY/cEQjN1flSSsCMFjI/fMMFK3PhV+yN8NPh3rMPjnxPc6h8R/HiOZv+Ei8T3B1G7hlbbuNnG/7izUbQqeQiuECoXYKK9j+Ffwp8AfBTwRp/w6+GekRaLoWmqRHDHlmZ25eSR2JaSRzyzsST9MCvRKACiiigArzP4lfBn4UfGLS30f4oeE9O8S27RNCpvLdJJY0cgsIpseZESQDmNlOQDnIr0yigD4I1LQvjz+yc6654Nv8AUPiz8IbPaLrQLv8A0rxLo1sWwZNOuQoa+hgXpbz5l2ABZCctX1v8MPil4C+MvgrTviF8NtYh1vQ9TQNFNC3KtgFopUPzRypnDxuAyngivQK/Pz4veGNU/ZW+J2p/tX+ABLJ4C11lf4i6DAgfKonlxa3ZRjG2eEkNdqp/fR7nIMmXoA/QOiqenajp+r6fbatpNzFe2N7Ek8E8DrJFLFIoZHR1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s218ZJT1APZPh7+054F+IXinS/CMek674eu/EVpNf6JJrWmyWMWr2tuEaV7RnJJKJIjlJBHJsYMFIBI890/9uz4J6xZWeuaNaa9f+HpLqGxvdZh0qVtN0u5uLgW0UV7PkBGZ2TIjEhQOhfbuFcX8HPB+nah8Q/Bes678H/Huj+JfDIujLqPiLxVd6rpOkTzWctvObRbrWbsXQm3eUjRwH5GDsUK4rjoPgT8SbX/gnU/watvDbReMpXaR9ORoVkZ2137WzFw/lkmH5yd2T068UAewePP2qdK8G/tMeHfhfcXF2ugSaNq8+prHouoXEv262mtFt/JeK3YyR7JZNzRBkBxuYHAP1/oms2HiHSLPXNLMjWl9Es0Rlhkt5CjjI3RTKkiH1VlBHcV8r/GzS/GPhT48fDz45aF4W1Dxho2j6Treiala6QIXvrc6i9pNb3CQzSxCZN9uyOFYMm4NgjOPp7wxrN54h0Cx1vUNIutBnvYxI1jfGH7VACeFl8iSWMPjBIWRgM4zkGgDeooooAKKKKACiiigAooooAKKKKACiiigAooooA4D4sf8ks8Zf9gbUf8A0mkrz/8AZO/5NZ+Df/YmeHv/AE3QV6B8WP8AklnjL/sDaj/6TSV5/wDsnf8AJrPwb/7Ezw9/6boKAPf6KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK+IPiZ/yfn8Ev+xZ8V/zs6+36+IPiZ/yfn8Ev+xZ8V/zs6APt+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAr5A/a7/wCaK/8AZTPDn/tevr+vkD9rv/miv/ZTPDn/ALXoA+v6KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD5A/YK/5NP8Df8AcT/9OV1X1/XyR+wraXVj+yt4Itb2F7eZP7S3JIpRhnUbkjIPIyDmvregAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAPkDUv+T+fD3/ZM9Z/9PWm19f18gal/wAn8+Hv+yZ6z/6etNr6/oAKKKKACiiigAooooAKKKKACiiigAooooA//9P9/KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD5A/aT/5K7+zn/wBjnc/+mTUK+v6+U/2g9D1rVfip8AL3S9PuLy30zxdcz3ckMTyJbxHRr9A8rKCEUsQu5sDJA6mvqygAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAorgPix/ySzxl/wBgbUf/AEmkrz/9k7/k1n4N/wDYmeHv/TdBQB7/AEUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAVGYYmlWcoplRWVWwNwViCwB64JUZHfA9Kkr4s+I+o6hB+3N8GtOguZY7S78NeKGmhV2EcrRG12F1BwxXcdpI4ycdaAPtOiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAqvcWlrd+X9qhSbyXEib1DbHXoy56MOxHIqxXyZ+1fqOoac3wafT7mW1af4keH4JDE7IXilFwro20jKsOGU8EcGgD6zooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAK9rd2t9At1ZTJcQvna8bB1ODg4I4OCMVYr5A/YK/5NP8AA3/cT/8ATldV9f0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUV8gal/yfz4e/7JnrP/p602vr+gAooooAKKKKACiiigAooooAKKKKACiiigD/1P38ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAMu/wBc0XSrqxstU1C3s7jU5TBaRzSpG9xKFLlIlYguwUFtq5OAT0FalfIH7Sf/ACV39nP/ALHO5/8ATJqFfX9ABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAHAfFj/klnjL/ALA2o/8ApNJXn/7J3/JrPwb/AOxM8Pf+m6Cve5oYriJ4J0WSKRSrKwBVlIwQQeCCOoohhit4kggRY4o1CqqgBVUDAAA4AA6CgCSiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACviD4mf8n5/BL/ALFnxX/Ozr7frLl0PRZ9Xt/EE+n28mqWkTwQ3bRIbiKKUguiSkblVioLKDg4GelAGpRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAV8gftd/8ANFf+ymeHP/a9fX9Z+oaTpWrf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19f0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAf/X/fyiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA8L+LHxR1rwD44+FfhfS7W3uLfx5r02k3bzBy8MUdhc3geLayjcWgC/MCME8Zr3SvkD9pP8A5K7+zn/2Odz/AOmTUK+v6ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA8g/aE/5IF8S/wDsWdZ/9IpaP2e/+SBfDT/sWdG/9IoqP2hP+SBfEv8A7FnWf/SKWj9nv/kgXw0/7FnRv/SKKgD1+iiigDn/ABZ/yKus/wDXlcf+i2rwD9in/k0f4Q/9izpn/oha9/8AFn/Iq6z/ANeVx/6LavAP2Kf+TR/hD/2LOmf+iFoA+n6KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAr5A+DX/ACdh+0V/3KP/AKbZK+v68I8AfC/X/Cvxu+K3xK1G4tZNM8df2F9hjidzPH/Zlo9vN5ysiqu5mBTazZHXaeKAPd6KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACvkD9rv8A5or/ANlM8Of+16+v6+eP2hfh54o+IX/CtP8AhGIEn/4Rrxto2t3u+RY9llZ+b5zruI3MN4wo5PagD6HooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAPN/hH8L9A+DPw90r4a+F7i6utM0fz/JkvHR52+0TyXDb2jSNThpCBhRxjOTzXpFeEfszfFDX/jN8EfDfxK8UW9ra6nrH2zzo7NHSBfs93NbrsWR5GGVjBOWPOcYHFe70AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB8gal/yfz4e/7JnrP/p602vr+q/2S1+1fb/JT7Ts8vzdo37M7tu7rtzzjpmrFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/0P38ooooAKKKKACiiigAooooAKKKKACiiigAooooAp3uo6fpkQn1G5itYmbaGldY1LEE4BYgZwDxWX/wlvhX/oM2X/gRH/jXxx+1T4J8I/EX45/s6eDfHej2uvaHqGteIftFleRLNBL5WhXUqb0bIO2RFYehANekf8MU/sj/APRIfDP/AILI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igAooooAK+ZPhZ4v8Tax+0d8cfCWp6jLc6P4ebw02n2zkFLY3mns8/l9wHZQxGcZyRyTn6br5A+DX/J2H7RX/co/+m2SgD6/ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK+cP2jPHvizwH/wrD/hFL77D/wkXjnRNHv/AN1FL51hd+d50X7xW27to+ZMOMcMOa+j6+QP2u/+aK/9lM8Of+16APr+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA8g+Avwp/4Uh8J9C+F/9qf21/Yv2r/S/I+zeb9puZbj/Vb5Nu3zNv3znGeM4Hr9eUfA/wCKlr8bPhdovxOstPfSodZ+07baSQStH9nuJLc5cBQcmPd074r1egAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAPkDUv8Ak/nw9/2TPWf/AE9abX1/Xm8/wv0Cf4u2Xxoe4uhrdjoVz4fSEOn2U2t1dQXbuybN/mh4FCkSBdpIKk4I9IoAKKKKACiiigAooooAKKKKACiiigAooooA/9T9/KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigDwv4sfC7WvH3jj4V+KNLure3t/AevTatdpMXDzRSWFzZhItqsNwacN8xAwDzmvdK8z8dfFHRfAPiXwP4X1S1uLi48earJpNo8IQpDLHaT3heXcynaVgK/KCckcYr0ygAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigDm/GWuS+GfCGueJIIlml0mxubtY2JCu0ETSBSRzglcGuX+C3jbUPiZ8HPAnxH1aCK1vvFeg6Xq08MG7yo5b61jndE3EttVnIXJJx1Jq78WP+SWeMv+wNqP/pNJXn/7J3/JrPwb/wCxM8Pf+m6CgD3+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACuX0rwX4X0TxLrvjDStPS31nxL9l/tG5UsWufscZig3AkgbEJUYA9811FfOHwz8e+LPEH7Qnxo8DavffaNE8J/wDCOf2Zb+VEn2f7fYvNcfOqh33uAfnZsdFwOKAPo+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAr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

