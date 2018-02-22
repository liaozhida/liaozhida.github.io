---
layout:     post
title:      "JUC系列(3)-ThreadPoolExecutor 源码解析"
subtitle:    ""
date:       2016-05-22 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-snow.jpg"
tags:
    - 并发编程
    - Java
---


线程池的使用和工作队列(Work Queue)密切相关。 工作者线程 (Work Thread)任务：从工作队列中获取一个任务，执行，完成后返回线程池等待下一个任务。

**优点**主要是：1、重复利用线程，避免创建和销毁的开销； 2、任务到达直接使用现有线程，提高响应性； 3、合适的线程池大小，可以避免线程争用和空闲。

1、本文先从使用场景去查看源码，如果不基于使用案例去查看，基本上看完了也不知道在说什么

2、带着使用场景的一些疑问再去看其他的函数：比如提交的任务大于设定的 corePoolSize 怎么处理，任务如果入队列了什么时候取出来消费等等。。。

#### 线程池的使用场景

```
ExecutorService es = Executors.newFixedThreadPool(100);

Future<String> future = es.submit(new Callable<String>() {

    @Override
    public String call() throws Exception {
        return "hello";
    }

});

String str = future.get();
System.out.println(str);
```

简单的概述一下主要流程： 
- 创建一个 ExecutorService,制定了初始的线程数量和队列
- 当提交一个任务的时候，会判断线程数量，如果小于 corePoolSize 初始数量，直接创建 worker 对象执行业务，如果大于就入队列等到后续的 worker 获取处理， 如果队列满了，并且大于初始线程数量，小于 maximumPoolSize , 创建新的线程执行
- worker 在执行任务完毕的时候，会从队列中获取积累的任务执行，直到完毕，移除这个worker
- 有不符合条件的任务执行情况直接使用 不同的handler 处理

####  继承关系

```
public interface Executor {

    void execute(Runnable command);
}

public interface ExecutorService extends Executor {
 
    void shutdown();
 
    List<Runnable> shutdownNow();
 
    boolean isShutdown();
 
    boolean isTerminated();
 
    boolean awaitTermination(long timeout, TimeUnit unit)
        throws InterruptedException;
 
    <T> Future<T> submit(Callable<T> task);

    //...
}

public interface ScheduledExecutorService extends ExecutorService {

    public ScheduledFuture<?> schedule(Runnable command, long delay, TimeUnit unit);
 
    public <V> ScheduledFuture<V> schedule(Callable<V> callable,  long delay, TimeUnit unit);
 
    public ScheduledFuture<?> scheduleAtFixedRate(Runnable command,long initialDelay,long period,TimeUnit unit);
 
    public ScheduledFuture<?> scheduleWithFixedDelay(Runnable command,long initialDelay,long delay,TimeUnit unit);

}

public abstract class AbstractExecutorService implements ExecutorService

public class ThreadPoolExecutor extends AbstractExecutorService

public class ScheduledThreadPoolExecutor extends ThreadPoolExecutor implements ScheduledExecutorService 

```


#### Executors

列出Executors的几个重点内部类和方法：

###### newXXXThreadPool

创建不同类型的 ExecutorService， 返回 不同入参的`ThreadPoolExecutor`实现类 ，有以下几种
- newFixedThreadPool: 初始线程和最大线程数量一致，超过指定 corePoolSize 线程数量无界阻塞入队列
- newSingleThreadExecutor: 单线程。
- newCachedThreadPool: 初始线程数为0，最大线程数为 Integer.MAX_VALUE，超过指定 corePoolSize 线程数量无界阻塞入队列
- newScheduledThreadPool: 带有时间任务属性的线程池，固定长度，最大线程数为 Integer.MAX_VALUE，超过指定 corePoolSize 线程数量无界阻塞入队列

LinkedBlockingQueue不传构造参数，默认的队列容量为:Integer.MAX_VALUE,也就是无界阻塞队列

```
public class Executors {
    public static ExecutorService newFixedThreadPool(int nThreads) {
        return new ThreadPoolExecutor(nThreads, nThreads,
                                      0L, TimeUnit.MILLISECONDS,
                                      new LinkedBlockingQueue<Runnable>());
}
```



###### DefaultThreadFactory

用来创建一个新的线程；如果没有指定 threadFactory , 会使用默认的DefaultThreadFactory 

```
static class DefaultThreadFactory implements ThreadFactory {

    private static final AtomicInteger poolNumber = new AtomicInteger(1);
    private final ThreadGroup group;
    private final AtomicInteger threadNumber = new AtomicInteger(1);
    private final String namePrefix;

    DefaultThreadFactory() {
        SecurityManager s = System.getSecurityManager();
        group = (s != null) ? s.getThreadGroup() :
                              Thread.currentThread().getThreadGroup();
        namePrefix = "pool-" +
                      poolNumber.getAndIncrement() +
                     "-thread-";
    }

    public Thread newThread(Runnable r) {
        Thread t = new Thread(group, r,
                              namePrefix + threadNumber.getAndIncrement(),
                              0);
        if (t.isDaemon())
            t.setDaemon(false);
        if (t.getPriority() != Thread.NORM_PRIORITY)
            t.setPriority(Thread.NORM_PRIORITY);
        return t;
    }
}
```


###### PrivilegedThreadFactory

需要利用安全策略： 通过 Executor 中的 privilegedThreadFactory， 通过他创建的线程将与创建 privilegedThreadFactory 的线程拥有相同的权限、 AccessControlContext / contextClassLoader

```
static class PrivilegedThreadFactory extends DefaultThreadFactory {
    private final AccessControlContext acc;
    private final ClassLoader ccl;

    PrivilegedThreadFactory() {
        super();
        SecurityManager sm = System.getSecurityManager();
        if (sm != null) {
            sm.checkPermission(SecurityConstants.GET_CLASSLOADER_PERMISSION);
            sm.checkPermission(new RuntimePermission("setContextClassLoader"));
        }
        this.acc = AccessController.getContext();
        this.ccl = Thread.currentThread().getContextClassLoader();
    }

    public Thread newThread(final Runnable r) {
        return super.newThread(new Runnable() {
            public void run() {
                AccessController.doPrivileged(new PrivilegedAction<Void>() {
                    public Void run() {
                        Thread.currentThread().setContextClassLoader(ccl);
                        r.run();
                        return null;
                    }
                }, acc);
            }
        });
    }
}
```

###### callable & RunnableAdapter

返回封装 Runnable 过后的 Callable。

```
public static Callable<Object> callable(Runnable task) {
    if (task == null)
        throw new NullPointerException();
    return new RunnableAdapter<Object>(task, null);
}
 
static final class RunnableAdapter<T> implements Callable<T> {
    final Runnable task;
    final T result;
    RunnableAdapter(Runnable task, T result) {
        this.task = task;
        this.result = result;
    }
    public T call() {
        task.run();
        return result;
    }
}
```





#### AbstractExecutorService

###### submit
```
public <T> Future<T> submit(Callable<T> task) {
    if (task == null) throw new NullPointerException();
    RunnableFuture<T> ftask = newTaskFor(task);
    execute(ftask);
    return ftask;
}
```

###### newTaskFor
```
protected <T> RunnableFuture<T> newTaskFor(Callable<T> callable) {
    return new FutureTask<T>(callable);
}
```



#### ThreadPoolExecutor

###### 构造函数 & 全局变量

`ctl`变量是最重要的属性，他包装了两个概念，工作者worker数量（workerCount） 和 线程池的状态（runState）

**workerCount:** 有效的线程数量 ， 被授权启动的以及没有被授权关闭的worker，

**runState:**

线程池的运行状态：
- RUNNING: 接收新的任务，并且处理队列中的任务
- SHUTDOWN： 不接受新的任务，但是处理队列中存在的任务
- STOP：不接受新的任务，不处理队列中存在的任务
- TIDYING：所有任务呗终止，workerCount 为0，线程转化为 TIDYING 状态会触发 terminated() 钩子方法
- TERMINATED： terminated（） 调用完毕

状态之间的转换：
- RUNNING -> SHUTDOWN ：On invocation of shutdown(), perhaps implicitly in finalize()
- (RUNNING or SHUTDOWN) -> STOP：On invocation of shutdownNow()
- SHUTDOWN -> TIDYING：When both queue and pool are empty
- STOP -> TIDYING：When pool is empty
- TIDYING -> TERMINATED：When the terminated() hook method has completed

Threads waiting in awaitTermination() will return when the state reaches TERMINATED.

**`corePoolSize & maximumPoolSize`**

- 当调用execute 方法的时候，新的任务会被提交，如果当前的线程数量少于 corePoolSize ,新的线程会被创建出来处理这个任务。
- 即使存在空闲的 worker ,  当线程大于 corePoolSize 但是小于 maximumPoolSize ,只有当 workQueue 被填满的情况下才会创建新的线程
- 如果要这两个参数值一致的话，你可以创建 fixed-size 类型的 threadPool
- 可以调用 `setCorePoolSize` 方法在后期调整 corePoolSize 的大小

```

/* ctl主要用来表示当前有多少个任务在进行， 使用CAS来进行操作 */
private final AtomicInteger ctl = new AtomicInteger(ctlOf(RUNNING, 0));

private static final int COUNT_BITS = Integer.SIZE - 3;
private static final int CAPACITY   = (1 << COUNT_BITS) - 1;

/* 标记线程池的生命周期 */
private static final int SHUTDOWN   =  0 << COUNT_BITS;
private static final int RUNNING    = -1 << COUNT_BITS;
private static final int STOP       =  1 << COUNT_BITS;
private static final int TIDYING    =  2 << COUNT_BITS;
private static final int TERMINATED =  3 << COUNT_BITS;

/* 各种位运算的转换操作 */
private static int runStateOf(int c)     { return c & ~CAPACITY; }
private static int workerCountOf(int c)  { return c & CAPACITY; }
private static int ctlOf(int rs, int wc) { return rs | wc; }

private static boolean runStateLessThan(int c, int s) {
    return c < s;
}

private static boolean runStateAtLeast(int c, int s) {
    return c >= s;
}

private static boolean isRunning(int c) {
    return c < SHUTDOWN;
}

private boolean compareAndIncrementWorkerCount(int expect) {
    return ctl.compareAndSet(expect, expect + 1);
}

private boolean compareAndDecrementWorkerCount(int expect) {
    return ctl.compareAndSet(expect, expect - 1);
}

private void decrementWorkerCount() {
    do {} while (! compareAndDecrementWorkerCount(ctl.get()));
}

/* 使用队列来存储任务 */
private final BlockingQueue<Runnable> workQueue;

/* 对线程的生命周期做加锁处理 */
private final ReentrantLock mainLock = new ReentrantLock();

/* 保存workder */
private final HashSet<Worker> workers = new HashSet<Worker>();

/* 加锁条件 */
private final Condition termination = mainLock.newCondition();

/* 当前的最大的线程池数量 */
private int largestPoolSize;

/* 任务完成的数量 */
private long completedTaskCount;

/* 线程的工厂方法 */
private volatile ThreadFactory threadFactory;

/* 线程的异常处理器 */    
private volatile RejectedExecutionHandler handler;

/* 空闲线程的最大维持时间  */
private volatile long keepAliveTime;

/* 用来标记是否让初始线程关闭 ，如果是，在指定的keepalivetime时间过后关闭空闲的初始线程  */
private volatile boolean allowCoreThreadTimeOut;

/* 初始线程数量  */
private volatile int corePoolSize;

/* 最大的线程数量  */    
private volatile int maximumPoolSize;

/* 默认的线程拒绝策略 */
private static final RejectedExecutionHandler defaultHandler =
    new AbortPolicy();

private static final RuntimePermission shutdownPerm = new RuntimePermission("modifyThread");

public ThreadPoolExecutor(int corePoolSize,
                          int maximumPoolSize,
                          long keepAliveTime,
                          TimeUnit unit,
                          BlockingQueue<Runnable> workQueue) {
    this(corePoolSize, maximumPoolSize, keepAliveTime, unit, workQueue,
         Executors.defaultThreadFactory(), defaultHandler);
}

public ThreadPoolExecutor(int corePoolSize,
                          int maximumPoolSize,
                          long keepAliveTime,
                          TimeUnit unit,
                          BlockingQueue<Runnable> workQueue,
                          ThreadFactory threadFactory,
                          RejectedExecutionHandler handler) {
    if (corePoolSize < 0 ||
        maximumPoolSize <= 0 ||
        maximumPoolSize < corePoolSize ||
        keepAliveTime < 0)
        throw new IllegalArgumentException();
    if (workQueue == null || threadFactory == null || handler == null)
        throw new NullPointerException();
    this.corePoolSize = corePoolSize;
    this.maximumPoolSize = maximumPoolSize;
    this.workQueue = workQueue;
    this.keepAliveTime = unit.toNanos(keepAliveTime);
    this.threadFactory = threadFactory;
    this.handler = handler;
}
```

###### execute

任务将会添加一个新的线程来执行，或者从线程池中获取一个旧的线程；如果任务不能被提交执行，有可能是线程池被关闭了或者达到了最大的容量上限，任务将会被RejectedExecutionHandler处理

可以参考 上文开始的 corePoolSize 和 maximumPoolSize的介绍，再看三种处理方式:
- 1、线程数量少于 corePoolSize ,尝试开始一个新的线程运行任务，addWorker 方法自动检测状态和 worker 数量，来防止错误的创建线程
- 2、线程池是运行状态且任务已经成功入队列： 1、double check, 判断线程池是否已经关闭，如果是就移除任务，然后拒绝响应  2、如果worker数量为0，创建空的woker
- 3、如果上一步判断线程池关闭了，再次执行 addWorker 方法，查看线程池的状态是否发生了变更，查看是否有空闲线程可以执行运行worker（因为上一步不能成功入列，所以尝试直接运行）


当提交的任务大于 corePoolSize 的值，处理如下：workQueue.offer(command) ；将任务提交到队列中保存 , 后续的任务处理请参考上文的 `runWorker()`

```
public void execute(Runnable command) {
    if (command == null)
        throw new NullPointerException();

    int c = ctl.get();
    if (workerCountOf(c) < corePoolSize) {
        // 添加新的 worker
        if (addWorker(command, true))
            return;
        c = ctl.get();
    }

    if (isRunning(c) && workQueue.offer(command)) {
        int recheck = ctl.get();
        if (! isRunning(recheck) && remove(command))
            reject(command);
        else if (workerCountOf(recheck) == 0)
            addWorker(null, false);
    }

    else if (!addWorker(command, false))
        reject(command);
}    
```

###### addWorker

加锁的情况下，添加新的worker，启动任务。第一个参数是任务，第二个参数是是否取初始最小线程值

```
private boolean addWorker(Runnable firstTask, boolean core) {
    retry:
    for (;;) {
        int c = ctl.get();
        int rs = runStateOf(c);

        /* 状态异常 直接返回失败 */
        if (rs >= SHUTDOWN && ! (rs == SHUTDOWN && firstTask == null && ! workQueue.isEmpty()))
            return false;

        for (;;) {
            int wc = workerCountOf(c);
            /* 当前 worker 数量大于最大数量 或者 大于初始数量/最大线程数，直接返回失败 */
            if ( wc >= CAPACITY || wc >= (core ? corePoolSize : maximumPoolSize) )
                return false;
            
            /* 原子添加worker 数量+1，跳出循环 */    
            if (compareAndIncrementWorkerCount(c))
                break retry;
            c = ctl.get();  // Re-read ctl
            if (runStateOf(c) != rs)
                continue retry;
            // else CAS failed due to workerCount change; retry inner loop
        }
    }

    boolean workerStarted = false;
    boolean workerAdded = false;
    Worker w = null;
    try {
        final ReentrantLock mainLock = this.mainLock;
        w = new Worker(firstTask);
        final Thread t = w.thread;
        if (t != null) {
             // 全局锁
            mainLock.lock();
            try {
                int c = ctl.get();
                int rs = runStateOf(c);
                
                if (rs < SHUTDOWN ||  (rs == SHUTDOWN && firstTask == null)) {
                    // 再次确认 double check , 线程是否已经启动 ；如果线程池是关闭/运行状态，但是新的工作线程是已启动的（说明有异常情况），则直接抛出异常
                    if (t.isAlive()) 
                        throw new IllegalThreadStateException();
                    workers.add(w);
                    // 修改当前线程池的最大线程数量
                    int s = workers.size();
                    if (s > largestPoolSize)
                        largestPoolSize = s;
                    workerAdded = true;
                }
            } finally {
                mainLock.unlock();
            }
            // 启动work 开始执行任务
            if (workerAdded) {
                t.start();
                workerStarted = true;
            }
        }
    } finally {
        if (! workerStarted)
            addWorkerFailed(w);
    }
    return workerStarted;
}
```

###### Worker

工作单元，负责执行 Future任务。继承自AbstractQueuedSynchronizer ， 线程执行的时候会调用 `runWorker(this)`

```
private final class Worker extends AbstractQueuedSynchronizer implements Runnable
{
    

    final Thread thread;
    // 任务属性
    Runnable firstTask;
    volatile long completedTasks;

    Worker(Runnable firstTask) {
        setState(-1); // inhibit interrupts until runWorker
        this.firstTask = firstTask;
        this.thread = getThreadFactory().newThread(this);
    }

    // 任务执行的入口
    public void run() {
        runWorker(this);
    }


    // 0 代表释放锁的状态
    // 1 代表锁定状态
    protected boolean isHeldExclusively() {
        return getState() != 0;
    }

    protected boolean tryAcquire(int unused) {
        if (compareAndSetState(0, 1)) {
            setExclusiveOwnerThread(Thread.currentThread());
            return true;
        }
        return false;
    }

    protected boolean tryRelease(int unused) {
        setExclusiveOwnerThread(null);
        setState(0);
        return true;
    }
    
    // 锁定独占运行模式
    public void lock()        { acquire(1); }
    public boolean tryLock()  { return tryAcquire(1); }
    public void unlock()      { release(1); }
    public boolean isLocked() { return isHeldExclusively(); }

    void interruptIfStarted() {
        Thread t;
        if (getState() >= 0 && (t = thread) != null && !t.isInterrupted()) {
            try {
                t.interrupt();
            } catch (SecurityException ignore) {
            }
        }
    }
}
```


###### runWorker(Worker w) 

取出 worker 中的任务运行， 执行完成之后,查看是否队列中还存在其他任务，如果有就从队列中取出执行运行任务。当没有任务执行的时候，将 worker 移除。

```
final void runWorker(Worker w) {

    Thread wt = Thread.currentThread();
    // 取出任务
    Runnable task = w.firstTask;
    w.firstTask = null;
    w.unlock();  
    boolean completedAbruptly = true;
    try {
        while (task != null || (task = getTask()) != null) {
            // 上锁 避免任务被并发执行 
            w.lock();
            if ((runStateAtLeast(ctl.get(), STOP) ||  (Thread.interrupted() && runStateAtLeast(ctl.get(), STOP))) 
                    && !wt.isInterrupted())
                wt.interrupt();
            try {
                beforeExecute(wt, task);
                Throwable thrown = null;
                try {
                    task.run();
                } catch (RuntimeException x) {
                    thrown = x; throw x;
                } catch (Error x) {
                    thrown = x; throw x;
                } catch (Throwable x) {
                    thrown = x; throw new Error(x);
                } finally {
                    afterExecute(task, thrown);
                }
            } finally {
                task = null;
                w.completedTasks++;
                w.unlock();
            }
        }
        completedAbruptly = false;
    } finally {
        processWorkerExit(w, completedAbruptly);
    }
}
```

###### getTask()

从任务队列中取出任务返回；主要对超时、状态等条件进行判断，然后返回任务

```
private Runnable getTask() {
    boolean timedOut = false; // Did the last poll() time out?

    retry:
    for (;;) {
        int c = ctl.get();
        int rs = runStateOf(c);

        /* 线程池异常状态 对当前的worker数量进行删减 */
        if (rs >= SHUTDOWN && (rs >= STOP || workQueue.isEmpty())) {
            decrementWorkerCount();
            return null;
        }

        boolean timed;      // Are workers subject to culling?

        for (;;) {
            int wc = workerCountOf(c);
            timed = allowCoreThreadTimeOut || wc > corePoolSize;
            /// 符合运行条件的，跳出循环
            if (wc <= maximumPoolSize && ! (timedOut && timed))
                break;
            if (compareAndDecrementWorkerCount(c))
                return null;
            c = ctl.get();  // Re-read ctl
            if (runStateOf(c) != rs)
                continue retry;
            // else CAS failed due to workerCount change; retry inner loop
        }

        try {
            // 从队列中取出任务返回
            Runnable r = timed ? workQueue.poll(keepAliveTime, TimeUnit.NANOSECONDS) : workQueue.take();
            if (r != null)
                return r;
            timedOut = true;
        } catch (InterruptedException retry) {
            timedOut = false;
        }
    }
}
```


###### processWorkerExit(Worker w, boolean completedAbruptly)

runWorker方法任务执行完成之后的清理工作，统计完成任务的总数，`workers.remove(w)` 移除完成的worker,如果worker数量少于最小线程值，创建空的worker

```
private void processWorkerExit(Worker w, boolean completedAbruptly) {
    if (completedAbruptly) // If abrupt, then workerCount wasn't adjusted
        decrementWorkerCount();

    final ReentrantLock mainLock = this.mainLock;
    mainLock.lock();
    try {
        completedTaskCount += w.completedTasks;
        workers.remove(w);
    } finally {
        mainLock.unlock();
    }

    tryTerminate();

    int c = ctl.get();
    if (runStateLessThan(c, STOP)) {
        if (!completedAbruptly) {
            int min = allowCoreThreadTimeOut ? 0 : corePoolSize;
            if (min == 0 && ! workQueue.isEmpty())
                min = 1;
            if (workerCountOf(c) >= min)
                return; // replacement not needed
        }
        addWorker(null, false);
    }
}
```

###### tryTerminate()

尝试关闭线程池，如果处于这三种情况不需要关闭线程池
- Running 状态
- SHUTDOWN 状态并且任务队列不为空，不能终止
- TIDYING 或者 TERMINATE 状态，说明已经在关闭了 不需要重复关闭

```
final void tryTerminate() {
    for (;;) {
        int c = ctl.get();
       
        if (isRunning(c) ||
            runStateAtLeast(c, TIDYING) ||
            (runStateOf(c) == SHUTDOWN && ! workQueue.isEmpty()))
            return;
        
        if (workerCountOf(c) != 0) { // Eligible to terminate
            interruptIdleWorkers(ONLY_ONE);
            return;
        }

        final ReentrantLock mainLock = this.mainLock;
        mainLock.lock();
        try {
            if (ctl.compareAndSet(c, ctlOf(TIDYING, 0))) {
                try {
                    terminated();
                } finally {
                    ctl.set(ctlOf(TERMINATED, 0));
                    termination.signalAll();
                }
                return;
            }
        } finally {
            mainLock.unlock();
        }
        // else retry on failed CAS
    }
}
```



###### reject(Runnable command)

拒绝新的任务，根据不同的handler执行不同的策略
```
final void reject(Runnable command) {
    handler.rejectedExecution(command, this);
}
```

###### shutdown()

`不接受新任务`，等待开始的任务结束

```
public void shutdown() {
    final ReentrantLock mainLock = this.mainLock;
    mainLock.lock();
    try {
        checkShutdownAccess();
        advanceRunState(SHUTDOWN);
        interruptIdleWorkers();
        onShutdown(); // hook for ScheduledThreadPoolExecutor
    } finally {
        mainLock.unlock();
    }
    tryTerminate();
}
```

###### advanceRunState (int targetState)

如果当前线程池状态小于target的，就更改线程池的状态为 target

```
private void advanceRunState(int targetState) {
    for (;;) {
        int c = ctl.get();
        if (runStateAtLeast(c, targetState) ||
            ctl.compareAndSet(c, ctlOf(targetState, workerCountOf(c))))
            break;
    }
}
```

###### interruptIdleWorkers(boolean onlyOne)

中断空闲的worker， 因为运行的 worker 会获取到锁， w.tryLock()将会处于等待状态，所以能被中断的都是空闲的
```
private void interruptIdleWorkers(boolean onlyOne) {
    final ReentrantLock mainLock = this.mainLock;
    mainLock.lock();
    try {
        for (Worker w : workers) {
            Thread t = w.thread;
            if (!t.isInterrupted() && w.tryLock()) {
                try {
                    t.interrupt();
                } catch (SecurityException ignore) {
                } finally {
                    w.unlock();
                }
            }
            if (onlyOne)
                break;
        }
    } finally {
        mainLock.unlock();
    }
}
```


###### shutdownNow()

尝试取消所有开始的任务，不再启动`尚未开始`（可能是已接受的新任务）执行的任务。

```
public List<Runnable> shutdownNow() {
    List<Runnable> tasks;
    final ReentrantLock mainLock = this.mainLock;
    mainLock.lock();
    try {
        checkShutdownAccess();
        advanceRunState(STOP);
        interruptWorkers();
        tasks = drainQueue();
    } finally {
        mainLock.unlock();
    }
    tryTerminate();
    return tasks;
}
```

###### interruptWorkers()

中断所有的线程，即使是活跃的线程
```
private void interruptWorkers() {
    final ReentrantLock mainLock = this.mainLock;
    mainLock.lock();
    try {
        for (Worker w : workers)
            w.interruptIfStarted();
    } finally {
        mainLock.unlock();
    }
}
```


```
void interruptIfStarted() {
    Thread t;
    if (getState() >= 0 && (t = thread) != null && !t.isInterrupted()) {
        try {
            t.interrupt();
        } catch (SecurityException ignore) {
        }
    }
}

```

###### drainQueue()

将队列中未处理的任务取出，放置在list中（用于后续的处理），DelayQueue或其他的一些队列调用 drainTo方法可能会失败，需要手动的调用添加流程

```
private List<Runnable> drainQueue() {
    BlockingQueue<Runnable> q = workQueue;
    List<Runnable> taskList = new ArrayList<Runnable>();
    q.drainTo(taskList);
    if (!q.isEmpty()) {
        for (Runnable r : q.toArray(new Runnable[0])) {
            if (q.remove(r))
                taskList.add(r);
        }
    }
    return taskList;
}
```



#### CallerRunsPolicy

判断线程池是否关闭，如果没有，就在当前主线程中执行任务，阻塞新的任务
```
 public static class CallerRunsPolicy implements RejectedExecutionHandler {
       
        public CallerRunsPolicy() { }

        public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
            if (!e.isShutdown()) {
                r.run();
            }
        }
    }

```


#### AbortPolicy
抛出异常RejectedExecutionException。
```
public static class AbortPolicy implements RejectedExecutionHandler {

    public AbortPolicy() { }

    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        throw new RejectedExecutionException("Task " + r.toString() +
                                             " rejected from " +
                                             e.toString());
    }
}
```

#### DiscardPolicy

悄无声息的丢弃任务

```
public static class DiscardPolicy implements RejectedExecutionHandler {

    public DiscardPolicy() { }

    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
    }
}	
```

#### DiscardOldestPolicy

丢弃旧的任务

```
public static class DiscardOldestPolicy implements RejectedExecutionHandler {

    public DiscardOldestPolicy() { }

    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        if (!e.isShutdown()) {
            e.getQueue().poll();
            e.execute(r);
        }
    }
}
```



#### 参考网站

[ThreadPoolExecutor源码学习笔记](http://extremej.itscoder.com/threadpoolexecutor_source/)

