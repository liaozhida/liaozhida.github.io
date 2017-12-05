---
layout:     post
title:      "引用(1) - Reference和ReferenceQueue源码分析"
subtitle:	""
date:       2016-10-23 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-snow.jpg"
tags:
    - Java
---

看文章前个人建议先把源码看一遍，带着疑问去阅读会好一点。我自己在看这个类的时候也有好多东西不明白，参考了几个大神的文章，重新整理了一遍。


## Reference

所有引用对象的抽象基类，为所有的引用对象定义了通用的操作。因为引用对象的实现在与垃圾收集器存在紧密合作

先看 Reference 每个域的作用，主要有以下几个

```
private T referent;         /* Treated specially by GC */

ReferenceQueue<? super T> queue;

Reference next;

transient private Reference<T> discovered;  /* used by VM */

static private class Lock { };

private static Lock lock = new Lock();

private static Reference pending = null;
```

#### reference状态的表示方式

在看 reference注释的时候，标注了几个状态码，并做了解释。但是我们并没有在类中发现类似 state 的状态变量， 因为jvm并不需要定义状态值来判断相应引用的状态处于哪个状态,只需要通过计算next和queue即可进行判断。一个引用实例有四种内部状态：

###### Active：
被垃圾收集器特殊对待的对象，有时候在收集器检测它的可达性状态后会改变对象的状态，可以转换成 pending 和 Inactive 状态，主要取决于被创建的时候是否在 ReferenceQueue 队列中注册。 
正常情况下他也会被添加到 pending-Reference 集合中。新创建的实例是 Active状态。

###### Pending：
未被注册的实例不存在这个状态。当垃圾回收器检测到可达性发生变化（变为不可达时），如果queue不为空，则加入到 Reference的静态变量pending的队列中，并将状态设置为 Pending。 元素在 pending-Reference 集合中，等待Reference-handler 线程将它入队列。

###### Enqueued： 
当实例被创建，并且之后入队列了就是这个状态。当实例被移除 ReferenceQueue 队列， 他就是 Inactive 状态，没被注册的实例不存在这个状态

###### Inactive： 
当垃圾回收器检测到可达性发生变化（变为不可达时），如果 queue == ReferenceQueue.Null的话，状态直接变为 InActive,实例进入这个状态不会再有任何改变。

###### JVM通过计算next和queue判断：

- Active: `next = null`;

- Pending: `queue = ReferenceQueue`  `补充。。`

- Enqueue: 进入队列中的Reference 中的 next 为队列中一个引用，或等于this(表示当前引用为最后一个), `queue = ReferenceQueue.ENQUEUE。`
    
- InActive： `queue = ReferenceQueue.NULL; next = this`


>* A Reference instance is in one of four possible internal states:
     *
     *     Active: Subject to special treatment by the garbage collector.  Some
     *     time after the collector detects that the reachability of the
     *     referent has changed to the appropriate state, it changes the
     *     instance's state to either Pending or Inactive, depending upon
     *     whether or not the instance was registered with a queue when it was
     *     created.  In the former case it also adds the instance to the
     *     pending-Reference list.  Newly-created instances are Active.
     *
     *     Pending: An element of the pending-Reference list, waiting to be
     *     enqueued by the Reference-handler thread.  Unregistered instances
     *     are never in this state.
     *
     *     Enqueued: An element of the queue with which the instance was
     *     registered when it was created.  When an instance is removed from
     *     its ReferenceQueue, it is made Inactive.  Unregistered instances are
     *     never in this state.
     *
     *     Inactive: Nothing more to do.  Once an instance becomes Inactive its
     *     state will never change again.
     *
     * The state is encoded in the queue and next fields as follows:
     *
     *     Active: queue = ReferenceQueue with which instance is registered, or
     *     ReferenceQueue.NULL if it was not registered with a queue; next =
     *     null.
     *
     *     Pending: queue = ReferenceQueue with which instance is registered;
     *     next = Following instance in queue, or this if at end of list.
     *
     *     Enqueued: queue = ReferenceQueue.ENQUEUED; next = Following instance
     *     in queue, or this if at end of list.
     *
     *     Inactive: queue = ReferenceQueue.NULL; next = this.
     *
     * With this scheme the collector need only examine the next field in order
     * to determine whether a Reference instance requires special treatment: If
     * the next field is null then the instance is active; if it is non-null,
     * then the collector should treat the instance normally.
     *
     * To ensure that concurrent collector can discover active Reference
     * objects without interfering with application threads that may apply
     * the enqueue() method to those objects, collectors should link
     * discovered objects through the discovered field.
     */


#### T referent

referent代表的是引用的对象，比如 `Object obj = new Object()` ,  `new Object()`，为引用的对象描述当前引用所引用的实际对象,正如在注解中所述,其会认真对待.即什么时候会被回收,如果一旦被回收,则会直接置为null,而外部程序可通过通过引用对象本身(而不是referent)了解到,回收行为的产生.

referent表示其引用的对象,即我们在构造的时候,需要被包装在其中的对象.对象即将被回收的定义，即此对象除了被reference引用之外没有其它引用了(并非确实没有被引用,而是gcRoot可达性不可达,以避免循环引用的问题).

#### ReferenceQueue<? super T> queue

每个Reference对象都有一个对应的ReferenceQueue，用来存储Reference对象。一个ReferenceQueue对象可以被多个Reference共享。

> “ Reference queues, to which registered reference objects are appended by the garbage collector after the appropriate reachability changes are detected. ”

当被引用的对象被GC回收之后，GC会把Reference对象添加到队列中。因此，可以这样理解，在队列中的Reference对象，它们引用的对象被GC回收。而不在队列中的，它们引用的对象则还没有被GC回收。这个队列的存在，可以帮助开发者执行一些与被引用对象相关联的数据清理的动作。

如果在创建ReferenceQueue的时候没有指定队列，这个Reference就会使用默认的ReferenceQueue.Null队列，生命周期直接由  Active 进入 Inactive：
queue即是对象即被回收时所要通知的队列,当对象即被回收时,整个reference对象会被放到queue里面,然后外部程序即可通过监控这个queue拿到相应的数据了.

ReferenceQueue类型的queue 是一个后入先出的队列，先看看他的源码和关键的几个方法:

###### 全局域

```
static ReferenceQueue NULL = new Null();
static ReferenceQueue ENQUEUED = new Null();
```

当引用对象被移除队列的时候，对象的 queue 将会重置为空值的 ReferenceQueue

当引用对象入列的时候，对象的 queue 将会置为空值的ENQUEUED，标志这个对象已经被处理，避免重复操作。

###### enqueue()

```
boolean enqueue(Reference<? extends T> r) { /* Called only by Reference class */
    synchronized (r) {
        if (r.queue == ENQUEUED) return false;
        synchronized (lock) {
            r.queue = ENQUEUED;
            r.next = (head == null) ? r : head;
            head = r;
            queueLength++;
            if (r instanceof FinalReference) {
                sun.misc.VM.addFinalRefCount(1);
            }
            lock.notifyAll();
            return true;
        }
    }
}
```

这个队列并没有相对应的Node数据结构，其自己仅存储当前的head节点，队列的维护主要依靠 Reference的 next 节点来完成。enqueue 方法的示意图如下所示

![image](queue1)

###### reallyPoll()

将引用对象从队列中移除，后入先出，没什么好讲的

```
private Reference<? extends T> reallyPoll() {       /* Must hold lock */
    if (head != null) {
        Reference<? extends T> r = head;
        head = (r.next == r) ? null : r.next;
        r.queue = NULL;
        r.next = r;
        queueLength--;
        if (r instanceof FinalReference) {
            sun.misc.VM.addFinalRefCount(-1);
        }
        return r;
    }
    return null;
}
```

###### poll()

轮询查看是否队列中有元素可用，如果有直接返回，否则返回null
```

public Reference<? extends T> poll() {
    if (head == null)
        return null;
    synchronized (lock) {
        return reallyPoll();
    }
}
```

###### remove

从队列中移除一个最近的引用对象，在规定时间内将一直阻塞直到有可用的元素返回

```
public Reference<? extends T> remove(long timeout)  throws IllegalArgumentException, InterruptedException
{
    if (timeout < 0) {
        throw new IllegalArgumentException("Negative timeout value");
    }
    synchronized (lock) {
        Reference<? extends T> r = reallyPoll();
        if (r != null) return r;
        for (;;) {
            lock.wait(timeout);
            r = reallyPoll();
            if (r != null) return r;
            if (timeout != 0) return null;
        }
    }
}
```


#### Reference next

在queue中 描述当前引用节点所存储的下一个节点.但next仅在放到queue中才会有意义.用于维护 queue 链表

为了描述相应的状态值,在放到队列当中后,其queue就不会再引用初始化时注册的引用队列了.而是引用一个特殊null值的ENQUEUED.因为已经放到队列当中,并且不会再次放到队列当中.


#### Lock lock = new Lock();

为了避免对变量同时进行操作，设置锁来确保并发异常。


#### Reference<T> discovered;  

使用关键字 `transient` 修饰，根据注释可以看到只要是给 VM 参考使用的。

表示要处理的对象的下一个对象.即可以理解要处理的对象也是一个链表,通过discovered进行排队

未完。。。


#### Reference pending 

**注意这个pending队列是一个静态类变量。**可以理解为整个VM维护着一个pending队列。

此队列维护着需要进入引用队列的引用，由JVM虚拟机垃圾回收器在检测到被引用指向的对象可达性发生改变后，如果该对象的引用（Referecnce）注册了引用队列(ReferenceQueue),则JVM虚拟机垃圾收集器会将该引用加入到pending队列

同时,另一个字段discovered,表示要处理的对象的下一个对象.即可以理解要处理的对象也是一个链表,通过discovered进行排队,这边只需要不停地拿到pending,然后再通过discovered不断地拿到下一个对象即可.因为这个pending对象,两个线程都可能访问,因此需要加锁处理.

pending是由jvm来赋值的，当Reference内部的referent对象的可达状态改变时，jvm会将Reference对象放入pending链表。

#### pending & discovered

private static Reference pending = null;

//这个对象，定义为 private，并且全局没有任何给它赋值的地方，

再看discovered，同样为private，上下文也没有任何地方使用它

transient private Reference<T> discovered;   
//看到了它的注释也明确写着是给VM用的。

上面两个变量对应在VM中的调用，可以参考openjdk中的hotspot源码，在hotspot/src/share/vm/memory/referenceProcessor.cpp 的ReferenceProcessor::discover_reference 方法。(根据此方法的注释由了解到虚拟机在对Reference的处理有ReferenceBasedDiscovery和RefeferentBasedDiscovery两种策略)

#### 构造方法

```
/* -- Constructors -- */

Reference(T referent) {
    this(referent, null);
}

Reference(T referent, ReferenceQueue<? super T> queue) {
    this.referent = referent;
    this.queue = (queue == null) ? ReferenceQueue.NULL : queue;
}
```

两个构造方法，一个没有引用队列 ReferenceQueue ， 一个有ReferenceQueue，取决于你是否需要通知机制。

通知机制：每个引用可以关联一个引用队列，该引用队列由应用程序创建的，然后垃圾回收器在检测到引用不可达时，将该引用加入到该队列，应用程序可以根据该引用队列来做些处理。（也就是该引用队列 成为 垃圾回收器与应用程序的通信机制）

ReferenceQueue是作为 JVM GC与上层Reference对象管理之间的一个消息传递方式，它使得我们可以对所监听的对象引用可达发生变化时做一些处理，WeakHashMap正是利用此来实现的。


这两种方法均有相应的使用场景,取决于实际的应用.如weakHashMap中就选择去查询queue的数据,来判定是否有对象将被回收.而ThreadLocalMap,则采用判断get()是否为null来作处理.

而如果不带的话,就只有不断地轮训reference对象,通过判断里面的get是否返回null(phantomReference对象不能这样作,其get始终返回null,因此它只有带queue的构造函数).


###### 场景

```
SoftReference sf = new SoftReference( new Object() ); 
```

其中sf 为引用，new Object为 sf指向的对象，，其实也就是建立了 sf 到 new Object对象的引用（关联）
然后垃圾回收器发现new Object的可达性发生变化（其实就是变为不可达后），
此时JVM虚拟机会根据引用对象 sf 的 queue是否为空，如果为空，则直接将引用的状态变为 InActivie(非激活，离真正回收不远了)

```
ReferenceQueue queue = new ReferenceQueue();
SoftReference sf2 = new SoftRerence( new Object(),  queue  );
```

如果垃圾回收器检测到 new Object的可达性发生变化后，会将该引用添加到 pending 引用链上，然后有专门的线程 ReferenceHandle线程来将引用加入到引用
链中（入队），也就是应用程序可以从queue中获取到所以垃圾回收器回收的对象的应用，也就是 queue是 垃圾回收器通知应用程序 被引用指向的对象已经被垃圾回收的消息。



#### ReferenceHandler


上面提到jvm会将要处理的对象设置到pending对象当中,因此肯定有一个线程来进行不断的enqueue操作,此线程即引用处理器线程,其优先级为MAX_PRIORITY,即最高.相应的启动过程为静态初始化创建,可以理解为当任何使用到Reference对象或类时,此线程即会被创建并启动.相应的代码如下所示:

```
private static class ReferenceHandler extends Thread {

    ReferenceHandler(ThreadGroup g, String name) {
        super(g, name);
    }

    public void run() {
        for (;;) {

            Reference r;
            synchronized (lock) {
                if (pending != null) {
                    r = pending;
                    Reference rn = r.next;
                    pending = (rn == r) ? null : rn;
                    r.next = r;
                } else {
                    try {
                        lock.wait();
                    } catch (InterruptedException x) { }
                    continue;
                }
            }

            // Fast path for cleaners
            if (r instanceof Cleaner) {
                ((Cleaner)r).clean();
                continue;
            }

            ReferenceQueue q = r.queue;
            if (q != ReferenceQueue.NULL) q.enqueue(r);
        }
    }
}

static {
    ThreadGroup tg = Thread.currentThread().getThreadGroup();
    for (ThreadGroup tgn = tg;
         tgn != null;
         tg = tgn, tgn = tg.getParent());
    Thread handler = new ReferenceHandler(tg, "Reference Handler");
    /* If there were a special system-only priority greater than
     * MAX_PRIORITY, it would be used here
     */
    handler.setPriority(Thread.MAX_PRIORITY);
    handler.setDaemon(true);
    handler.start();
}
```



handler的wait是jvm在gc的时候唤醒的，大概逻辑就是 gc的某个阶段检查到 oop的可达性变化后把jvm内维护引用的链表链接到到pending后 执行了notify

#### get()

```
public T get() {
    return this.referent;
}
```


#### clear()


```
public void clear() {
    this.referent = null;
}
```

清除引用对象所引用的原对象,这样通过get()方法就不能再访问到原对象了.从相应的设计思路来说,既然都进入到queue对象里面,就表示相应的对象需要被回收了,因为没有再访问原对象的必要.

这个方法只会被代码调用， 垃圾收集器会直接清楚引用的对象，不需要调用这个方法。

- WeakReference对象进入到queue之后,相应的referent为null.
- SoftReference对象,如果对象在内存足够时,不会进入到queue,自然相应的reference不会为null.如果需要被处理(内存不够或其它策略),则置相应的referent为null,然后进入到queue.
- FinalReference对象,因为需要调用其finalize对象,因此其reference即使入queue,其referent也不会为null,即不会clear掉.
- PhantomReference对象,因为本身get实现为返回null.因此clear的作用不是很大.因为不管enqueue还是没有,都不会清除掉.

#### isEnqueued()

查看引用是否入列了，当 引用对象在创建的时候没有注册队列，这个方法永远返回NULL
```
public boolean isEnqueued() {
        
    synchronized (this) {
        return (this.queue != ReferenceQueue.NULL) && (this.next != null);
    }
}

```

#### enqueue()

将引用入引用队列，这个方法只会被代码调用， 垃圾收集器会直接操作，不需要调用这个方法。

```
public boolean enqueue() {
    return this.queue.enqueue(this);
}
```



#### 流程

###### 场景1

```
public static void test() throws Exception{
    Object o = new Object();
    WeakReference<Object> wr = new WeakReference<Object>(o);
    System.out.println(wr.get() == null);
    o = null;
    System.gc();
    System.out.println(wr.get() == null);
}
```

结合代码eg1中的 o = null; 这一句，它使得o对象满足垃圾回收的条件，并且在后边显式的调用了 System.gc()，垃圾收集进行的时候会标记WeakReference所referent的对象o为不可达（使得wr.get()==null），并且通过 赋值给pending，触发ReferenceHandler线程处理pending。

ReferenceHandler线程要做的是将pending对象enqueue，但默认我们所提供的queue，也就是从构造函数传入的是null，实际是使用了ReferenceQueue.NULL，Handler线程判断queue为ReferenceQueue.NULL则不进行操作，只有非ReferenceQueue.NULL的queue才会将Reference进行enqueue。


###### 场景2

```
public class TestReference {
   	private static ReferenceQueue aQueue = new ReferenceQueue();
   	public static void main(String args) {
        Object a = new Object();   // 代码1
        WeakReference ref = new WeakReference( a, aQueue );  
   	}
}
```

然后在程序运行过程，内存不断消耗，直至触发垃圾回收操作时，垃圾收集器发现代码1处的 a 所指向的对象，只有 ref引用它，从根路径不可达，，故垃圾回收器，会将 ref 引用加入到  static Reference pending 链表中。【注意，此代码是写在JVM实现中的】

- 如果pending 为空，则将当前引用(ref) 设置为pengding,并且将 ref对象的next指针指向自己； 
- 如果pending不为空，则将当前的引用(ref)的next指向pengding,然后pengding = 当前的引用ref 】





#### 优化

另外,由于直接使用referenceQueue,再加上开启线程去监控queue太过麻烦和复杂.可以参考由google guava实现的 FinalizableReferenceQueue 以及相应的FinalizableReference对象.可以简化一点点处理过程.

## 


## 参考网址

[gc过程中reference对象的处理](http://www.importnew.com/21628.html)

[JVM源码分析之 FinalReference 完全解读](http://www.infoq.com/cn/articles/jvm-source-code-analysis-finalreference)

[java中针对Reference的实现和相应的执行过程](http://www.importnew.com/21633.html)

[话说ReferenceQueue](http://hongjiang.info/java-referencequeue/)

[java Reference 引用学习总结](http://blog.csdn.net/prestigeding/article/details/52692057)

[理解Java-Reference](http://yukai.space/2017/11/21/%E7%90%86%E8%A7%A3Java-Reference/)

[JAVA中reference类型简述](http://shift-alt-ctrl.iteye.com/blog/1839163)

[Java Reference Objects or How I Learned to Stop Worrying and Love OutOfMemoryError](http://www.kdgregory.com/index.php?page=java.refobj)



[queue1]:data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAxYAAAGoCAYAAADb4XOLAAAKrmlDQ1BJQ0MgUHJvZmlsZQAASImVlgdYU1kWx+976Y2WEOmE3qR3kF5Dlw42QgIhlBgDQcCGyuAIjgUVEbChQxEFxwLIKAKiWBgElGIdkEFAXQcLoqKyD1jCzu63u9+e9513f+/kvv877+ae9x0AyAMsgSAZlgIghZ8mDPZyZURGRTNwQwCFHERgCZRZ7FSBS1CQH0BsYfyrfewD0Ox433BW699//68mzYlLZQMABSEcy0llpyB8EfEmtkCYBgAKcaCxPk0wy0UI04RIggifmWXuPDfPcuw8P5ibExrshvAYAHgyiyXkAkD6gMQZ6WwuokOmIWzC5/D4CLsj7MhOYHEQzkF4aUrK2lk+h7Bu7D/pcP+iGSvWZLG4Yp5/lznDu/NSBcmszP9zOf63pSSLFp6hjjg5QegdjIx0ZM0qk9b6ipkfGxC4wDzO3Pw5ThB5hy0wO9UteoE5LHffBRYlhbksMEu4eC8vjRm6wMK1wWJ9fnKAn1g/jinmuFSPkAWO53kyFzgrITRigdN54QELnJoU4rs4x00cF4qCxTnHCz3F75iSupgbm7X4rLSEUO/FHCLF+XDi3D3EcX6YeL4gzVWsKUgOWsw/2UscT00PEd+bhmywBU5k+QQt6gSJ1we4Aw/ghxwMEAbMgAUwRRzJKi0uY3ZPA7e1gkwhj5uQxnBBqiaOweSzjZYyzExMrQGYrcH5v/j9wFxtQXT8YowjAYDZbSSouRhLRPbrFXOknDCLMV155BoNQAuKLRKmz8fQsycMUtmSgAbkgQrQALrAEMnPCtgDZyRjHxAIQkEUWA3YIAGkACFYDzaCrSAX5IO94CAoBsfASVAJzoLzoB5cAS3gJrgLukAveAwGwQh4BSbARzANQRAOokBUSB5ShbQgA8gMsoEcIQ/IDwqGoqAYiAvxIRG0EdoO5UMFUDF0AqqCfoEuQy3QbagbeggNQePQO+gLjILJMA1WhrVhY9gGdoF94VB4FcyF18FZcA68Gy6Cy+AzcB3cAt+Fe+FB+BU8iXy6SCg6Sg1liLJBuaECUdGoeJQQtRmVhypElaFqUI2odtR91CDqNeozGoumohloQ7Q92hsdhmaj16E3o3ehi9GV6Dp0G/o+egg9gf6OoWCUMAYYOwwTE4nhYtZjcjGFmHLMJcwNTC9mBPMRi8XSsTpYa6w3NgqbiN2A3YU9gq3FNmO7scPYSRwOJ48zwDngAnEsXBouF3cYdwZ3DdeDG8F9wpPwqngzvCc+Gs/Hb8MX4k/jm/A9+FH8NEGKoEWwIwQSOIRMwh7CKUIj4R5hhDBNlCbqEB2IocRE4lZiEbGGeIP4hPieRCKpk2xJy0k8UjapiHSOdIs0RPpMliHrk93IK8ki8m5yBbmZ/JD8nkKhaFOcKdGUNMpuShXlOuUZ5ZMEVcJIginBkdgiUSJRJ9Ej8UaSIKkl6SK5WjJLslDyguQ9yddSBCltKTcpltRmqRKpy1L9UpPSVGlT6UDpFOld0qelb0uPyeBktGU8ZDgyOTInZa7LDFNRVA2qG5VN3U49Rb1BHaFhaTo0Ji2Rlk87S+ukTcjKyFrIhstmyJbIXpUdpKPo2nQmPZm+h36e3kf/skR5icuSuCU7l9Qs6VkyJaco5ywXJ5cnVyvXK/dFniHvIZ8kv0++Xv6pAlpBX2G5wnqFowo3FF4r0hTtFdmKeYrnFR8pwUr6SsFKG5ROKnUoTSqrKHspC5QPK19Xfq1CV3FWSVQ5oNKkMq5KVXVU5akeUL2m+pIhy3BhJDOKGG2MCTUlNW81kdoJtU61aXUd9TD1beq16k81iBo2GvEaBzRaNSY0VTX9NTdqVms+0iJo2WglaB3Satea0tbRjtDeoV2vPaYjp8PUydKp1nmiS9F10l2nW6b7QA+rZ6OXpHdEr0sf1rfUT9Av0b9nABtYGfAMjhh0L8UstV3KX1q2tN+QbOhimG5YbThkRDfyM9pmVG/0xljTONp4n3G78XcTS5Nkk1Mmj01lTH1Mt5k2mr4z0zdjm5WYPTCnmHuabzFvMH9rYWARZ3HUYsCSaulvucOy1fKblbWV0KrGatxa0zrGutS634ZmE2Szy+aWLcbW1XaL7RXbz3ZWdml25+3+tDe0T7I/bT+2TGdZ3LJTy4Yd1B1YDiccBh0ZjjGOxx0HndScWE5lTs+dNZw5zuXOoy56LokuZ1zeuJq4Cl0vuU652bltcmt2R7l7uee5d3rIeIR5FHs881T35HpWe054WXpt8Gr2xnj7eu/z7mcqM9nMKuaEj7XPJp82X7JviG+x73M/fT+hX6M/7O/jv9//SYBWAD+gPhAEMgP3Bz4N0glaF/TrcuzyoOUly18EmwZvDG4PoYasCTkd8jHUNXRP6OMw3TBRWGu4ZPjK8KrwqQj3iIKIwUjjyE2Rd6MUonhRDdG46PDo8ujJFR4rDq4YWWm5Mndl3yqdVRmrbq9WWJ28+uoayTWsNRdiMDERMadjvrICWWWsyVhmbGnsBNuNfYj9iuPMOcAZj3OIK4gbjXeIL4gf4zpw93PHE5wSChNe89x4xby3id6JxxKnkgKTKpJmkiOSa1PwKTEpl/ky/CR+21qVtRlruwUGglzB4Dq7dQfXTQh9heWpUOqq1IY0GtLsdIh0RT+IhtId00vSP60PX38hQzqDn9GRqZ+5M3M0yzPr5w3oDewNrRvVNm7dOLTJZdOJzdDm2M2tWzS25GwZyfbKrtxK3Jq09bdtJtsKtn3YHrG9MUc5Jztn+AevH6pzJXKFuf077Hcc+xH9I+/Hzp3mOw/v/J7HybuTb5JfmP91F3vXnZ9Mfyr6aWZ3/O7OPVZ7ju7F7uXv7dvntK+yQLogq2B4v//+ugOMA3kHPhxcc/B2oUXhsUPEQ6JDg0V+RQ2HNQ/vPfy1OKG4t8S1pLZUqXRn6dQRzpGeo85Ha44pH8s/9uU47/jACa8TdWXaZYUnsSfTT744FX6q/Webn6vKFcrzy79V8CsGK4Mr26qsq6pOK53eUw1Xi6rHz6w803XW/WxDjWHNiVp6bf45cE507uUvMb/0nfc933rB5kLNRa2LpZeol/LqoLrMuon6hPrBhqiG7ss+l1sb7Rsv/Wr0a8UVtSslV2Wv7mkiNuU0zVzLujbZLGh+3cJtGW5d0/r4euT1B23L2zpv+N64ddPz5vV2l/ZrtxxuXbltd/vyHZs79Xet7tZ1WHZc+s3yt0udVp1196zvNXTZdjV2L+tu6nHqabnvfv/mA+aDu70Bvd19YX0D/Sv7Bwc4A2MPkx++fZT+aPpx9hPMk7ynUk8Lnyk9K/td7/faQavBq0PuQx3PQ54/HmYPv/oj9Y+vIzkvKC8KR1VHq8bMxq6Me453vVzxcuSV4NX069y/Sf+t9I3um4t/Ov/ZMRE5MfJW+Hbm3a738u8rPlh8aJ0Mmnz2MeXj9FTeJ/lPlZ9tPrd/ifgyOr3+K+5r0Te9b43ffb8/mUmZmRGwhKy5VgCFOBwfD8C7CgAoUQBQuwAgSsz3yHMGzff1cwT+E8/30XNmBUCFMwBhzQAEI16aDYAOci2JcBAyhjoD2Nxc7P+w1Hhzs3ktUj3SmhTOzLxHekOcHgDf+mdmputnZr6VI8k+AqD543xvPmtSSP9/vMw2wj2kJ8YvG/yL/R2gMwUHszLYKQAAAAlwSFlzAAAWJQAAFiUBSVIk8AAAQABJREFUeAHsvQmcbUdZ7v3seei9e567z8nEkEBCIEgYJJEol4B44cp1AEXwooCK3g9F9OKHMnwEgnqZxFy4cEEGQaYgfPDToIIIMoTRCGgIweSc0/M87e493+dd3XWy06d79+7uPfXeT52zuvZaq1atqn+tVaveet+q8m1ubhZRZefz+RAOh2F+I1yxWEQmk4H5jXDKv8pfz7/ef9V/qv8b8f3R90/ff7V/1P5rZPvX34iKT/cUAREQAREQAREQAREQARFoLQISLFqrPJUbERABERABERABERABEWgIAQkWDcGum4qACIiACIiACIiACIhAaxGQYNFa5anciIAIiIAIiIAIiIAIiEBDCEiwaAh23VQEREAEREAEREAEREAEWouABIvWKk/lRgREQAREQAREQAREQAQaQkCCRUOw66YiIAIiIAIiIAIiIAIi0FoEJFi0VnkqNyIgAiIgAiIgAiIgAiLQEAISLBqCXTcVAREQAREQAREQAREQgdYiIMGitcpTuREBERABERABERABERCBhhCQYNEQ7LqpCIiACIiACIiACIiACLQWAQkWrVWeyo0IiIAIiIAIiIAIiIAINISABIuGYNdNRUAEREAEREAEREAERKC1CEiwaK3yVG5EQAREQAREQAREQAREoCEEJFg0BLtuKgIiIAIiIAIiIAIiIAKtRUCCRWuVp3IjAiIgAiIgAiIgAiIgAg0hIMGiIdh1UxEQAREQAREQAREQARFoLQISLFqrPJUbERABERABERABERABEWgIAQkWDcGum4qACIiACIiACIiACIhAaxGQYNFa5anciIAIiIAIiIAIiIAIiEBDCAR9Pl/NblwsFmsWdyUR1zJvldxf+Vf5V/Kc1CqMnv/a1W2VlJnef73/lTwntQqj91/vf62erUriVf3XvvWfr1Ao1CT3mUymkmevZmHC4XDN4q4kYuVf5V/Jc1KrMHr+9f7X6tmqJF7Vf6r/KnlOahVG9Z/qv1o9W5XE2+71X000Fk5SdX4lBVHNMK6nxvnVjLuSuFy+nV/JNdUM4/Lt/GrGXUlcLt/Or+SaaoZx+XZ+NeOuJC6Xb+dXck01w7h8O7+acVcSl8u38yu5ppphXL6dX824K4nL5dv5lVxTzTAu386vZtyVxOXy7fxKrqlmGJdv51cz7kricvl2fiXXVDOMy7fzqxl3JXG5fDu/kmuqGcbl2/nVjLuSuFy+nV/JNdUM4/Lt/GrGXUlcLt/Or+SaaoZx+XZ+NeOuJC6Xb+dXck01w7h8O7+acVcSl+VbYywqIaUwIiACIiACIiACIiACIiACZQlIsCiLRydFQAREQAREQAREQAREQAQqISDBohJKCiMCIiACIiACIiACIiACIlCWgASLsnh0UgREQAREQAREQAREQAREoBICEiwqoaQwIiACIiACIiACIiACIiACZQlIsCiLRydFQAREQAREQAREQAREQAQqISDBohJKCiMCIiACIiACIiACIiACIlCWgASLsnh0UgREQAREQAREQAREQAREoBICEiwqoaQwIiACIiACIiACIiACIiACZQlIsCiLRydFQAREQAREQAREQAREQAQqISDBohJKCiMCIiACIiACIiACIiACIlCWgASLsnh0UgREQAREQAREQAREQAREoBICEiwqoaQwIiACIiACIiACIiACIiACZQlIsCiLRydFQAREQAREQAREQAREQAQqISDBohJKCiMCIiACIiACIiACIiACIlCWgASLsnh0UgREQAREQAREQAREQAREoBICEiwqoaQwIiACIiACIiACIiACIiACZQlIsCiLRydFQAREQAREQAREQAREQAQqISDBohJKCiMCIiACIiACIiACIiACIlCWgASLsnh0UgREQAREQAREQAREQAREoBICEiwqoaQwIiACIiACIiACIiACIiACZQkEy55t8MlisYi1tTXk83lspFIoFArwVZAmn8+HUCgE8xvhLN3ZbBbmN8KV5t/SEAgEMDIy4vmNSI/uKQLHIWDPcDqd9uqBpaWl7XqgzLtd+vwf575HvbaZ3n+XB1cP9PX1efVAOBx2p+SLQNsTsLaFtTNmZmY8/zhth2Z8/2tdwJZnv9+Pzs5Oz7f2l1z7EmhqwWJ9fR233norJicn8elPfxq2H6xQYDhOxVCNx8FetEY6y7+lIbWxgdHRUXzoQx/C2NhYI5Oke4vAkQiYUPHtb3/bqwfe9KY3wYSLcCRStuNA7/99nSpWD2xtbmJgYACvfe1r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
