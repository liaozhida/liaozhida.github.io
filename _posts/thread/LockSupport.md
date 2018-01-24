LockSupport.md


[解析Concurrent包下的ReentrantLock、LockSupport、AQS](http://blog.csdn.net/smuedward/article/details/55096338)
[Java多线程系列--“JUC锁”07之 LockSupport](http://www.cnblogs.com/skywang12345/p/3505784.html)


LockSupport.park不同于Thread.yield()，yield只是告诉操作系统可以先让其他线程运行，但自己依然是可运行状态，而park会放弃调度资格，使线程进入WAITING状态。


park是响应中断的，当有中断发生时，park会返回，线程的中断状态会被设置。另外，还需要说明一下，park可能会无缘无故的返回，程序应该重新检查park等待的条件是否满足。

park有两个变体： 
parkNanos：可以指定等待的最长时间，参数是相对于当前时间的纳秒数。 
parkUntil：可以指定最长等到什么时候，参数是绝对时间，是相对于纪元时的毫秒数。



这些park方法还有一些变体，可以指定一个对象，表示是由于该对象进行等待的，以便于调试，通常传递的值是this，这些方法有：
```
public static void park(Object blocker)
public static void parkNanos(Object blocker, long nanos)
public static void parkUntil(Object blocker, long deadline)
```




重点，阻塞的时候主要看有没有许可：

按照一般的逻辑， Test因为阻塞了两秒，导致 LockSupport.unpark(test); 先执行，然后再执行 LockSupport.park(); 按理说 "hello world" 会因为阻塞导致不会打印出来，但是因为 unpark 获得了许可，park并不会阻塞，所以会成功输出 "hello world"

```
public class Printer {

	public static void main(String[] args) throws InterruptedException {

		Test test = new Test();
		test.start();
		LockSupport.unpark(test);
	}

}

class Test extends Thread {

	@Override
	public void run() {
		try {
			TimeUnit.MILLISECONDS.sleep(2000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		LockSupport.park();
		System.out.println("hello world");
	}

}
```


使用 LockSupport 实现交替输出

```

```

