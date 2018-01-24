## 基本概念

一.dump基本概念

在故障定位(尤其是out of memory)和性能分析的时候，经常会用到一些文件来帮助我们排除代码问题。这些文件记录了JVM运行期间的内存占用、线程执行等情况，这就是我们常说的dump文件。常用的有heap dump和thread dump（也叫javacore，或java dump）。我们可以这么理解：heap dump记录内存信息的，thread dump是记录CPU信息的。

heap dump：

heap dump文件是一个二进制文件，它保存了某一时刻JVM堆中对象使用情况。HeapDump文件是指定时刻的Java堆栈的快照，是一种镜像文件。
Heap Analyzer工具通过分析HeapDump文件，哪些对象占用了太多的堆栈空间，来发现导致内存泄露或者可能引起内存泄露的对象。

thread dump：

thread dump文件主要保存的是java应用中各线程在某一时刻的运行的位置，即执行到哪一个类的哪一个方法哪一个行上。thread dump是一个文本文件，打开后可以看到每一个线程的执行栈，以stacktrace的方式显示。通过对thread dump的分析可以得到应用是否“卡”在某一点上，即在某一点运行的时间太长，如数据库查询，长期得不到响应，最终导致系统崩溃。

单个的thread dump文件一般来说是没有什么用处的，因为它只是记录了某一个绝对时间点的情况。比较有用的是，线程在一个时间段内的执行情况。

两个thread dump文件在分析时特别有效，因为它可以看出在先后两个时间点上，线程执行的位置，如果发现先后两组数据中同一线程都执行在同一位置，则说明此处可能有问题，因为程序运行是极快的，如果两次均在某一点上，说明这一点的耗时是很大的。通过对这两个文件进行分析，查出原因，进而解决问题。

## 学习过程

###### 随意写一个多线程的代码

```
package com.paraller.hystrix_demo;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

public class PrinterDemo {

	private volatile static boolean flag = false;
	private volatile static int index = 1;

	public static void main(String[] args) {

		new Thread(new TaskA()).start();
		new Thread(new TaskB()).start();

	}

	static abstract class Task implements Runnable {

		abstract boolean interest();

		@Override
		public void run() {

			for (;;) {

				try {
					TimeUnit.MILLISECONDS.sleep(3000);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}

				if (interest()) {

					Map<String, String> map = new HashMap<String, String>();
					map.put("hello" + index, " world");

					System.out.println(Thread.currentThread().getName() + "--" + index++);
					flag = !flag;
				}
			}
		}

	}

	static class TaskA extends Task {

		@Override
		boolean interest() {
			return flag;
		}

	}

	static class TaskB extends Task {

		@Override
		boolean interest() {
			return !flag;
		}

	}

}

```


###### 找到Java进程ID 

```
ps aux | grep java 
```

###### 转储文件

heap dump
```
➜  javadump /Library/Java/JavaVirtualMachines/jdk1.7.0_80.jdk/Contents/Home/bin/jmap -dump:file=/Users/zhidaliao/javadump/hello.hprof,format=b 98414
Dumping heap to /Users/zhidaliao/javadump/hello.hprof ...
Heap dump file created
```

thread dump
```
 /Library/Java/JavaVirtualMachines/jdk1.7.0_80.jdk/Contents/Home/bin/jstack 723 > /Users/zhidaliao/javadump/thread.txt
```

######  分析文件

```
➜  javadump jhat /Users/zhidaliao/javadump/hello.hprof
Reading from /Users/zhidaliao/javadump/hello.hprof...
Dump file created Thu Jan 04 11:34:15 CST 2018
Snapshot read, resolving...
Resolving 18225 objects...
Chasing references, expect 3 dots...
Eliminating duplicate references...
Snapshot resolved.
Started HTTP server on port 7000
Server is ready.
```


###### 浏览网页

输入地址： localhost:7000 ，可以看到所有的内存情况，还有各种类信息。


```
All Classes (excluding platform)

Package com.paraller.hystrix_demo

class com.paraller.hystrix_demo.PrinterDemo [0x7d556c838]
class com.paraller.hystrix_demo.PrinterDemo$Task [0x7d55717c8]
class com.paraller.hystrix_demo.PrinterDemo$TaskA [0x7d5571820]
class com.paraller.hystrix_demo.PrinterDemo$TaskB [0x7d5573d50]
Other Queries

All classes including platform
Show all members of the rootset
Show instance counts for all classes (including platform)
Show instance counts for all classes (excluding platform)
Show heap histogram
Show finalizer summary
Execute Object Query Language (OQL) query
```

###### 分析文件2

去到网址 https://www.ibm.com/developerworks/community/groups/service/html/communityview?communityUuid=4544bafe-c7a2-455f-9d43-eb866ea60091

[Download HeapAnalyzer](ftp://public.dhe.ibm.com/software/websphere/appserv/support/tools/HeapAnalyzer/ha456.jar)

运行命令 `<Java path>java –Xmx[heapsize] –jar ha<HeapAnalyzer version>.jar <heapdump file>`

```
sudo java -Xms1024m -jar /Users/zhidaliao/Downloads/ha456.jar /Users/zhidaliao/javadump/hello.hprof 
```

会启动一个界面

使用方式看解压文件的 README.md 文件

#### jhat指定参数

###### -stack false|true

关闭对象分配调用栈跟踪(tracking object allocation call stack)。 如果分配位置信息在堆转储中不可用. 则必须将此标志设置为 false. 默认值为 true.

###### -refs false|true

关闭对象引用跟踪(tracking of references to objects)。 默认值为 true. 默认情况下, 返回的指针是指向其他特定对象的对象,如反向链接或输入引用(referrers or incoming references), 会统计/计算堆中的所有对象。

###### -port port-number

设置 jhat HTTP server 的端口号. 默认值 7000.

###### -exclude exclude-file

指定对象查询时需要排除的数据成员列表文件(a file that lists data members that should be excluded from the reachable objects query)。 例如, 如果文件列列出了 java.lang.String.value , 那么当从某个特定对象 Object o 计算可达的对象列表时, 引用路径涉及 java.lang.String.value 的都会被排除。

###### -baseline exclude-file

指定一个基准堆转储(baseline heap dump)。 在两个 heap dumps 中有相同 object ID 的对象会被标记为不是新的(marked as not being new). 其他对象被标记为新的(new). 在比较两个不同的堆转储时很有用.

###### -debug int

设置 debug 级别. 0 表示不输出调试信息。 值越大则表示输出更详细的 debug 信息.

###### -version

启动后只显示版本信息就退出

###### -h

显示帮助信息并退出. 同 -help

###### -help

显示帮助信息并退出. 同 -h

###### -J< flag >

因为 jhat 命令实际上会启动一个JVM来执行, 通过 -J 可以在启动JVM时传入一些启动参数. 例如, -J-Xmx512m 则指定运行 jhat 的Java虚拟机使用的最大堆内存为 512 MB. 如果需要使用多个JVM启动参数,则传入多个 -Jxxxxxx.


## 参考链接

- [Java Heap dump文件分析工具jhat简介](http://blog.csdn.net/renfufei/article/details/41444559)

- [java程序性能分析之thread dump和heap dump](http://bijian1013.iteye.com/blog/2221240)

- [三个实例演示 Java Thread Dump 日志分析](http://www.cnblogs.com/zhengyun_ustc/archive/2013/01/06/dumpanalysis.html)

- [利用 Java dump 进行 JVM 故障诊断](https://www.ibm.com/developerworks/cn/websphere/library/techarticles/0903_suipf_javadump/)

- [Java堆dump文件分析](http://valleylord.github.io/post/201409-java-heap-dump/)