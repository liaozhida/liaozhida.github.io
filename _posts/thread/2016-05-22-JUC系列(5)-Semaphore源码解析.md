---
layout:     post
title:      "JUC系列(5)-Semaphore源码解析"
subtitle:	"信号量 AbstractQueuedSynchronizer 共享模式"
date:       2016-05-22 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-snow.jpg"
tags:
    - 并发编程
---



看这篇文章前请先阅读《JUC系列(2)-ReentrantLock源码分析》， 信号量主要用来控制同时操作某个资源的并发数量，可以用来实现资源池等。可以理解为 acquire 是消费许可，release是创建许可。

主要流程很好理解：
- 创建一定数量的许可 
- 不断的消耗许可，当许可被消耗完毕，后面的线程进行队列排队，设置头节点
- 当有许可被释放的时候，唤醒节点进行许可申请。重置 state 许可数量


#### 使用场景
```
Semaphore semaphore = new Semaphore(5);
		
semaphore.acquire();

System.out.println("todo");

semaphore.release();
```


直接进入主题，查看源码可以看到和 ReentrantLock 的代码非常类似，一个静态内部类 `Sync`继承自 AbstractQueuedSynchronizer ，有两个版本，公平锁 `FairSync` 非公平锁 `NonfairSync`;
通过 acquire() 和 release() 方法理解源码。


`new Semaphore(5)`  ,将AbstractQueuedSynchronizer 的state变量值设为5，代表允许五个线程并发操作
```
abstract static class Sync extends AbstractQueuedSynchronizer {

    Sync(int permits) {
        setState(permits);
    }
    ...
}
```

acquire()
```
public void acquire() throws InterruptedException {
    sync.acquireSharedInterruptibly(1);
}
```

###### AbstractQueuedSynchronizer#acquireSharedInterruptibly

获取共享锁，支持响应中断，如果获取锁失败，则调用 doAcquireSharedInterruptibly 
```
public final void acquireSharedInterruptibly(int arg)
        throws InterruptedException {
    if (Thread.interrupted())
        throw new InterruptedException();
    if (tryAcquireShared(arg) < 0)
        doAcquireSharedInterruptibly(arg);
}
```

###### FairSync#tryAcquireShared

- 查询当前线程之前是否还有其他的线程节点,如果有就返回true ，返回 -1 
- 如果获取了锁，剩余的许可数量小于0，获取共享锁失败，则返回剩余数量； 如果剩余许可大于等于0，并且 state的CAS操作成功，说明获取共享锁成功则返回一个许可数量；

```

protected int tryAcquireShared(int acquires) {
    for (;;) {
        if (hasQueuedPredecessors())
            return -1;
        int available = getState();
        int remaining = available - acquires;
        if (remaining < 0 ||
            compareAndSetState(available, remaining))   // 如果state值为 available,就使用 remaining 覆盖state值
            return remaining;
    }
}
```


###### AbstractQueuedSynchronizer#doAcquireSharedInterruptibly 

按照AQS的逻辑，获取锁失败的线程需要进行排队。

- 创建一个node(共享类型)，放置在链表尾部 
- 获取node的前驱节点，如果前驱节点是头节点，那就再尝试获取一次锁，**成功后就设置为头节点**和传播状态，（setHeadAndPropagate）返回
- 如果node的前驱节点不是头节点，则阻塞当前线程。

```
private void doAcquireSharedInterruptibly(int arg)
    throws InterruptedException {
    final Node node = addWaiter(Node.SHARED);
    boolean failed = true;
    try {
        for (;;) {
            final Node p = node.predecessor();
            if (p == head) {
                int r = tryAcquireShared(arg);
                if (r >= 0) {
                    setHeadAndPropagate(node, r);
                    p.next = null; // help GC
                    failed = false;
                    return;
                }
            }
            if (shouldParkAfterFailedAcquire(p, node) && parkAndCheckInterrupt())
                throw new InterruptedException();
        }
    } finally {
        if (failed)
            cancelAcquire(node);
    }
}
```




###### AbstractQueuedSynchronizer#setHeadAndPropagate

- 设置头节点
- 如果剩余许可大于0 或者 原来的头节点为NULL 或者  原来的头节点状态不是取消状态 ，并且node节点的下一个节点为NULL，调用 doReleaseShared()
- 如果剩余许可大于0 或者 原来的头节点为NULL 或者  原来的头节点状态不是取消状态 ，并且node节点的下一个节点为共享类型的节点，调用 doReleaseShared()
 
Note: s.isShared() 为true，会调用 doReleaseShared()方法接触下一个节点的阻塞状态，对于独占功能来说，有且只有一个线程能够获取锁，但是对于共享功能来说，共享的状态是可以被共享的，也就是意味着其他AQS队列中的其他节点也应能第一时间知道状态的变化 

```
private void setHeadAndPropagate(Node node, int propagate) {
    Node h = head; // Record old head for check below
    setHead(node);
    if (propagate > 0 || h == null || h.waitStatus < 0) {
        Node s = node.next;
        if (s == null || s.isShared())
            doReleaseShared();
    }
}
```


###### AbstractQueuedSynchronizer#doReleaseShared

取出头节点，如果状态是 Signal,唤醒下一个节点, 下一个节点被唤醒之后，重复 doAcquireSharedInterruptibly 方法申请许可


```
private void doReleaseShared() {
    for (;;) {
        Node h = head;
        if (h != null && h != tail) {
            int ws = h.waitStatus;
            if (ws == Node.SIGNAL) {
                if (!compareAndSetWaitStatus(h, Node.SIGNAL, 0))
                    continue;           
                unparkSuccessor(h);
            }
            else if (ws == 0 && !compareAndSetWaitStatus(h, 0, Node.PROPAGATE))
                continue;                // loop on failed CAS
        }
        if (h == head)                   // loop if head changed
            break;
    }
}
```


###### AbstractQueuedSynchronizer#parkAndCheckInterrupt


```
private final boolean parkAndCheckInterrupt() {
    LockSupport.park(this);
    return Thread.interrupted();
}
```


###### AbstractQueuedSynchronizer#release()

释放许可，可以理解为生成新的可用许可

```

public void release() {
    sync.releaseShared(1);
}

```


###### AbstractQueuedSynchronizer#releaseShared

```
public final boolean releaseShared(int arg) {
    if (tryReleaseShared(arg)) {
        doReleaseShared();
        return true;
    }
    return false;
}
```


######  Semaphore#tryReleaseShared

子类实现，将可用许可+1， 判断是否有溢出， 然后循环CAS重置 state值。

```
protected final boolean tryReleaseShared(int releases) {
    for (;;) {
        int current = getState();
        int next = current + releases;
        if (next < current) // overflow
            throw new Error("Maximum permit count exceeded");
        if (compareAndSetState(current, next))
            return true;
    }
}
```







