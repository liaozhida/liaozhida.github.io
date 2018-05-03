Random.md


在Java中，随机数的产生取决于种子，随机数和种子之间的关系遵循以下两个规则： 

1.种子不同，产生不同的随机数。 

2.种子相同，即使实例不同也产生相同的随机数。 

Random类的默认种子（无参构造）是System.nanoTime()的返回值（JDK1.5版本以前默认种子是System.currentTimeMillis()的返回值），这个值是距离某一个固定时间点的纳秒数，不同操作系统和硬件有不同的固定时间点，也就是不同的操作系统纳秒值是不同的，而同一操作系统的纳秒值也会不同，随机数自然也就不同了。 


---

在Java7新增了一个类ThreadLocalRandom，它是Random的增强版。在并发访问的环境下，使用ThreadLocalRandom来代替Random可以减少多线程竞争，最终保证系统具有更好的线程安全。
ThreadLocalRandom类的用法与Random用法基本类似，它提供一个静态的current()方法来获取ThreadLocalRandom对象，获取对象之后即可调用各种nextXXX()方法来获取伪随机数了。ThreadLocalRandom与Random都比Math的random()方法提供更多的方式来生成各种伪随机数，可以生成浮点类型的伪随机数，也可以生成整数类型的伪随机数，还可以指定生成随机数的范围。下面就是一个ThreadLocalRandom类的实用安全，代码如下：
System.out.println(java.util.concurrent.ThreadLocalRandom.current().nextInt(100));


[提高你的Java代码质量吧：不要随便设置随机种子](https://blog.csdn.net/p106786860/article/details/9465055)
[Java 7 的ThreadLocalRandom与 Random](https://blog.csdn.net/tfnew21/article/details/9137809)