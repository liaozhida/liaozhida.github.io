[Java魔法类：sun.misc.Unsafe.md](http://www.cnblogs.com/suxuan/p/4948608.html)


sun.misc.Unsafe是JDK内部用的工具类。它通过暴露一些Java意义上说“不安全”的功能给Java层代码，来让JDK能够更多的使用Java代码来实现一些原本是平台相关的、需要使用native语言（例如C或C++）才可以实现的功能。该类不应该在JDK核心类库之外使用。

JVM的实现可以自由选择如何实现Java对象的“布局”，也就是在内存里Java对象的各个部分放在哪里，包括对象的实例字段和一些元数据之类。sun.misc.Unsafe里关于对象字段访问的方法把对象布局抽象出来，它提供了objectFieldOffset()方法用于获取某个字段相对Java对象的“起始地址”的偏移量，也提供了getInt、getLong、getObject之类的方法可以使用前面获取的偏移量来访问某个Java对象的某个字段。

每个JVM都有自己的方式来实现Java对象的布局。Oracle/Sun HotSpot VM所使用的Java对象布局可以参考这篇博客：http://www.codeinstructions.com/2008/12/java-objects-memory-structure.html
（这篇内容其实并不是太完整但只是入门凑合看看是够了。另外它只针对32位的JDK6的HotSpot VM的默认配置。）

同事Aleksey Shipilev专门写了个小工具来显示Java对象的布局





[Java中Unsafe类详解](http://www.cnblogs.com/mickole/articles/3757278.html)