---
layout:     post
title:      "FutureTask源码解析"
subtitle:	""
date:       2016-05-22 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-snow.jpg"
tags:
    - 并发编程
    - Java
---

Runnable 作为任务的基本表示形式，是一种有局限性的抽象，不能返回任务结构和抛出一个受检查异常，在Executor框架中 Callable 是一种可替代 Runnable 的抽象，一般而言， Callable 抽象会封装在 Future 类中， Future 提供了一个任务的生命周期，状态的查询和结果的获取，取消等。本文使用常用的 FutureTask 来简述几个常用的方法过程。

网上比较多文章是说 FutureTask依赖于AbstractQueuedSynchronizer， 从1.7开始FutureTask已经被其作者Doug Lea修改为不再依赖AbstractQueuedSynchronizer。

#### 使用场景

一般在 Executor 框架中，我们使用下面的方式使用 Future，es.submit会触发 Runnable的 run 方法

```

ExecutorService es = Executors.newFixedThreadPool(100);

Future<String> future = es.submit(new Callable<String>() {
	@Override
	public String call() throws Exception {
		return "hello";
	}

});

String result = future.get();
```

#### 继承关系

和前文描述的一样，Future类主要提供了 取消，状态返回，结果返回 几个方法，FutureTask 实现了RunnableFuture，同时具备了任务的属性。
```
public interface Future<V> {

   
    boolean cancel(boolean mayInterruptIfRunning);

    
    boolean isCancelled();
 
    boolean isDone();
 
    V get() throws InterruptedException, ExecutionException;

    V get(long timeout, TimeUnit unit) throws InterruptedException, ExecutionException, TimeoutException;
}


public interface Runnable {
    public abstract void run();
}

public interface RunnableFuture<V> extends Runnable, Future<V> {
    void run();
}

public class FutureTask<V> implements RunnableFuture<V> { 
	
	public FutureTask(Callable<V> callable) {
        if (callable == null)
            throw new NullPointerException();
        this.callable = callable;
        this.state = NEW;       // ensure visibility of callable
    }
}
```


#### 全局变量的作用



```
/* FutureTask有几个状态变量，代表当前任务的状态 state */
private volatile int state;
private static final int NEW          = 0;
private static final int COMPLETING   = 1;
private static final int NORMAL       = 2;
private static final int EXCEPTIONAL  = 3;
private static final int CANCELLED    = 4;
private static final int INTERRUPTING = 5;
private static final int INTERRUPTED  = 6;

/* 当前任务的运行线程  */
private volatile Thread runner;

/* 任务抽象 */
private Callable<V> callable;

/* 任务完成后，将结果保存在该变量中*/
private Object outcome;

/* 使用 waitNode 来表示等待中的线程，栈形式  */
private volatile WaitNode waiters;

/* 类似于AQS的链表实现，是一个静态类，区别在于只保存线程，以及单向链表 */
static final class WaitNode {
    volatile Thread thread;
    volatile WaitNode next;
    WaitNode() { 
        thread = Thread.currentThread(); 
    }
}

使用JDK的内部工具类来操作变量的内存值
private static final sun.misc.Unsafe UNSAFE;
private static final long stateOffset;
private static final long runnerOffset;
private static final long waitersOffset;
```




#### FutureTask 的主要方法

###### run()

Callable任务存在并且 state 为 New，执行任务单元，将执行完的结果传递到 set(V v) 中
```
public void run() {
    if (state != NEW ||
        !UNSAFE.compareAndSwapObject(this, runnerOffset,
                                     null, Thread.currentThread()))
        return;
    try {
        Callable<V> c = callable;
        if (c != null && state == NEW) {
            V result;
            boolean ran;
            try {
                result = c.call();
                ran = true;
            } catch (Throwable ex) {
                result = null;
                ran = false;
                setException(ex);
            }
            if (ran)
                set(result);
        }
    } finally {
        // runner must be non-null until state is settled to
        // prevent concurrent calls to run()
        runner = null;
        // state must be re-read after nulling runner to prevent
        // leaked interrupts
        int s = state;
        if (s >= INTERRUPTING)
            handlePossibleCancellationInterrupt(s);
    }

}
```

###### set(V v)

将NEW状态置为 COMPLETING ,  将执行结果赋值给全局变量 outcome,  将 COMPLETING 状态置为 NORMAL, 调用 finishCompletion 方法

```
protected void set(V v) {
    if (UNSAFE.compareAndSwapInt(this, stateOffset, NEW, COMPLETING)) {
        outcome = v;
        UNSAFE.putOrderedInt(this, stateOffset, NORMAL); // final state
        finishCompletion();
    }
}
```

###### finishCompletion()

- 取出栈中的 waitNode, 将取得的 q 置空处理获取当前线程t
- 如果当前线程不为空，将q.thread置空，唤醒线程t,防止 get 方法一直阻塞
- 一直取出栈中的 waitNode 重复前面两步操作，直到栈中没有其他的 waitNode 就返回

```
/**
* Removes and signals all waiting threads, invokes done(), and
* nulls out callable.
*/
private void finishCompletion() {

    for (WaitNode q; (q = waiters) != null;) {
        if (UNSAFE.compareAndSwapObject(this, waitersOffset, q, null)) {
            for (;;) {
                Thread t = q.thread;
                if (t != null) {
                    q.thread = null;
                    LockSupport.unpark(t);
                }
                WaitNode next = q.next;
                if (next == null)
                    break;
                q.next = null; // unlink to help gc
                q = next;
            }
            break;
        }
    }

    done();

    callable = null;        // to reduce footprint
}

```

###### get()

使用Get方法返回结果，如果没有完成直接调用 awaitDone(false, 0L)
```
public V get() throws InterruptedException, ExecutionException {
    int s = state;
    if (s <= COMPLETING)
        s = awaitDone(false, 0L);
    return report(s);
}
```

###### awaitDone(boolean timed, long nanos)

- 条件1, 线程被中断，移除当前 waitNode ,抛出异常 InterruptedException
- 条件2，状态大于 COMPLETING, 线程置空，直接返回
- 条件3，状态等于 COMPLETING , 调用 thread.yield() ，先让出CPU，等待状态变成 Normal 或者其他。
- 条件4，q == null ，新建一个 waitNode
- 条件5，没有入队列，将新建的q.next 指向全局变量 waiters
- 条件6，如果超时了取消 waitNode, 直接返回，否则阻塞线程
- 其他情况，直接阻塞调用者线程，直到被唤醒

```
/* 等待完成  */
private int awaitDone(boolean timed, long nanos)
    throws InterruptedException {

    final long deadline = timed ? System.nanoTime() + nanos : 0L;
    WaitNode q = null;
    boolean queued = false;
    for (;;) {
        if (Thread.interrupted()) {
            removeWaiter(q);
            throw new InterruptedException();
        }

        int s = state;
        if (s > COMPLETING) {
            if (q != null)
                q.thread = null;
            return s;
        }
        else if (s == COMPLETING) // cannot time out yet
            Thread.yield();
        else if (q == null)
            q = new WaitNode();
        else if (!queued)
            queued = UNSAFE.compareAndSwapObject(this, waitersOffset,
                                                 q.next = waiters, q);
        else if (timed) {
            nanos = deadline - System.nanoTime();
            if (nanos <= 0L) {
                removeWaiter(q);
                return state;
            }
            LockSupport.parkNanos(this, nanos);
        }
        else
            LockSupport.park(this);
    }
}

```


###### removeWaiter(WaitNode node) 

removeWaiter的工作实际上就是将所有thread为null的节点全部扔掉。

```
private void removeWaiter(WaitNode node) {
    if (node != null) {
        node.thread = null;
        retry:
        for (;;) {          // restart on removeWaiter race
            for (WaitNode pred = null, q = waiters, s; q != null; q = s) {
                s = q.next;
                if (q.thread != null)
                    pred = q;
                else if (pred != null) {
                    pred.next = s;
                    if (pred.thread == null) // check for race
                        continue retry;
                }
                else if (!UNSAFE.compareAndSwapObject(this, waitersOffset,
                                                      q, s))
                    continue retry;
            }
            break;
        }
    }
}
```


###### report(int s) 

如果正常完成就返回结果，否则返回 CancellationException 代表取消， 或者ExecutionException

```
private V report(int s) throws ExecutionException {
    Object x = outcome;
    if (s == NORMAL)
        return (V)x;
    if (s >= CANCELLED)
        throw new CancellationException();
    throw new ExecutionException((Throwable)x);
}
```



