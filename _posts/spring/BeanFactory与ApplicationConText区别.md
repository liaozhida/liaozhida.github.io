BeanFactory与ApplicationConText区别.md

1. 两者都是通过xml配置文件加载bean,ApplicationContext和BeanFacotry相比,提供了更多的扩展功能，但其主要区别在于后者是延迟加载,如果Bean的某一个属性没有注入，BeanFacotry加载后，直至第一次使用调用getBean方法才会抛出异常；而ApplicationContext则在初始化自身是检验，这样有利于检查所依赖属性是否注入；所以通常情况下我们选择使用ApplicationContext.


2. Bean 工厂（com.springframework.beans.factory.BeanFactory）是Spring 框架最核心的接口，它提供了高级IoC 的配置机制。
应用上下文（com.springframework.context.ApplicationContext）建立在BeanFactory 基础之上。
几乎所有的应用场合我们都直接使用ApplicationContext 而非底层的BeanFactory。

ApplicationContext 由BeanFactory 派生而来，提供了更多面向实际应用的功能。在BeanFactory 中，很多功能需要以编程的方式实现，而在ApplicationContext 中则可以通过配置的方式实现。
    ApplicationContext 的主要实现类是ClassPathXmlApplicationContext 和FileSystemXmlApplicationContext，前者默认从类路径加载配置文件，后者默认从文件系统中装载配置文件。

核心接口包括：
    
- ApplicationEventPublisher：让容器拥有发布应用上下文事件的功能，包括容器启动事件、关闭事件等。实现了 ApplicationListener 事件监听接口的Bean 可以接收到容器事件， 并对事件进行响应处理。在ApplicationContext 抽象实现类AbstractApplicationContext中，我们可以发现存在一个ApplicationEventMulticaster，它负责保存所有监听器，以便在容器产生上下文事件时通知这些事件监听 者。
    
- MessageSource：为应用提供i18n 国际化消息访问的功能；
    
- ResourcePatternResolver ： 所有ApplicationContext 实现类都实现了类似于PathMatchingResourcePatternResolver 的功能，可以通过带前缀的Ant 风格的资源文件路径装载Spring 的配置文件。
   
- sLifeCycle：该接口是Spring 2.0 加入的，该接口提供了start()和stop()两个方法，主要用于控制异步处理过程。在具体使用时，该接口同时被 
ApplicationContext 实现及具体Bean 实现，ApplicationContext 会将start/stop 的信息传递给容器中所有实现了该接口的Bean，以达到管理和控制JMX、任务调度等目的。



BeanFactoryPostProcessor   
	//Spring IoC容器允许BeanFactoryPostProcessor在容器实际实例化任何其它的bean之前读取配置元数据，并有可能修改它。  
	//同时BeanFactoryPostProcessor的回调比BeanPostProcessor要早  
	void postProcessBeanFactory(ConfigurableListableBeanFactory arg) 



ConfigurableListableBeanFactory ：除了ListableBeanFactory和AutowireCapableBeanFactory功能之外还提供了访问和修改BeanDefinition，预实例化singleton列表。 


BeanDefinitionRegistry ：spring配置文件中的每一个bean节点元素在spring容器里都通过一个BeanDefinition对象表示，描述了Bean的配置信息。而BeanDefinitionRegistry接口提供了向容器手工注册BeanDefinition对象的方法； 


## 参考网站

[Spring之BeanFactory与ApplicationConText区别](https://blog.csdn.net/u013400939/article/details/51460503)
[BeanFactory 和ApplicationContext（Bean工厂和应用上下文）](http://elf8848.iteye.com/blog/324796)
[Spring中Bean初始化实例【重要】](http://uule.iteye.com/blog/2094609)
[Spring的BeanFactory体系结构一](http://programming.iteye.com/blog/850753)