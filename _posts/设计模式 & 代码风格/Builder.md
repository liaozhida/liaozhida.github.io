Builder.md

## 解决问题

构造器有多个参数，有些必填，有些选填

#### 重叠构造器方式

```
class A{

	private int a,b,c;

	public A(int a,int b){
		this.A(a,b,0);
	}

	public A(int a,int b,int c){
		...
	}
} 
```

#### JavaBean 模式

缺点：

构造过程被分成几个调用，类无法仅仅通过构造器检验保证一致性

```
class A{

	private int a,b,c;

	public A( ){
	}

	public void setA(int a){
		this.a = a;
	}

	... 
} 
```


#### Builder 模式

缺点：
- 开销
- 冗长


```
class Test{

	private int a,b,c;
	
	static class Builer{

		private int a,b,c;
	
		public Builer(int a){
			this.a = a;
		}

		public void b(int b){
			this.b = b
		}

		public void c(int c){
			this.c = c;
		}

		public Test builder(){
			return new Test(this);
		}
	}

	private Test(Builer builder){
		this.a = builer.a;
		this.b = builer.b;
		this.c = builer.c;
	}
}

```

```
Test a = new Test.Builder(a).b(b).c(c).builer();
```

特征
- 私有构造器，在构造器中用Builder对每个字段赋值
- 静态内部类 Builder， 声明同等数量的字段。
- Builder 存在 Build方法，用户实例化外部对象


优点：
- 使用简洁
- 避免高并发情况下，对象实例化之后使用 set方式，造成数据不一致性

