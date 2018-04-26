---
layout:     post
title:      "面试清单(10)"
subtitle: ""
date:       2010-10-23 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-road.jpg"
tags:
    - zчастный
---
面试清单(10) 其他语言的了解程度（Js Nodejs python）.md



## javascript

promise  [Promise对象](http://javascript.ruanyifeng.com/advanced/promise.html)

[Web Storage：浏览器端数据储存机制](http://javascript.ruanyifeng.com/bom/webstorage.html)

[线程](http://javascript.ruanyifeng.com/advanced/single-thread.html)


如果一层层地上溯，所有对象的原型最终都可以上溯到Object.prototype，即Object构造函数的prototype属性。那么，Object.prototype对象有没有它的原型呢？回答是有的，就是没有任何属性和方法的`null对象`，而null对象没有自己的原型。

**“原型链”的作用是**：读取对象的某个属性时，JavaScript 引擎先寻找对象本身的属性，如果找不到，就到它的原型去找，如果还是找不到，就到原型的原型去找。如果直到最顶层的Object.prototype还是找不到，则返回undefined。

`instanceof`的原理是检查原型链，

[prototype 对象](http://javascript.ruanyifeng.com/oop/prototype.html)


[同源](http://javascript.ruanyifeng.com/bom/same-origin.html)

[cors](http://javascript.ruanyifeng.com/bom/cors.html)

闭包

- 函数内部声明变量的时候，一定要使用var命令。如果不用的话，你实际上声明了一个全局变量！
- 函数内部可以直接读取全局变量。函数外部自然无法读取函数内的局部变量

如何从外部读取局部变量？ 

我们有时候需要得到函数内的局部变量。只有通过变通方法才能实现。那就是在函数的内部，再定义一个函数。

```
function f1(){
　　　　var n=999;
　　　　function f2(){
　　　　　　alert(n); // 999
　　　　}
　　}
```

既然f2可以读取f1中的局部变量，那么只要把f2作为返回值，就可以在f1外部读取它的内部变量了 ; f2函数，就是`闭包`:闭包就是能够读取其他函数内部变量的函数。

闭包的用途: 闭包可以用在许多地方。它的最大用处有两个
- 一个是前面提到的可以读取函数内部的变量
- 另一个就是让这些变量的值始终保持在内存中。

使用闭包的注意点:

1）由于闭包会使得函数中的变量都被保存在内存中，内存消耗很大，所以不能滥用闭包，否则会造成网页的性能问题，在IE中可能导致内存泄露。解决方法是，在退出函数之前，将不使用的局部变量全部删除。

2）闭包会在父函数外部，改变父函数内部变量的值。所以，如果你把父函数当作对象（object）使用，把闭包当作它的公用方法（Public Method），把内部变量当作它的私有属性（private value），这时一定要小心，不要随便改变父函数内部变量的值。


模块化

提升

变量声明提升（Hoisting）

JavaScript 会提升变量声明。这意味着 var 表达式和 function 声明都将会被提升到当前作用域的顶部。

```
var myvar = 'my value';  

(function() {  
    alert(myvar); // undefined  
    var myvar = 'local value';  
})();
```


```
var myvar;

(function() {  

	var myvar ;
    alert(myvar); // undefined  
    myvar = 'local value';  
})();

myvar = 'my value';  


```


this

JavaScript 有一套完全不同于其它语言的对 this 的处理机制。 在五种不同的情况下 ，this 指向的各不相同。
因为 this 只可能出现在上述的五种情况中


1、函数调用 `foo();` 这里 this 也会指向全局对象。

2、方法调用 `test.foo();`  这个例子中，this 指向 test 对象。

3、调用构造函数 `new foo(); ` 如果函数倾向于和 new 关键词一块使用，则我们称这个函数是 构造函数。 在函数内部，this 指向新创建的对象。 

```
var name = "The Window";　　
var object = {　　　　
	name: "My Object",
	　　　　
	getNameFunc: function() {　　　　　　
		var that = this;　　　　　　
		return function() {　　　　　　　　
			return that.name;　　　　　　
		};　　　　
	}　　
};　
console.log(object.getNameFunc()());



　　
var name = "The Window";　　
var object = {　　　　
	name: "My Object",

	getNameFunc: function() {　　　　　　
		return function() {　　　　　　　　
			return this.name;　　　　　　
		};　　　　
	}　　
};
console.log(object.getNameFunc()());
```

答案：
```
My Object 

undefined
```



为了在 test 中获取对 Foo 对象的引用，我们需要在 method 函数内部创建一个局部变量指向 Foo 对象。

```
Foo.method = function() {
    var that = this;
    function test() {
        // 使用 that 来指向 Foo 对象
    }
    test();
}
```



尽管 JavaScript 支持一对花括号创建的代码段，但是并不支持块级作用域； 而仅仅支持 函数作用域。



###### 单线程语言

有一个守护线程 

主线程在执行 网络请求的时候，注册一个回调函数， 线程会调用系统的网络请求，然后开始去处理接下来的主程序 ，当系统网络请求完成之后，会通知主线程，主线程在合适的时候调用回调函数


## Node

异步

express

socket IO 

命令行工具

中间件
