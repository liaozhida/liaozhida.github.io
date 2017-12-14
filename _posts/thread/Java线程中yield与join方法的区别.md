Java线程中yield与join方法的区别.md


[Java线程中yield与join方法的区别](http://www.importnew.com/14958.html)

LockSupport.park不同于Thread.yield()，yield只是告诉操作系统可以先让其他线程运行，但自己依然是可运行状态，而park会放弃调度资格，使线程进入WAITING状态。