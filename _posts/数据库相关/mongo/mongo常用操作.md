- 新增字段:更新现有集合字段相同，如果指定的字段不存在，$set 将添加一个新字段。

```
> db.foo.find()
> db.foo.insert({"test":"a"})
> db.foo.find()
{"_id" : ObjectId("4e93037bbf6f1dd3a0a9541a"),"test" :"a" }
> item = db.foo.findOne()
{"_id" : ObjectId("4e93037bbf6f1dd3a0a9541a"),"test" :"a" }
> db.foo.update({"_id" :ObjectId("4e93037bbf6f1dd3a0a9541a") },{$set : {"new_field":1}})
> db.foo.find()
{"_id" : ObjectId("4e93037bbf6f1dd3a0a9541a"),"new_field" : 1,"test" :"a" }
```