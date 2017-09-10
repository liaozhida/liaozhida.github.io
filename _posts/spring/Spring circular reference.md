# Spring circular reference



BeanCurrentlyInCreationException: Error creating bean with name 'productRedisService': 
Bean with name 'productRedisService' has been injected into other beans [productService,userService] in its raw version as part of a circular reference
but has eventually been wrapped. This means that said other beans do not use the final version of the bean. 
This is often the result of over-eager type matching - consider using 'getBeanNamesOfType' with the 'allowEagerInit' flag turned off, for example.

[Spring circular reference example](https://stackoverflow.com/questions/11348794/spring-circular-reference-example)
[http://blog.5ibc.net/p/26994.html](http://blog.5ibc.net/p/26994.html)
[spring autowired aop circular dependency](https://stackoverflow.com/questions/28985144/spring-autowired-aop-circular-dependency)