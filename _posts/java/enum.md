

###### 枚举的常规用法， 用来代替常量
```
public enum Day {
    SUNDAY, MONDAY, TUESDAY, WEDNESDAY,
    THURSDAY, FRIDAY, SATURDAY 
}
```




###### 可以添加复杂的逻辑

```
public enum Planet {
    MERCURY (3.303e+23, 2.4397e6),
    VENUS   (4.869e+24, 6.0518e6),

    URANUS  (8.686e+25, 2.5559e7),
    NEPTUNE (1.024e+26, 2.4746e7);

    private final double mass;   
    private final double radius;  
    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }
    private double mass() { return mass; }
    private double radius() { return radius; }

 

    double surfaceGravity() {
        return mass / (radius * radius);
    }
}
```


###### values方法会返回所有枚举类型

```
for (Planet p : Planet.values()) {
    System.out.printf("Your weight on %s is %f%n",
                      p, p.surfaceWeight(mass));
}
```




######  使用枚举创建单例模式

常规的 `Double checked locking` 单例模式

```
class DBPool{

	private volatile static Connection volatile = null;

	public Connection getCon(){
		if(con == null){
			synchronized(DBPool.class){
				if(con == null){
					con = new Connection();
				}
			}
			return con;
		}
	}

}
```


默认枚举实例的创建是线程安全的，但是在枚举中的其他任何方法由程序员自己负责。使用 enum 创建单例：

```
// 定义单例模式中需要完成的代码逻辑
public interface MySingleton {
    void doSomething();
}

public enum Singleton implements MySingleton {
    INSTANCE {
        @Override
        public void doSomething() {
            System.out.println("complete singleton");
        }
    };

    public static MySingleton getInstance() {
        return Singleton.INSTANCE;
    }
}
```



[Enum Types](https://docs.oracle.com/javase/tutorial/java/javaOO/enum.html)