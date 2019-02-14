 
## 理论篇


SUT：System Under Test或Software Under Test的簡寫，代表待測程式。如果是單元測試，SUT就是一個function或method。
DOC：SUT中的依赖组件，一般用测试桩(Mock)代替


 
#### 单元测试的几个特性

好的单元测试宏观上来说，具有自动化、独立性、可重复执行的特点。
- A:Automatic(自动化)
- I:Independent(独立性) 
- R:Repeatable(可重复)

#### rpc接口是否需要测试

RPC接口一般大家会忽略他的测试，觉得只要DAO层和业务层通过测试，验证了核心的业务流程就可以了，

- RPC的接口一般包含了数据校验加工和逻辑分发处理，如果因为上层的处理失败，下层的核心业务是正常的一样不能提供服务
- 保证返回给前端的数据结构符合要求


#### 应该为私有方法添加测试么？

新创建项目：
在成功的用了TDD或者测试驱动重构（Test-Driven Refactoring）以后，你的代码中就不会出现针对私有方法的测试。
如果你用TDD编写全新的代码，在没有测试之前是没有功能的。私有方法是到了重构那一步的最后才会出现。把代码转移到私有方法中的这个过程，已经被先前写过的测试覆盖到了。所以，如果你成功了用了TDD，代码中就不会出现针对私有方法的测试。

遗留项目：
如果你在改善遗留代码，你就该使用测试驱动重构。这样的话，可能会临时针对私有方法写一些测试。但是，随着测试覆盖率的增加，那些public方法的测试会覆盖到所有的路径，也包括了`私有方法的调用`。所以，你也不再需要测试私有方法。
    
临时私有方法测试采用映射的方式编写；

```
Example example = new Example();
Method add = example.getClass().getDeclaredMethod("add", int.class, int.class);
add.setAccessible(true);
```

另外可以参考这篇文章对私有方法的见解：[Testing Private Methods with JUnit and SuiteRunner](https://www.artima.com/suiterunner/private.html) ， 要点如下：
- Don't test private methods.
- Give the methods package access.
- Use a nested test class.
- Use reflection.


#### 单元测试回滚机制

默认机制:**不回滚**，需要自动回滚可以使用注释和集成类的方式设置：

###### 注释

```
@Transactional
@TransactionConfiguration(defaultRollback=true)
```

###### 类继承

`AbstractTransactionalJUnit4SpringContextTests`默认操作修改、新增、删除操作是事务自动回滚，避免出现脏数据，如果不需要回滚，可以添加@Rollback(false)注解即可。

```
extends AbstractTransactionalJUnit4SpringContextTests  
```


#### 单元覆盖率统计



- 推荐开源工具：jacoco
- 代码覆盖率统计是用来发现没有被测试覆盖的代码

1. 对Java字节码进行插桩，On-The-Fly和Offine两种方式。 
2. 执行测试用例，收集程序执行轨迹信息，将其dump到内存。 
3. 数据处理器结合程序执行轨迹信息和代码结构信息分析生成代码覆盖率报告。 
4. 将代码覆盖率报告图形化展示出来，如html、xml等文件格式。 

参考文章：[浅谈代码覆盖率](https://tech.youzan.com/code-coverage/)


#### 外部依赖


###### 对于数据库的依赖:

- 单元测试肯定是不能与实际数据库连接的，无论是本地开发数据库或者beta。所有对数据库操作的单元测试都需要是in memory。所以，你需要利用Dependency Injection的技术来提供一个in-memory database。
- 对于数据库相关的查询，更新，删除等操作，不能假设数据库里的数据是存在的，或者直接操作数据库把数据插入进去，请使用程序插入或者导入数据的方式来准备数据。
因为数据库里的数据都是有关联的，构造测试数据不是构造一两条记录那么简单
- 不能在开发中使用测试库的数据作为测试结果，hardcode测试库的数据会造成单元测试失效，无法维护

###### 对于外部系统的依赖

- 使用Mock技术代替（推荐）。
- 打桩处理，类似 [swagger](https://swagger.io/) 这样的外部服务或者自己用NodeJs搭建一个简单的路由转发应用，定义好接口地址和返回的结果数据结构


## Mock 工具

- 外部的服务会导致在 单测环境下没有办法工作， 比如数据库和外部的系统
- 测试应该关注的是类的代码实现， 如果外部的类会直接的影响到这些被测试的类，那不是我们想要的结果

Mockito 和 PowerMock 都用于集成测试中，使用mock对象替代耦合的类，两者的不同在于 Mockito 适用于所有标准的场景， PowerMock 用于特殊的情况：比如Mock私有 & 静态的方法。

#### 几种Mock比较

直接参考以下文章：

- [Mockito vs JMockit](https://stackoverflow.com/questions/4105592/comparison-between-mockito-vs-jmockit-why-is-mockito-voted-better-than-jmockit) 

- [https://www.baeldung.com/mockito-vs-easymock-vs-jmockit](Mockito vs EasyMock vs JMockit)


#### Mock特性演示：

###### 对私有方法进行Mock

```

class Generator {

    public int getLuckyNumber(String name) {
 
        if (name == null) {
            return getDefaultLuckyNumber();
        }

        return 0;
    }

    private int getDefaultLuckyNumber() {
        return 100;
    }

}


```

```
@Test
public  void test() throws Exception {

    Generator mock = spy(new Generator());

    doReturn(1).when(mock, "getDefaultLuckyNumber");

    int result = mock.getLuckyNumber(null);

    assertEquals(1, result);
}
```

Mock技术一般用于对外部类和组件进行替换，如果单元测试中对私有方法的Mock是必要的，说明类的设计是有问题的。



###### Mock & Spy

Mock一个对象，我们能改变对象的返回结果
Spy一个对象，能改变对象的返回结果，但是对象调用的方法内的逻辑会被真实的执行。

```
List list = new LinkedList();  
List spy = spy(list);  
  
when(spy.size()).thenReturn(100);  
spy.add("one");  
   
//prints "one" - the first element of a list  
System.out.println(spy.get(0));  
   
//size() method was stubbed - 100 is printed  
System.out.println(spy.size());  

```
 

#### Mockito


###### thenReturn & doReturn 执行顺序

```
List list = new LinkedList();
List spy = spy(list);

//报错，在执行 get(0)的时候就会抛出异常
when(spy.get(0)).thenReturn("foo");

//正常执行，直接返回 "foo" 值
doReturn("foo").when(spy).get(0);
```

###### 自定义返回结果

```
List list = mock(List.class);

when(list.get(0)).thenReturn("hello");
System.out.println(list.get(0));

when(list.get(0)).thenAnswer(new Answer() {
    @Override
    public Object answer(InvocationOnMock invocation) throws Throwable {
        Object[] args = invocation.getArguments();
        Object mock = invocation.getMock();
        return "hello world" ;
    }
});
System.out.println(list.get(0));
```

```
hello
hello world
```



###### 多次调用返回不同结果

```
List list = mock(List.class);

when(list.get(0)).thenReturn("hello").thenReturn("world").thenThrow(new RuntimeException("exception"));
//when(list.get(0)).thenReturn("hello","world").thenThrow(new RuntimeException("exception"));

System.out.println(list.get(0));
System.out.println(list.get(0));
System.out.println(list.get(0));


```

```
hello
world

java.lang.RuntimeException: exception
```


 



###### verify

用于验证被Mock的对象行为，几个例子：

- 验证 list.size() 方法是否被执行

```
List<String> mockedList = mock(MyList.class);
mockedList.size();
verify(mockedList).size();
```

- 验证 list.size() 方法被执行了几次

```
verify(mockedList, times(1)).size();
```

- 验证执行顺序

```
List<String> mockedList = mock(MyList.class);
mockedList.size();
mockedList.add("a parameter");
 
InOrder inOrder = Mockito.inOrder(mockedList);
inOrder.verify(mockedList).size();
inOrder.verify(mockedList).add("a parameter");
```

- 验证是否从来没有被执行过

```
List<String> mockedList = mock(MyList.class);
mockedList.size();
verify(mockedList, never()).clear();
```

 

## 参考网站

- [单元测试框架PowerMock教程](https://www.ezlippi.com/blog/2017/08/powermock-introduction.html)
- [Mockito And Private Methods](https://github.com/mockito/mockito/wiki/Mockito-And-Private-Methods)
- [使用Mockito进行单元测试【2】—— stub 和 高级特性](http://qiuguo0205.iteye.com/blog/1456528)
- [Android单元测试(三)：PowerMock框架的使用](https://juejin.im/entry/5a10fb786fb9a04522071756)
- [TestNG使用介绍](https://www.jianshu.com/p/74816a200221)
- [Mockito and Power Mockito – Cheatsheet](https://raseshmori.wordpress.com/2015/01/07/mockito-and-power-mockito-cheatsheet/)
- [JUnit Testing using Mockito and PowerMock](https://blog.codecentric.de/en/2016/03/junit-testing-using-mockito-powermock/)
- [Mocking of Private Methods Using PowerMock](https://www.baeldung.com/powermock-private-method)
- [Verify用法](https://www.baeldung.com/mockito-verify)
- [单元测试覆盖率-JaCoCo](https://www.ibm.com/developerworks/cn/java/j-lo-jacoco/index.html)
- [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)