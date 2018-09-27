https://martinfowler.com/articles/mocksArentStubs.html


https://blog.codecentric.de/en/2016/03/junit-testing-using-mockito-powermock/


https://www.ibm.com/developerworks/cn/java/j-lo-jacoco/index.html




In unit testing we want to test methods of one class in isolation. But classes are not isolated. They are using services and methods from other classes. Those are often referred to as collaborators. This leads to two major problems:

- 外部的服务会导致在 单测环境下没有办法工作， 比如数据库和外部的系统
- 测试应该关注的是类的代码实现， 如果外部的类会直接的影响到这些被测试的类，那不是我们想要的结果

Mockito 和 PowerMock 都用于集成测试中，使用mock对象替代耦合的类，两者的不同在于 Mockito 适用于所有标准的场景， PowerMock 用于特殊的情况：比如Mock私有 & 静态的方法。

Mocking with Mockito

In the method under test an item is fetched by its id and then some logic is applied. We only want to test that logic.

```
public class ItemServiceTest {
 
    @Mock
    private ItemRepository itemRepository;
 
    @InjectMocks
    private ItemService itemService;
 
    @Before
    public void setUp() throws Exception {
        MockitoAnnotations.initMocks(this);
    }
 
    @Test
    public void getItemNameUpperCase() {
 
        Item mockedItem = new Item("it1", "Item 1", "This is item 1", 2000, true);
        when(itemRepository.findById("it1")).thenReturn(mockedItem);
 
        String result = itemService.getItemNameUpperCase("it1");

        verify(itemRepository, times(1)).findById("it1");
        assertThat(result, is("ITEM 1"));
    }
}
```

PS: verify 的用法是验证这个方式是否被调用过

