### 全局的备份恢复

#### 备份

```
mongodump -d yea -o /data/db/3.1_2017_07_06_back
```

#### 迁移到本机

```
scp -r root@112.74.196.160:/root/docker-data/mongo/3.1_2017_02_06_back /Users/zhidaliao/bak_dir/mongo


scp -r testServer:/root/docker-data/mongo/3.1_2017_02_06_back /Users/zhidaliao/bak_dir/mongo


scp -r /Users/zhidaliao/bak_dir/mongo  dbServer:/mnt/docker-data/testMongo
```

#### 恢复

/root/docker-data/mongo   复制到这个文件夹
进入docer  进入/data/db

```
mongorestore -d yea 3.1_back/yea
```


### 指定集合的导入导出

#### 导出数据库中指定集合的数据：

```
 mongoexport -h 192.168.1.233 --port 27018 -d yourdb -c yourcoll -o /root/yourcoll.json
```

#### 导出集合中指定字段的数据，导出的文件格式为csv

```
mongoexport -d yourdb -c test -f "id,name,score" --csv -o /root/test.csv
```

#### 根据条件导出数据：

```
mongoexport -d yourdb -c yourcoll -q '{score:{$gt:80}}' -o /root/yourcoll-bk.json
```


#### 还原导出的集合数据：

```
mongoimport -d yourdb -c yourcoll --file /root/yourcoll.json
```

#### 导入集合数据，插入或更新现有的数据：

```
mongoimport -d test -c yourcoll --file /root/yourcoll.json --upsert
```


### MongoDB数据库克隆

```
db.copyDatabase(fromdb, todb, fromhost, username, password)
```

#### 从远程MongoDB中复制指定数据库到本地：

```
 db.copyDatabase("yii2", "lyii2", "192.168.0.69")
```

#### 集合的克隆

```
db.runCommand({ cloneCollection: "<namespace>", from: "<hostname>", query: { <query> } });
```

#### 从远程MongoDB中克隆指定的集合到本地数据库中：

```
db.runCommand({  cloneCollection: "test.user", from: "192.168.0.69", query:{}    })
```