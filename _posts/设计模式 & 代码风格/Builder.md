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


