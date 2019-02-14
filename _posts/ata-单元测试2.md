 
#### PowerMock特性


- PowerMockito 支持大部分Mockito 不支持的场景,比如：静态、私有、构造方法
- PowerMockito 使用的是操纵字节的方式，所以他使用的是自己的 JUnit runner. 需要使用@PrepareForTest注释
- PowerMock 大部分的写法和 Mockito 类似，因为 PowerMock 是扩展 Mockito 的 API 形成的

######  依赖


```
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <version>2.8.9</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-module-junit4</artifactId>
    <version>1.7.3</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-module-junit4-rule</artifactId>
    <version>1.7.3</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-api-mockito2</artifactId>
    <version>1.7.3</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-classloading-xstream</artifactId>
    <version>1.7.3</version>
    <scope>test</scope>
</dependency>
```

###### doNothing & suppress

如果一个私有方法包含太多的外部依赖，不想引入测试，可以让私有方法不执行

```
PowerMockito.doNothing().when(IcbcNraBizServiceImpl.class,"createNraUsdTransfer_internal",Long.class,BigDecimal.class);
PowerMockito.suppress(PowerMockito.method(IcbcNraBizServiceImpl.class,"createNraUsdTransfer_internal"));
```

 


###### 静态的方法。

```
@RunWith(PowerMockRunner.class)
@PrepareForTest({StaticService.class})
public class ItemServiceTest {
 
    @InjectMocks
    private ItemService itemService;
 
    @Before
    public void setUp() throws Exception {
        MockitoAnnotations.initMocks(this);
    }
 
    @Test
    public void readItemDescriptionWithoutIOException() throws IOException {

        //静态类
        mockStatic(StaticService.class);
        when(StaticService.readFile(fileName)).thenReturn("Dummy");
 
        // 运行方法
        itemService.readItemDescription(fileName);

        //验证
        verifyStatic(times(1));

    }
}
```


###### 私有方法

```
class Demo{
    
    /*转账*/
    public void transfetAmount(){
        this.initBankInfo()
    }

    /*获取银行渠道信息*/
    private void initBankInfo(){
        ...
    }
}
```

这个场景中， getBankInfo 是一个私有方法，已经在线上经过长时间的验证，默认是没有问题的，对 transfetAmount 方法的单元测试，不需要再引入 `getBankInfo`的测试，简化测试的复杂度，可以对 私有方法 进行Mock

```
@RunWith(PowerMockRunner.class)
@PrepareForTest({ Demo.class })
public class DemoTest {

    @Autowried
    private Demo demo;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        // 写法1
        PowerMockito.suppress(PowerMockito.method(Demo.class,"getBankInfo"));
        //
        PowerMockito.doNothing().when(IcbcNraBizServiceImpl.class,"createNraUsdTransfer_internal");
    }

    @Test
    public void test_01() {
        try {
            demo.transfetAmount();
        }catch (Exception e){
            Assert.fail();
        }
    }
}
```

#### 注意事项

- 需要添加注释： `@RunWith(PowerMockRunner.class)`,`@PrepareForTest({ Demo.class })`
- 被Mock的类不要使用接口类，你测试的是类的实现逻辑是否正确，不是接口是否优雅；而且会提示你找不到方法抛出异常。


## 常见异常

**1:java.lang.NoSuchMethodError**
org.mockito.internal.handler.MockHandlerFactory.createMockHandler(Lorg/mockito/mock/MockCreationSettings;)Lorg/mockito/internal/InternalMockHandler;

```
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-module-junit4</artifactId>
    <version>2.0.0-beta.5</version>
    <scope>test</scope>
</dependency>

<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-api-mockito2</artifactId>
    <version>2.0.0-beta.5</version>
    <scope>test</scope>
</dependency>
```



**2:Extension API internal error**org.powermock.api.extension.reporter.MockingFrameworkReporterFactoryImpl
```
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-api-mockito-common</artifactId>     
    <version>1.6.5</version>
</dependency>
```


**3:javassist 包冲突问题**

把不需要的版本排除掉即可，推荐版本
```
<dependency>
  <groupId>org.javassist</groupId>
  <artifactId>javassist</artifactId>
  <version>3.21.0-GA</version>
</dependency>
```
 