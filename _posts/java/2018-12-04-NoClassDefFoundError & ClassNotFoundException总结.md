---
layout:     post
title:      "NoClassDefFoundError & ClassNotFoundException总结"
subtitle:	"异常定位"
date:       2018-12-12 12:00:00
author:     "zhida"
header-img: "img/post-bg-road.jpg"
tags:
    - Java
---


最近一个应用程序A，引入了一个二方包 xxx-common.jar, 能够正常运行。
然后应用B也引用了这个二方包，部署启动也都正常，但是使用 xxx-common.jar 的一个类的静态方法时，却抛出了一个异常 `NoClassDefFoundError`。

借这个排查的机会把这个异常重新学习了一下，首先是理解两种异常的区别，因为长得很像，大家很容易混在一起。

首先理解两种异常的区别：

### ClassNotFoundException ： 

受检异常，在应用启动的时候，加载不到相应的类就会抛出异常，常见场景：

- 1、没有引入相应的jar包。
- 2、包冲突，不同的jar包中有相同的类

一般在编译的时候就会报异常，或者在调用反射代码的时候报异常 ,所以我们在启动spring容器的时候偶尔会看到这种异常。

```
Class.forName("").newInstance()
// Class.forName() 、 ClassLoader.loadClass() 、 ClassLoader.findSystemClass()
``` 


### NoClassDefFoundError

NoClassDefFoundError 是fata error,主线程发生异常时整个程序都会挂掉， 
当JVM初始化一个对象 或者 调用类的静态方法 ，不能找到class文件的时候就会报这个错。

出现异常一般是因为这几种原因：

- 1、编译时和运行时的classpath不一致，导致无法加载到类。
- 2、引入的jar包的JDK版本和应用支持的JDK版本不一致，也会导致无法加载类。
- 3、执行对象的静态代码块或者初始化静态域的时候抛异常，导致类无法成功初始化。

1、2 好理解，主要梳理一下第三种情况

这种错误一般在编译期是不会出现的，在运行时加载类的时候才会出现，通常在执行静态代码块或者初始化类中的静态域的时候抛出异常，就会导致类初始化失败。

复现错误：

```
public class NoClassDefTest {

    public static void main(String[] args) {
        NoClassDefFoundErrorExample noClassDefFoundErrorExample = new NoClassDefFoundErrorExample();
        noClassDefFoundErrorExample.getClassWithInitErrors();
    }

}

class ClassWithInitErrors {
	// 静态域抛出异常，导致无法初始化类
    static int data = 1 / 0;
}

class NoClassDefFoundErrorExample {
    public ClassWithInitErrors getClassWithInitErrors() {
        ClassWithInitErrors test;
        try {
            test = new ClassWithInitErrors();
        } catch (Throwable t) {
            System.out.println("Throwable--->" + t);
        }
        test = new ClassWithInitErrors();
        return test;
    }
}
```


```
Throwable--->java.lang.ExceptionInInitializerError
Exception in thread "main" java.lang.NoClassDefFoundError: Could not initialize class ClassWithInitErrors
	at NoClassDefFoundErrorExample.getClassWithInitErrors(NoClassDefTest.java:38)
	at NoClassDefTest.main(NoClassDefTest.java:21)
```

##### 解决方案：

- 确认你需要的类在classpath中,查看你的 IDE :maven - external Libraries即可

- 确保classpath没有被覆盖(被脚本所修改)，在运行的程序中，加上代码 `System.getProperty("java.class.path")` 打印你加载的jar包。

- 运行时明确指定你认为程序能正常运行的 -classpath 参数，如果增加之后程序能正常运行，说明原来程序的classpath被其他人覆盖了。

- 如果你的应用使用了多个类加载器，类A被加载器X加载了，那么对于加载器Y就不可用了。

- 确认应用所支持的JDK版本，以及引用的二方包版本信息。



### 总结：

异:NoClassDefFoundError编译期存在类，运行时在classpath中无法找到。

同:两种异常都和 classpath 以及 运行时无法找到class相关。



### 参考网站



[怎么解决java.lang.NoClassDefFoundError错误](https://blog.csdn.net/jamesjxin/article/details/46606307)
[ClassNotFoundException vs NoClassDefFoundError](https://www.baeldung.com/java-classnotfoundexception-and-noclassdeffounderror)

[3 ways to solve java.lang.NoClassDefFoundError in Java J2EE](https://javarevisited.blogspot.com/2011/06/noclassdeffounderror-exception-in.html)

[Why am I getting a NoClassDefFoundError in Java?](https://stackoverflow.com/questions/34413/why-am-i-getting-a-noclassdeffounderror-in-java)

