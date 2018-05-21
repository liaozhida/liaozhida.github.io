Guide to the Java 8 forEach.md


新增的foreach方法区别


###### 一个是内部类，一个是外部处理

```
names.forEach(new Consumer<String>() {
    public void accept(String name) {
        System.out.println(name);
    }
});
```


###### 能够将处理流程用法类封装，被重复调用

```

Consumer<String> consumerNames = name -> {
    System.out.println(name);
};
 
names.forEach(consumerNames);
```
###### 支持使用 lambda表达式

```
names.forEach(name -> System.out.println(name));

names.forEach(System.out::println);		
```
				


[Guide to the Java 8 forEach](http://www.baeldung.com/foreach-java)