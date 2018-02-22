Integet

int四字节，32位， 最大值应该是 `2^31 - 1` ,为什么指数不是32，因为需要预留一位符号位
最小值 `-2^31`
```
public final class Integer extends Number implements Comparable<Integer> {
    
    public static final int   MIN_VALUE = 0x80000000;

   
    public static final int   MAX_VALUE = 0x7fffffff;

```
