---
layout:     post
title:      "for循环中retry的用法"
subtitle:	""
date:       2016-10-23 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-.jpg"
tags:
    - 
---

在 FutureTask 的源码中发现了一段代码 `continue retry`,以前没有看到过这个语法，于是去网上找了一些简单的介绍。


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


```
retry:
for (;;) {
    int c = ctl.get();
    int rs = runStateOf(c);

    /* 状态异常 直接返回失败 */
    if (rs >= SHUTDOWN && ! (rs == SHUTDOWN && firstTask == null && ! workQueue.isEmpty()))
        return false;

    for (;;) {
        int wc = workerCountOf(c);
        /* 当前 worker 数量大于最大数量 或者 大于初始数量，直接返回失败 */
        if ( wc >= CAPACITY || wc >= (core ? corePoolSize : maximumPoolSize) )
            return false;
            
        if (compareAndIncrementWorkerCount(c))
            break retry;
```
