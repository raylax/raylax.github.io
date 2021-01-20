---
title: java集合-List类
date: 2019-01-27 22:47:17
tags:
	- java
	- 集合
categories:
	- java
---
### ArrayList
ArrayList内部使用数组实现

内部关键变量
```java
// 默认初始容量
private static final int DEFAULT_CAPACITY = 10;
// 空列表常量
private static final Object[] EMPTY_ELEMENTDATA = {};
// 默认空列表常量
private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};
// 存放数据数组
transient Object[] elementData;
// 列表大小(列表大小并不总是等于elementData.length，因为elementData会有冗余)
private int size;
```
构造方法
```java
/* 
 * 创建一个初始容量为0空列表
 * 使用DEFAULTCAPACITY_EMPTY_ELEMENTDATA填充elementData
 */
public ArrayList();
/* 
 * 如果initialCapacity大于0，创建一个初始容量为initialCapacity的列表
 * 为elementData创建一个大小为initialCapacity的数组
 *
 * 如果initialCapacity等于0，创建一个初始容量为0的数组
 * 使用EMPTY_ELEMENTDATA填充elementData
 * 
 * 如果initialCapacity小于0，抛出IllegalArgumentException
 */
public ArrayList(int initialCapacity);
/*
 * 传入一个集合如果c长度不为0，将c的数组复制到elementData
 * c的长度赋值到size
 */
public ArrayList(Collection<? extends E> c);
```
#### 扩容机制
如果使用无参构造创建List，在第一次扩容时如果如果期望容量小于10则会将容量设置为10
后续扩容`newCapacity = oldCapacity + (oldCapacity >> 1)`也就是说每次扩容后大小是原数组大小的1.5倍

#### RandomAccess
ArrayList实现了*RandomAccess*接口，实际上*RandomAccess*内部并无需要实现的方法
此接口只是为了标识该列表支持随机访问，也就是支持按下标访问
主要用于`Collections.binarySearch`等方法区分查找方式

### LinkedList
LinkedList内部使用双向链表实现

内部关键变量
```java
// 列表大小
transient int size = 0;
// 第一个节点指针
transient Node<E> first;
// 最后一个节点指针
transient Node<E> last;
// 内部Node
class Node<E> {
	// 实际对象
    E item;
    // 指向上一个对象
    Node<E> next;
    // 指向下一个对象
    Node<E> prev;
}
```

#### 运行原理
向头部添加对象会创建一个next指向first的新节点，将first指向新节点
向指定位置添加对象创建一个prev指向该位置元素的prev，last指向该对象的新节点，原对象prev指向新节点
向尾部添加对象会创建一个prev指向last的新节点，将last指向新节点

#### Deque
LinkedList实现了*Deque*接口，说明LinkedList实现了可以当做一个双向队列使用，LinkedList使用的数据结构完美的支持双向队列

### 时间复杂度对比

操作\类型			| ArrayList 	| LinkedList
--					|	:--:		|	:--:
获取指定位置对象		| $O(1)$ 		| $O(n)$
向头部添加对象		| $O(n)$ 		| $O(1)$
向指定位置添加对象		| $O(n)$ 		| $O(n)$
向尾部添加对象		| $O(1)$ 		| $O(1)$
删除头部对象			| $O(n)$ 		| $O(1)$
删除指定位置对象		| $O(n)$ 		| $O(n)$
删除尾部对象			| $O(1)$ 		| $O(1)$

### Vector与ArrayList区别
*Vector*与*ArrayList*实现原理基本类似
主要区别在于，*Vector*每个方法都是加了*synchronized*同步的，是线程安全的
而*ArrayList*是非线程安全的
