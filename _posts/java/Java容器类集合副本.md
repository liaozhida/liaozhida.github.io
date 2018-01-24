---
layout:     post
title:      "Java容器类集合"
subtitle:    "主要源码分析，容器类关系图"
date:       2016-10-22 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-road.jpg"
tags:
    - Java
---

> This document is not completed and will be updated anytime.


![](/img/in-post/collectionsH.png)
[点击查看大图](http://www.falkhausen.de/Java-8/java.util/Collection-Hierarchy.html)

![](/img/in-post/mapH.png)
[点击查看大图](http://www.falkhausen.de/Java-8/java.util/Map-Hierarchy.html)

# 普通容器类

[Collections关系图1](http://www.falkhausen.de/Java-8/java.util/Collection-Hierarchy-simple.html)

## List

All Known Implementing Classes: `AbstractList, AbstractSequentialList, ArrayList, AttributeList, CopyOnWriteArrayList, LinkedList, RoleList, RoleUnresolvedList, Stack, Vector`

以下为 List 的子类，**当然也实现了其他的接口,比如 LinkedList实现了 Queue接口**

#### ArrayList

父接口：`Serializable, Cloneable, Iterable<E>, Collection<E>, List<E>, RandomAccess`

```
public class ArrayList<E> extends AbstractList<E>
    implements List<E>, RandomAccess, Cloneable, java.io.Serializable{

    private static final int DEFAULT_CAPACITY = 10;

    private static final Object[] EMPTY_ELEMENTDATA = {};

    private transient Object[] elementData;

    // 初始化逻辑
    public ArrayList(int initialCapacity) {
        super();
        if (initialCapacity < 0)
            throw new IllegalArgumentException("Illegal Capacity: "+
                                               initialCapacity);
        this.elementData = new Object[initialCapacity];
    }

    public ArrayList() {
        super();
        this.elementData = EMPTY_ELEMENTDATA;
    }
  
    // 添加元素逻辑
    public boolean add(E e) {
        ensureCapacityInternal(size + 1);  // Increments modCount!!
        elementData[size++] = e;
        return true;
    }

    public void add(int index, E element) {
        rangeCheckForAdd(index);

        ensureCapacityInternal(size + 1);  // Increments modCount!!
        System.arraycopy(elementData, index, elementData, index + 1,
                         size - index);
        elementData[index] = element;
        size++;
    }

    
    // 扩容逻辑
    private void ensureCapacityInternal(int minCapacity) {
        if (elementData == EMPTY_ELEMENTDATA) {
            minCapacity = Math.max(DEFAULT_CAPACITY, minCapacity);
        }

        ensureExplicitCapacity(minCapacity);
    }

    private void ensureExplicitCapacity(int minCapacity) {
        modCount++;

        // overflow-conscious code
        if (minCapacity - elementData.length > 0)
            grow(minCapacity);
    }

    private static final int MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;
    
    private void grow(int minCapacity) {
        // overflow-conscious code
        int oldCapacity = elementData.length;
        int newCapacity = oldCapacity + (oldCapacity >> 1);
        if (newCapacity - minCapacity < 0)
            newCapacity = minCapacity;
        if (newCapacity - MAX_ARRAY_SIZE > 0)
            newCapacity = hugeCapacity(minCapacity);
        // minCapacity is usually close to size, so this is a win:
        elementData = Arrays.copyOf(elementData, newCapacity);
    }

}
```
    

- 每次插入前都会进行容量检查，检查是否超出了容量，如果超出了，则进行扩容

- 默认大小是10，容量拓展，是创建一个新的数组，然后将旧数组上的数组copy到新数组，这是一个很大的消耗，所以在我们使用ArrayList时，最好能预计数据的大小，在第一次创建时就申请够内存。

- `clear`方法并不是把整个数组都删除，因为毕竟已经申请了内存，这样删了，很可惜，因为可能以后还用得着，这就免去了再次去申请内存的麻烦。这里只是把每个元素的都置为null，并把size设为0.

- 容量进行扩展的时候，其实例如整除运算将容量扩展为原来的1.5倍加1，而jdk1.7是利用位运算`oldCapacity >> 1`，从效率上，jdk1.7就要快于jdk1.6。

- 在算出newCapacity时，其没有和ArrayList所定义的`MAX_ARRAY_SIZE`作比较，为什么没有进行比较呢，原因是jdk1.6没有定义这个MAX_ARRAY_SIZE最大容量，也就是说，其没有最大容量限制的，但是jdk1.7做了一个改进，进行了容量限制。


[ArrayList实现原理以及其在jdk1.6和jdk1.7的实现区别](http://zhh9106.iteye.com/blog/2152419)

#### LinkedList

父接口：`Serializable, Cloneable, Iterable<E>, Collection<E>, Deque<E>, List<E>, Queue<E>`

```
public class LinkedList<E>
    extends AbstractSequentialList<E>
    implements List<E>, Deque<E>, Cloneable, java.io.Serializable
{
    transient int size = 0;

    transient Node<E> first;

    transient Node<E> last;

     public LinkedList() {
    }

    public LinkedList(Collection<? extends E> c) {
        this();
        addAll(c);
    }

    private void linkFirst(E e) {
        final Node<E> f = first;
        final Node<E> newNode = new Node<>(null, e, f);
        first = newNode;
        if (f == null)
            last = newNode;
        else
            f.prev = newNode;
        size++;
        modCount++;
    }

    void linkLast(E e) {
        final Node<E> l = last;
        final Node<E> newNode = new Node<>(l, e, null);
        last = newNode;
        if (l == null)
            first = newNode;
        else
            l.next = newNode;
        size++;
        modCount++;
    }

    public boolean add(E e) {
        linkLast(e);
        return true;
    }

    public E getFirst() {
        final Node<E> f = first;
        if (f == null)
            throw new NoSuchElementException();
        return f.item;
    }


    private class ListItr implements ListIterator<E> {
        private Node<E> lastReturned = null;
        private Node<E> next;
        private int nextIndex;
        private int expectedModCount = modCount;

        ListItr(int index) {
            // assert isPositionIndex(index);
            next = (index == size) ? null : node(index);
            nextIndex = index;
        }

        public boolean hasNext() {
            return nextIndex < size;
        }

        public E next() {
            checkForComodification();
            if (!hasNext())
                throw new NoSuchElementException();

            lastReturned = next;
            next = next.next;
            nextIndex++;
            return lastReturned.item;
        }

        ...
    }   

    // 获取指定元素 折中查找元素
    public E get(int index) {
        checkElementIndex(index);
        return node(index).item;
    }

    Node<E> node(int index) {
        if (index < (size >> 1)) {
            Node<E> x = first;
            for (int i = 0; i < index; i++)
                x = x.next;
            return x;
        } else {
            Node<E> x = last;
            for (int i = size - 1; i > index; i--)
                x = x.prev;
            return x;
        }
    }

    private void checkElementIndex(int index) {
        if (!isElementIndex(index))
            throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
    }

    private boolean isElementIndex(int index) {
        return index >= 0 && index < size;
    }
}
```



#### ArrayList vs LinkedList

ArrayList底层数据结构为数组， LinkedList 是双向列表。

LinkedList迭代器的next函数只是通过next指针快速得到下一个元素并返回。而get方法会从折中开始遍历直到index下标，查找一个元素时间复杂度为哦O(n/2)，get()遍历的时间复杂度就达到了O(n2),next()方式遍历时间复杂度是O(n)


###### ArrayList 和 LinkedList遍历方式结果对比分析

从上面的数量级来看，同样是foreach循环遍历，ArrayList和LinkedList时间差不多，可将本例稍作修改加大list size会发现两者基本在一个数量级上。

但ArrayList get函数直接定位获取的方式时间复杂度为O(1)，而LinkedList的get函数时间复杂度为O(n)。
再结合考虑空间消耗的话，建议首选ArrayList。对于个别插入删除非常多的可以使用LinkedList。

###### 结论总结

通过上面的分析我们基本可以总结下：

(1) 无论ArrayList还是LinkedList，遍历建议使用foreach，尤其是数据量较大时LinkedList避免使用get遍历。

(2) List使用首选ArrayList。对于个别插入删除非常多的可以使用LinkedList。

(3) 可能在遍历List循环内部需要使用到下标，这时综合考虑下是使用foreach和自增count还是get方式。

- [ArrayList和LinkedList的几种循环遍历方式及性能对比分析](http://www.trinea.cn/android/arraylist-linkedlist-loop-performance/)




# 同步容器类


每个操作都上锁，效率比较慢,相对于同步容器类，并发容器更高的效率和多样化的设计显得更加的主流。

迭代操作中，修改元素，可能会抛出ConcurrentModificationException ，
删除元素元素可能抛出ArrayIndexOutBoundsException  

#### Vector

Vector和ArrayList的实现方式可以看出非常的相像，每个方法中都添加了synchronized的关键字来保证同步



#### collections.synchronizedlist




# 并发容器类




## List

####  CopyOnWriteArrayList

[CopyOnWriteArrayList实现原理及源码分析](http://www.cnblogs.com/chengxiao/p/6881974.html)

区别于`读写锁`，写锁是通过 ReentrantLock 实现的 ， 读是没有任何锁  ，不保证数据的强一致性

###### 理论

CopyOnWriteArrayList是Java并发包中提供的一个并发容器，它是个线程安全且读操作无锁的ArrayList，写操作则通过创建底层数组的新副本来实现，是一种读写分离的并发策略，我们也可以称这种容器为"写时复制器"，
Java并发包中类似的容器还有CopyOnWriteSet。

集合框架中的ArrayList是非线程安全的，Vector虽是线程安全的，但由于简单粗暴的锁同步机制，性能较差。而CopyOnWriteArrayList则提供了另一种不同的并发处理策略 

很多时候，我们的系统应对的都是读多写少的并发场景。CopyOnWriteArrayList容器允许并发读，读操作是无锁的，性能较高。至于写操作，比如向容器中添加一个元素，则首先将当前容器复制一份，然后在新副本上执行写操作，结束之后再将原容器的引用指向新容器。

###### 优点：
读操作性能很高，因为无需任何同步措施，比较适用于读多写少的并发场景。Java的list在遍历时，若中途有别的线程对list容器进行修改，则会抛出ConcurrentModificationException异常。而CopyOnWriteArrayList由于其"读写分离"的思想，遍历和修改操作分别作用在不同的list容器，所以在使用迭代器进行遍历时候，也就不会抛出ConcurrentModificationException异常了

###### 缺点： 
内存可见性不能得到保证  、  内存的使用比较高





## 参考网址

[Java Collections](https://beginnersbook.com/2017/08/java-collections-deque-interface/)

[http://www.falkhausen.de/Java-8/](http://www.falkhausen.de/Java-8)


