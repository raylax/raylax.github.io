---
title: java-String/StringBuilder/StringBuffer区别
date: 2019-01-28 22:29:04
tags:
	- java
categories:
	- java
---
### String
```java
/*
 * java.lang.String部分代码
 */
public final class String
    implements java.io.Serializable, Comparable<String>, CharSequence {
    /** The value is used for character storage. */
    private final char value[];
}
```
首先*String*是一个*final*修饰不可继承的类，内部使用*final*修饰的*char[]*来保存数据，String是不可变的
```java
String str = "123";
System.out.println((str + "456") == str);
// output : false
```
每次对String拼接都会创建一个新String对象

### AbstractStringBuilder
*AbstractStringBuilder*是一个抽象类，是*StringBuilder*和*StringBuffer*的父类，二者大部分操作都是基于此类实现的
```java
/*
 * java.lang.AbstractStringBuilder部分代码
 */
abstract class AbstractStringBuilder 
	implements Appendable, CharSequence {
    /**
     * The value is used for character storage.
     */
    char[] value;

    /**
     * The count is the number of characters used.
     */
    int count;
}
```
*AbstractStringBuilder*是一个可变的字符串类，内部使用*char[]*来保存数据，*count*用来记录*value*已用长度。
每次*append*操作都会向*value*中添加数据，若数组容量不够则进行扩容，扩容后容量是原容量的2倍
*append*操作并不会创建新对象，而是在原有对象上进行修改，所以*AbstractStringBuilder*是可变的
```java
StringBuilder bd = new StringBuilder("123");
System.out.println(bd.append("345") == bd);
// output : true
StringBuffer bf = new StringBuffer("123");
System.out.println(bf.append("345") == bf);
// output : true
```

#### StringBuilder
*StringBuilder*继承*AbstractStringBuilder*类所有方法均调用父类实现

#### StringBuffer
*StringBuilder*继承*AbstractStringBuilder*类所有方法均调用父类实现
所有方法均使用*synchronized*关键字修饰，所以*StringBuffer*是线程安全的

### 结语
实际上在编译期优化了的`string+`操作的运行效率并非低于使用其他两个类
因为许多编译器会将此操作优化为`builder.append`的形式
理论上执行效率 StringBuilder > StringBuffer > String



