---
layout:     post
title:      "JUC系列(2)-ReentrantLock 源码分析"
subtitle:	"独占模式-公平锁和非公平锁的获取和释放 & AbstractQueuedSynchronizer"
date:       2016-05-22 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-snow.jpg"
tags:
    - 并发编程
---

本文逻辑，按照 ReentrantLock 获取锁这一个场景，逐步分析每一个流程中调用的方法函数。看之前请先阅读这篇文章 [自旋锁-排队自旋锁-MCS锁-CLH锁/](http://www.paraller.com/2015/10/22/转-自旋锁-排队自旋锁-MCS锁-CLH锁/)

#### 公平锁- 获取锁

公平锁的实现，继承自 Sync类，Sync继承自 AbstractQueuedSynchronizer

```
static final class FairSync extends Sync {

    final void lock() {
        acquire(1);
    }

   	...
}
```



###### acquire

1、调用 tryAcquire 获取锁
- 1.1 调用 `!hasQueuedPredecessors()`是否有线程在占有锁，如果是就返回false 
- 1.2 调用`compareAndSetState`，如果state变量时0，就将state变量设置为 1
- 1.3 上面两步执行成功了，就调用 `setExclusiveOwnerThread` 保存当前线程，返回true

2、要是上一步获取锁失败了，就要开始执行 入队列操作，调用 `acquireQueued`
- 2.1 第一步，调用 addWaiter 方法，新建一个Node，然后放在链表的尾部，如果CAS失败，使用自旋的方式重试直到成为尾结点
- 2.2 判断新建的结点前一节点是否为头结点，如果是，就调用tryAcquire方法，如果成功，则将当前的节点node设置为头结点，然后返回false。
- 2.3 
    - 情况(1)前结点是 signal状态，直接返回true，然后阻塞当前线程；等待前一节点唤醒，然后执行2.2
    - 情况(2) 前结点状态是取消状态，则跳过无效的前结点，返回false，继续 2.2 ； 
    - 情况(3) 将前结点的状态设置为 sign,告知前结点如果释放了锁或者取消了，记得通知node,返回false，继续 2.2



```
public final void acquire(int arg) {
    if (!tryAcquire(arg) &&
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg))
        selfInterrupt();
}
```

###### tryAcquire

公平锁版本的尝试获取，不要授权去访问，除非是递归的调用 或者 没有waiter 或者 是第一次调用 , 成功获取返回True
```
protected final boolean tryAcquire(int acquires) {
    final Thread current = Thread.currentThread();
    int c = getState();
    if (c == 0) {
        // CLH 锁的特性，轮询前置结点（在 acquireQueued中轮询 ）。
        if (!hasQueuedPredecessors() &&
            compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(current);
            return true;
        }
    }
    // 重入锁，如果是当前线程, state +1 ，设置新的state值
    else if (current == getExclusiveOwnerThread()) {
        int nextc = c + acquires;
        if (nextc < 0)
            throw new Error("Maximum lock count exceeded");
        setState(nextc);
        return true;
    }
    return false;
}
```

###### hasQueuedPredecessors

查询当前线程之前是否还有其他的线程结点,如果没有就返回false

满足以下任意条件即返回false，表示最优先线程
- 头结点就是尾结点，那么当前线程就是最优先申请锁的线程
- 头结点的下一个结点不为空，并且下一个节点的线程就是当前线程


```
public final boolean hasQueuedPredecessors() {
   
    Node t = tail; // Read fields in reverse initialization order
    Node h = head;
    Node s;
    return h != t &&
        ((s = h.next) == null || s.thread != Thread.currentThread());
}
```

###### compareAndSetState

如果状态值state当前等于 expect ,那么会使用 update 的值去更新状态值， CAS模式
```
protected final boolean compareAndSetState(int expect, int update) {
    // See below for intrinsics setup to support this
    return unsafe.compareAndSwapInt(this, stateOffset, expect, update);
}
```

###### setExclusiveOwnerThread

AbstractOwnableSynchronizer抽象类，用于设置当前的线程
```
public abstract class AbstractOwnableSynchronizer
    implements java.io.Serializable {

    protected AbstractOwnableSynchronizer() { }

    private transient Thread exclusiveOwnerThread;

    protected final void setExclusiveOwnerThread(Thread t) {
        exclusiveOwnerThread = t;
    }

    protected final Thread getExclusiveOwnerThread() {
        return exclusiveOwnerThread;
    }
}
```

###### addWaiter

添加新的Node，保存当前的线程，跟在tail结点之后，结点链接的操作使用CAS模式
```
private Node addWaiter(Node mode) {
    Node node = new Node(Thread.currentThread(), mode);
    // Try the fast path of enq; backup to full enq on failure
    Node pred = tail;
    if (pred != null) {
        node.prev = pred;
        if (compareAndSetTail(pred, node)) {
            pred.next = node;
            return node;
        }
    }
    enq(node);
    return node;
}
```


###### acquireQueued 

在独占模式下，当前线程已经在队列中，使用条件方法来获取；

获取当前线程的Node的前一个结点
- 如果前一个结点是头结点，并且调用tryAcquire方法是否成功，如果是，设置当前结点为头结点，原来的头结点置空，返回false（代表获取锁成功）；
- 循环调用 shouldParkAfterFailedAcquire 找到waitStatus = 0 的结点；然后调用 parkAndCheckInterrupt ，使用LockSupport 阻塞当前线程，等待唤醒；

```
final boolean acquireQueued(final Node node, int arg) {
    boolean failed = true;
    try {
        boolean interrupted = false;
        for (;;) {
            final Node p = node.predecessor();
            if (p == head && tryAcquire(arg)) {
                setHead(node);
                p.next = null; // help GC
                failed = false;
                return interrupted;
            }
            if (shouldParkAfterFailedAcquire(p, node) && parkAndCheckInterrupt())
                interrupted = true;
        }
    } finally {
        if (failed)
            cancelAcquire(node);
    }
}
```

###### shouldParkAfterFailedAcquire

检查和更新获取失败的节点状态。如果线程应该阻塞就返回true，在所有的获取循环中这是主要的控制信号。
```
private static boolean shouldParkAfterFailedAcquire(Node pred, Node node) {
    int ws = pred.waitStatus;
    // Node.SIGNAL = -1
    // Node.CANCELLED = 1
    if (ws == Node.SIGNAL)
        // signal状态代表是前一结点是申请获取锁的线程，等待触发，直接返回true , 以便接着执行 parkAndCheckInterrupt
        return true;
    if (ws > 0) {
       	// 前一节点是取消状态，修改指针，指向pred结点的上一节点，直到不是取消状态
        do {
            node.prev = pred = pred.prev;
        } while (pred.waitStatus > 0);
        pred.next = node;
    } else {
    	// 将前一节点的状态置为 signal ,等待触发的状态
        compareAndSetWaitStatus(pred, ws, Node.SIGNAL);
    }
    return false;
}
```


###### parkAndCheckInterrupt

阻塞当前线程，除非许可可用 ； 当被唤醒的时候，清除当前线程的中断状态。  //LockSupport 

获取失败，被挂起，等待下次唤醒后继续循环尝试获取锁

```
private final boolean parkAndCheckInterrupt() {
    LockSupport.park(this);
    // 执行到这里说明被唤醒，清除当前的中断状态
    return Thread.interrupted();
}
```

###### selfInterrupt

当前线程没有获取成功，中断当前线程。
```
private static void selfInterrupt() {
    Thread.currentThread().interrupt();
}

```


------

#### 公平锁 - 释放锁

```
public void unlock() {
    sync.release(1);
}
```

###### release

独占模式下释放锁，
```
public final boolean release(int arg) {
    if (tryRelease(arg)) {
        Node h = head;
        if (h != null && h.waitStatus != 0)
            unparkSuccessor(h);
        return true;
    }
    return false;
}
```

###### tryRelease

如果不是重入锁，将当前的state设置为0，然后将当前的占取线程设置为NULL，返回true ； 如果是重入锁， state - 1设置新值，返回 false
```
protected final boolean tryRelease(int releases) {
    int c =getState() - releases;
    if (Thread.currentThread() != getExclusiveOwnerThread())
        throw new IllegalMonitorStateException();
    boolean free = false;
    if (c == 0) {
        free = true;
        setExclusiveOwnerThread(null);
    }
    setState(c);
    return free;
}
```

###### unparkSuccessor

唤醒下一个节点，设置 waitStatus = 0； 
```
private void unparkSuccessor(Node node) {
   
    int ws = node.waitStatus;
    if (ws < 0)
        compareAndSetWaitStatus(node, ws, 0);

    Node s = node.next;
    if (s == null || s.waitStatus > 0) {
        s = null;
        for (Node t = tail; t != null && t != node; t = t.prev)
            if (t.waitStatus <= 0)
                s = t;
    }
    if (s != null)
        LockSupport.unpark(s.thread);
}
```


------

#### 非公平锁

非公平锁和公平锁的区别在于执行顺序，优先执行 compareAndSetState ， 而公平锁是在判断当前结点的上一个结点是否头结点，才执行compareAndSetState方法。

```
static final class NonfairSync extends Sync {

    final void lock() {
        if (compareAndSetState(0, 1))
            setExclusiveOwnerThread(Thread.currentThread());
        else
            acquire(1);
    }
}
```


#### 参考网站

[深度解析Java 8：JDK1.8 AbstractQueuedSynchronizer的实现分析（上）](http://www.infoq.com/cn/articles/jdk1.8-abstractqueuedsynchronizer)

[AbstractQueuedSynchronizer框架](https://t.hao0.me/java/2016/04/01/aqs.html)
