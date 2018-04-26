---
layout:     post
title:      "JUC系列(1)-AbstractQueuedSynchronizer源码分析"
subtitle:	""
date:       2016-10-23 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-snow.jpg"
tags:
    - 并发编程
---


#### 前言

AbstractQueuedSynchronizer 是很多同步工具的公共类，对于线程的控制基于 CLH 思想，可以参考这篇文章 [自旋锁-排队自旋锁-MCS锁-CLH锁/](http://www.paraller.com/2015/10/22/转-自旋锁-排队自旋锁-MCS锁-CLH锁/)，先了解一下几种锁的异同，简单的说CLH锁也是一种基于链表的可扩展、高性能、公平的自旋锁，它不断轮询前驱的状态，如果发现前驱释放了锁就结束自旋。

现在逐一的根据源码分析

#### 继承关系

AbstractQueuedSynchronizer作为一个抽象类，定义了基本的操作和数据结构，子类根据它来实现各种同步类。

```
abstract class AbstractQueuedSynchronizer  extends AbstractOwnableSynchronizer
```

AbstractOwnableSynchronizer 类只有getter/setter 方法，只要保存当前正在运行的线程。
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


#### Node结点

AbstractQueuedSynchronizer 内部有一个 Node 类，这个类称为节点，每个节点都有双向指针， 串联成链表的数据结构。

每个节点有一个状态变量 waitStatus ，一个线程属性  thread , 表示结点类型的常量 SHARED 共享型 EXCLUSIVE 独占型，独占型请参考往期文章 ReentrantLock的源码分析， 共享型请参考 Semaphore源码分析。

默认的 waitStatus 是0，每个结点有几种状态：
- CANCELLED ： 结点是被取消的状态，因为超时或者被中断的原因，到达这个状态之后将不再改变，特别说明一下，取消状态的节点是不会被阻塞的。
- SIGNAL：当前结点的后一个结点是阻塞状态（LockSupport.park）,所以当前结点如果释放了锁或者被取消了，要解除后续结点的阻塞状态。为了避免发生竞态条件，acquire 方法必须首先表明他们需要一个信号，然后再去尝试原子的 acquire ，然后返回失败或者直接阻塞。
- CONDITION：当前结点在条件队列中，在状态没有修改之前，他不会被用作同步队列的节点，此时状态将被设置为0（这个状态没有任何用处，只是一个简单的机制）
- PROPAGATE：在共享类型的结点中用到，代表当前结点的状态需要传递给下一个结点

```
static final class Node {
        
        static final Node SHARED = new Node();
        static final Node EXCLUSIVE = null;

        static final int CANCELLED =  1;
        static final int SIGNAL    = -1;
        static final int CONDITION = -2;
        static final int PROPAGATE = -3;

        volatile int waitStatus;

        volatile Node prev;

        volatile Node next;

        volatile Thread thread;
 
        Node nextWaiter;

        final boolean isShared() {
            return nextWaiter == SHARED;
        }
 
        final Node predecessor() throws NullPointerException {
            Node p = prev;
            if (p == null)
                throw new NullPointerException();
            else
                return p;
        }

        Node() {    // 用来初始化头结点或者用作共享结点类型的标志
        }

        Node(Thread thread, Node mode) {     // 被addWaiter方法使用
            this.nextWaiter = mode;
            this.thread = thread;
        }

        Node(Thread thread, int waitStatus) { // 被Condition使用
            this.waitStatus = waitStatus;
            this.thread = thread;
        }
    }

```

####  AbstractQueuedSynchronizer 的几个关键属性：
- head / tail  代表当前 aqs 的头尾结点，不解释
- state, 在不同的场合有不同的意思，在 ReentrantLock 中 state > 0 代表已经有线程获取了锁； 在信号量中代表有几个许可 ； 对该变量的操作都必须使用 CAS 模式

```
private transient volatile Node head;
 
private transient volatile Node tail;

private volatile int state;

protected final boolean compareAndSetState(int expect, int update) {
    // See below for intrinsics setup to support this
    return unsafe.compareAndSwapInt(this, stateOffset, expect, update);
}
```


#### 几个基本操作：


###### enq
将指定的节点添加到链表尾部，如果不存在尾部，则创建一个节点作为尾部；指定节点的前指针指向尾部节点，然后compareAndSetTail将自己变成尾结点

如果失败，通过自旋的方式修复
```
private Node enq(final Node node) {
    for (;;) {
        Node t = tail;
        if (t == null) { // Must initialize
            if (compareAndSetHead(new Node()))
                tail = head;
        } else {
            node.prev = t;
            if (compareAndSetTail(t, node)) {
                t.next = node;
                return t;
            }
        }
    }
}
```

###### addWaiter
添加waiter, 作用和上面的操作类似，不同点在于为Node添加线程信息。
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

###### unparkSuccessor
解除指定节点后续Node的阻塞状态，
- 将自身的 waitStatus 状态设置为初始状态
- 取出下一个节点，如果取出来的节点为空或者是取消状态的，则从尾部节点开始遍历，找到离当前结点最近且非取消状态的结点，然后解除结点线程的阻塞状态

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

###### doReleaseShared
暂时不理解，等分析到后面使用这个方法的子类再倒回来补充
```
private void doReleaseShared() {
    for (;;) {
        Node h = head;
        if (h != null && h != tail) {
            int ws = h.waitStatus;
            if (ws == Node.SIGNAL) {
                if (!compareAndSetWaitStatus(h, Node.SIGNAL, 0))
                    continue;            // loop to recheck cases
                unparkSuccessor(h);
            }
            else if (ws == 0 &&
                     !compareAndSetWaitStatus(h, 0, Node.PROPAGATE))
                continue;                // loop on failed CAS
        }
        if (h == head)                   // loop if head changed
            break;
    }
}
```

###### setHeadAndPropagate
暂时不理解，等分析到后面使用这个方法的子类再倒回来补充

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

###### cancelAcquire
取消获取锁的逻辑
```
private void cancelAcquire(Node node) {
    if (node == null)
        return;

    node.thread = null;

    // 跳过取消状态的Node，当前node的前指针指向不是取消状态的结点
    Node pred = node.prev;
    while (pred.waitStatus > 0)
        node.prev = pred = pred.prev;

    
	// 临时变量 代表 node 
    Node predNext = pred.next;

    // Can use unconditional write instead of CAS here.
    // After this atomic step, other Nodes can skip past us.
    // Before, we are free of interference from other threads.
    node.waitStatus = Node.CANCELLED;

    // 如果node是尾结点，则使用node的前结点代替node结点   ， 然后将node置换为空
    if (node == tail && compareAndSetTail(node, pred)) {
        compareAndSetNext(pred, predNext, null);
    } else {
        // If successor needs signal, try to set pred's next-link
        // so it will get one. Otherwise wake it up to propagate.
        int ws;
        if (pred != head &&
            ((ws = pred.waitStatus) == Node.SIGNAL ||
             (ws <= 0 && compareAndSetWaitStatus(pred, ws, Node.SIGNAL))) &&
            pred.thread != null) {
            Node next = node.next;
            if (next != null && next.waitStatus <= 0)
                compareAndSetNext(pred, predNext, next);
        } else {
            unparkSuccessor(node);
        }

        node.next = node; // help GC
    }
}
```

###### shouldParkAfterFailedAcquire
获取锁失败，判断是否需要将线程阻塞
- 如果当前结点node的前一节点的状态是 signal , 则返回true，并接下来的parkAndCheckInterrupt将当前线程阻塞。
- 如果前一节点的状态是取消，则node的前指针指向一个状态正常的前节点，返回false
- 如果是其他状态，则将前一节点的状态置为 signal ,返回false

```
private static boolean shouldParkAfterFailedAcquire(Node pred, Node node) {
    int ws = pred.waitStatus;
    if (ws == Node.SIGNAL)
        return true;
    if (ws > 0) {
 
        do {
            node.prev = pred = pred.prev;
        } while (pred.waitStatus > 0);
        pred.next = node;
    } else {
        compareAndSetWaitStatus(pred, ws, Node.SIGNAL);
    }
    return false;
}
```

###### selfInterrupt
当前线程触发中断操作
```
private static void selfInterrupt() {
    Thread.currentThread().interrupt();
}
```

###### parkAndCheckInterrupt
调用 LockSupport.park 操作阻塞当前线程
```
private final boolean parkAndCheckInterrupt() {
    LockSupport.park(this);
    return Thread.interrupted();
}
```

###### acquireQueued
申请锁队列。
- 1、取出指定node节点的前一节点，如果是头结点，接着调用 tryAcquire 方法查看当前线程是否是最优先的线程，并且 state 的CAS操作是否成功，如果成功就将当前结点设置为头结点
- 2、如果不是头结点，调用shouldParkAfterFailedAcquire查看前一节点的状态是否是 signal, 如果是就阻塞当前线程，如果不是继续循环第一步
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
            if (shouldParkAfterFailedAcquire(p, node) &&
                parkAndCheckInterrupt())
                interrupted = true;
        }
    } finally {
        if (failed)
            cancelAcquire(node);
    }
}
```

###### doAcquireInterruptibly
获取锁，支持响应中断
```
private void doAcquireInterruptibly(int arg)
    throws InterruptedException {
    final Node node = addWaiter(Node.EXCLUSIVE);
    boolean failed = true;
    try {
        for (;;) {
            final Node p = node.predecessor();
            if (p == head && tryAcquire(arg)) {
                setHead(node);
                p.next = null; // help GC
                failed = false;
                return;
            }
            if (shouldParkAfterFailedAcquire(p, node) &&
                parkAndCheckInterrupt())
                throw new InterruptedException();
        }
    } finally {
        if (failed)
            cancelAcquire(node);
    }
}
```

###### doAcquireShared
```
private void doAcquireShared(int arg) {
    final Node node = addWaiter(Node.SHARED);
    boolean failed = true;
    try {
        boolean interrupted = false;
        for (;;) {
            final Node p = node.predecessor();
            if (p == head) {
                int r = tryAcquireShared(arg);
                if (r >= 0) {
                    setHeadAndPropagate(node, r);
                    p.next = null; // help GC
                    if (interrupted)
                        selfInterrupt();
                    failed = false;
                    return;
                }
            }
            if (shouldParkAfterFailedAcquire(p, node) &&
                parkAndCheckInterrupt())
                interrupted = true;
        }
    } finally {
        if (failed)
            cancelAcquire(node);
    }
}

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
            if (shouldParkAfterFailedAcquire(p, node) &&
                parkAndCheckInterrupt())
                throw new InterruptedException();
        }
    } finally {
        if (failed)
            cancelAcquire(node);
    }
}
```


###### 所有的实现在不同的子类中
```
protected boolean tryAcquire(int arg) {
    throw new UnsupportedOperationException();
}
 
protected boolean tryRelease(int arg) {
    throw new UnsupportedOperationException();
}
 
protected int tryAcquireShared(int arg) {
    throw new UnsupportedOperationException();
}

protected boolean tryReleaseShared(int arg) {
    throw new UnsupportedOperationException();
}

protected boolean isHeldExclusively() {
    throw new UnsupportedOperationException();
}
```

###### release
释放锁：找到链表中的头结点，然后调用unparkSuccessor解除后驱结点的阻塞状态
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

###### 剩下的都是一些工具方法

提供给所有子类使用，就不解释了，大家可以预览一下:
```
public final int getQueueLength() {
    int n = 0;
    for (Node p = tail; p != null; p = p.prev) {
        if (p.thread != null)
            ++n;
    }
    return n;
}

... 
```

