《HeadFirst设计模式》学习笔记.md

**设计原则：把会变化的部分取出并封装起来，以便以后可以轻易的改动和扩充此部分，而不影响不需要变化的其他部分**

几乎是所有设计模式的精髓所在，每种设计模式都提供了一种方法，让系统的某部分改变不影响其他部分


## 抽象

- 在面向对象的概念中，所有的对象都是通过类来描绘的，但是反过来，并不是所有的类都是用来描绘对象的，如果一个类中没有包含足够的信息来描绘一个具体的对象，这样的类就是抽象类。

- 抽象类除了不能实例化对象之外，类的其它功能依然存在，成员变量、成员方法和构造方法的访问方式和普通类一样。

- 由于抽象类不能实例化对象，所以抽象类必须被继承，才能被使用。

#### 演示

通过抽象类:
- 可以将公共的行为定义好，以便于**代码复用**
- 可以定义抽象方法，确保所有子类都要保持相同的特征。

```
public abstract class Duck {

    private String weight;

    protected  void sound(){
        System.out.println("guagua");
    }

    abstract void color();
}
```

```
public class AfricaDuck extends Duck{

    @Override
    void color() {
        System.out.println("yellow");
    }
}

```

```
public class AsiaDuck extends Duck{
    @Override
    void color() {
        System.out.println("green");
    }
}
```

```
public class Farm {

    public static void main(String[] args) {
        Duck asiaDuck = new AsiaDuck();
        Duck africaDuck = new AfricaDuck();

        asiaDuck.color();
        asiaDuck.sound();

        africaDuck.color();
        africaDuck.sound();
    }
}
```

如果要增加新的特性，比如 fly() 方法; 会影响所有的子类 ，难以改动；
- 不是所有的子类都有 fly() 特征，比如水鸭就不会飞
- 不是所有的子类 fly() 都有相同的行为，比如有些品种的鸭子飞的很低

```
public abstract class Duck {

    private String weight;

    protected  void sound(){
        System.out.println("guagua");
    }

    protected  void fly(){
        System.out.println(" i flying so high");
    }

    abstract void color();
}
```

所以接下来引入了了接口的概念。

## 接口

是一个抽象类型，是抽象方法的集合，接口通常以interface来声明。一个类通过继承接口的方式，从而来继承接口的抽象方法。通俗讲，定义了一系列的特征

接口特性：
- 接口中每一个方法也是隐式抽象的,接口中的方法会被隐式的指定为 public abstract（只能是 public abstract，其他修饰符都会报错）。
- 接口中可以含有变量，但是接口中的变量会被隐式的指定为 public static final 变量（并且只能是 public，用 private 修饰会报编译错误）。
- 接口中的方法是不能在接口中实现的，只能由实现接口的类来实现接口中的方法。
- 除非实现接口的类是抽象类，否则该类要定义接口中的所有方法。

```
public interface flyable{
    void fly();
}
```

对需要具有 fly 能力的类，实现 flyable 接口，然后在子类中编写具体的代码

缺点： 接口无法实现代码，无法**复用**，有很多鸭子，就有很多不同的接口类。

针对接口编程，而不是针对实现编程

抽象出可变的行为，利用接口代表行为。而不是针对Duck类的具体实现。特定的实现写在行为的实现类中。

针对接口编程： 针对超类型编程，超类型可以理解为 抽象类和接口类；利用多态，执行时根据实际情况执行到真正的行为；将行为的具体实现委托给超类型。

```
class Demo{
    private Animal animal;
}
```










