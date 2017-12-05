#### Java dump



 Thread dump，是 JVM 故障诊断中最重要的转储文件之一。由于 Java dump 文件包含的内容比较广泛，JVM 的许多问题都可以使用这个文件进行诊断，其中比较典型的包括线程阻塞，CPU 使用率过高，JVM Crash，堆内存不足，和类装载等问题。作为一款轻量级（与 Heap dump 和 System dump 相比）的转储文件，Java dump 的确是我们诊断 JVM 问题的首选

###### 段格式


为了便于大家的分析，Java dump 的每一段的开头，都会用“-----”与上一段明显的区分开来。而每一段的标题也会用“=====”作为标识，这样我们就能够很容易的找到每一段的开头和标题部分（如清单 1）。
清单 1. Java dump 段标题示例


```
NULL --------------------------------
0SECTION TITLE subcomponent dump routine
NULL ===============================
```

###### 行格式


Java dump 文件中，每一行都包含一个标签，这个标签最多由 15 个字符组成（如清单2中所示）。其中第一位数字代表信息的详细级别（0，1，2，3，4），级别越高代表信息越详细；接下来的两个字符是段标题的缩写，比如，“CI” 代表 “Command-line interpreter”，“CL” 代表 “Class loader”，“LK” 代表 “Locking”，“ST” 代表 “Storage”，“TI” 代表 “Title”，“XE” 代表 “Execution engine”等等；其余部分为信息的概述。
清单 2. Java dump 行标签和内容示例
```
1TISIGINFO Dump Event "uncaught" (00008000) Detail "java/lang/OutOfMemoryError" received
```

不同版本的 JVM 所产生的 Java dump 的格式可能会稍有不同，但基本上都会包含以下几个方面的内容：
- TITLE 信息块：描述 JAVA DUMP 产生的原因，时间以及文件的路径。
- GPINFO信息块：GPF 信息。
- ENVINFO 信息块：系统运行时的环境及 JVM 启动参数。
- MEMINFO 信息块：内存的使用情况和垃圾回收记录。
- LOCKS 信息块：用户监视器(Monitor)和系统监视器(Monitor)。
- THREADS信息块：所有 java 线程的状态信息和执行堆栈。
- CLASSES信息块：类加载信息。


一般来说，JVM 崩溃的时候，系统一般会自动产生一个 Java dump 文件（JVM 默认的设置参数就会触发）。这个 Java dump 会帮我们记录下 JVM 崩溃的原因，相关的信息会记录在 TITLE 信息块，GPINFO 信息块和 THREADS 信息块中。
TITLE 信息块：用于确认问题产生的原因，即是否是由于一些底层错误而导致 JVM Crash。
GPINFO 信息块：用于查看问题的详细信息和问题定位。
THREADS信息块：用于了解问题线程的运行情况。


#### Heap dump 



#### System dump