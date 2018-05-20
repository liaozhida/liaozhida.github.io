ServiceLoader使用及原理分析.md



> 依赖倒置，依赖接口而不是依赖具体的实现。Java提供了一种方式, 让我们可以对接口的实现进行动态替换, 这就是SPI机制. SPI可以降低依赖。

> ServiceLoader是实现SPI一个重要的类。是jdk6里面引进的一个特性。在资源目录META-INF/services中放置提供者配置文件，然后在app运行时，遇到Serviceloader.load(XxxInterface.class)时，会到META-INF/services的配置文件中寻找这个接口对应的实现类全路径名，**然后使用反射去生成一个无参的实例。**


> 步骤如下:

- 定义接口
- 定义接口的实现 
- 创建resources/META-INF/services目录
- 在上一步创建的目录下创建一个以接口名(类的全名) 命名的文件, 文件的内容是实现类的类名 (类的全名), 如:在services目录下创建的文件是com.stone.imageloader.ImageLoader 文件中的内容为ImageLoader接口的实现类,可能是com.stone.imageloader.impl.FrescoImageLoader
- 使用ServiceLoader查找接口的实现.


[ServiceLoader使用及原理分析](https://blog.csdn.net/a910626/article/details/78811273)

[ServiceLoader使用看这一篇就够了](https://www.jianshu.com/p/7601ba434ff4)