---
layout:     post
title:      "ReentrantLock源码分析"
subtitle:	"独占模式-公平锁和非公平锁的获取和释放 & AbstractQueueSynchronizer"
date:       2016-05-22 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-snow.jpg"
tags:
    - 并发编程
---

#### 公平锁- 获取锁

公平锁的实现，继承自 Sync类，Sync继承自 AbstractQueueSynchronizer

```
static final class FairSync extends Sync {

    final void lock() {
        acquire(1);
    }

   	...
}
```


###### acquire

独占模式的获取，忽略中断。至少调用了一次tryAcquire方法,如果成功就返回，否则线程会入队列，可能会不断的阻塞和解除阻塞状态，直到成功。 tryAcquire返回true 或者 acquireQueued返回false, 就代表获取成功
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

查询是否有线程比当前线程等待获取的时间还要长 ； 查询头结点的下一个节点是否当前节点，如果是返回false , 如果不是返回 True 
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
        // 前一个结点在等待触发，返回true，上层调用继续循环
        return true;
    if (ws > 0) {
       	// 前一个结点为取消状态，将当前的节点的前指针指向下一个前结点
        do {
            node.prev = pred = pred.prev;
        } while (pred.waitStatus > 0);
        pred.next = node;
    } else {
    	waitStatus 为0 或者 PROPAGATE，结点需要一个触发信号。
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
