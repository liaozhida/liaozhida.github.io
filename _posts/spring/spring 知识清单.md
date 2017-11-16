
spring 知识清单.md

###### [Java JDK 动态代理使用及实现原理分析](http://blog.jobbole.com/104433/)

Java动态代理类位于java.lang.reflect包下，一般主要涉及到以下两个类：

(1): `Interface InvocationHandler`：该接口中仅定义了一个方法: `publicobject invoke(Object obj,Method method, Object[] args)`
(2): `Proxy`：该类即为动态代理类
- `protected Proxy(InvocationHandler h)`：构造函数，用于给内部的h赋值。
- `static Class getProxyClass (ClassLoaderloader, Class[] interfaces)`：获得一个代理类，其中loader是类装载器，interfaces是真实类所拥有的全部接口的数组。
- `static Object newProxyInstance(ClassLoaderloader, Class[] interfaces, InvocationHandler h)`：返回代理类的一个实例，返回后的代理类可以当作被代理类使用(可使用被代理类的在Subject接口中声明过的方法)

**因为JDK生成的最终真正的代理类，它继承自Proxy并实现了我们定义的Subject接口，在实现Subject接口方法的内部，通过反射调用了`InvocationHandlerImpl`(构造入参是被代理类)的invoke(调用被代理类的方法，然后增强)方法。**

原理？其实就是装饰者模式，通过反射调用 被代理类的方法。

###### [Spring AOP 实现原理与 CGLIB 应用](http://blog.jobbole.com/28791/)

广泛应用于处理一些具有横切性质的系统级服务，如事务管理、安全检查、缓存、对象池管理等。AOP 实现的关键就在于 AOP 框架自动创建的 AOP 代理，AOP 代理则可分为静态代理和动态代理两大类，其中静态代理是指使用 AOP 框架提供的命令进行编译，从而在编译阶段就可生成 AOP 代理类，因此也称为编译时增强；而动态代理则在运行时借助于 JDK 动态代理、CGLIB 等在内存中“临时”生成 AOP 动态代理类，因此也被称为运行时增强。

假设系统中有 3 段完全相似的代码，这些代码通常会采用“复制”、“粘贴”方式来完成，通过这种“复制”、“粘贴”方式开发出来的软件如图 1 所示。：应用需要方法 1、方法 2、方法 3 彻底与深色方法分离——方法 1、方法 2、方法 3 无须直接调用深色方法，那如何解决？

我们希望有一种特殊的方法：我们只要定义该方法，无须在方法 1、方法 2、方法 3 中显式调用它，系统会“自动”执行该特殊方法。

AOP 专门用于处理系统中分布于各个模块（不同方法）中的交叉关注点的问题，在 Java EE 应用中，常常通过 AOP 来处理一些具有横切性质的系统级服务，如事务管理、安全检查、缓存、对象池管理等，AOP 已经成为一种非常常用的解决方案。


AspectJ 是 Java 语言的一个 AOP 实现，其主要包括两个部分：第一个部分定义了如何表达、定义 AOP 编程中的语法规范，通过这套语言规范，我们可以方便地用 AOP 来解决 Java 语言中存在的交叉关注点问题；另一个部分是工具部分，包括编译器、调试工具等。有自己的命名规范编译过程


与 AspectJ 相同的是，Spring AOP 同样需要对目标类进行增强，也就是生成新的 AOP 代理类；与 AspectJ 不同的是，Spring AOP 无需使用任何特殊命令对 Java 源代码进行编译，它采用运行时动态地、在内存中临时生成“代理类”的方式来生成 AOP 代理。


Spring 允许使用 AspectJ Annotation 用于定义方面（Aspect）、切入点（Pointcut）和增强处理（Advice），Spring 框架则可识别并根据这些 Annotation 来生成 AOP 代理。Spring 只是使用了和 AspectJ 5 一样的注解，但并没有使用 AspectJ 的编译器或者织入器（Weaver），底层依然使用的是 Spring AOP，依然是在运行时动态生成 AOP 代理，并不依赖于 AspectJ 的编译器或者织入器。



