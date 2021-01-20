---
title: java并发-volatile关键字
date: 2019-01-24 14:16:31
tags:
	- java
	- 并发
categories:
	- java
---
### 引言
前一篇文章讲了java内存模型相关概念，线程在工作的时候会从主内存中复制数据到工作内存中进行操作，这样多线程情况下就会出现数据一致性问题，使用*volatile*关键字则可以避免此问题。

### 作用
如果使用*volatile*关键字修饰一个类的(静态)成员变量，则有两种作用
- 确保了多线程对此变量的可见性
每次获取变量会强制从主内存获取，每次修改变量后会立即刷新到主内存
- 禁止进行指令重排(java虚拟为了优化执行效率会进行指令重排，暂不详细说明)

### volatile可以保证原子性么
volatile仅能确保每次获取的数据都是最新的数据，并不能保证原子性
```java
public class VolatileTest {
    private volatile int count = 0;
    public static void main(String[] args) throws Exception {
        VolatileTest v = new VolatileTest();
        List<Thread> threads = new ArrayList<>(10);
        // 创建10个线程
        for (int i = 0; i < 10; i++) {
            threads.add(new Thread(() -> {
                // 每个线程增加10000
                for (int j = 0; j< 10000; j++) {
                    v.count++;
                }
            }));
        }
        // 启动
        threads.forEach(Thread::start);
        for (Thread thread : threads) {
            thread.join();
        }
        System.out.println(v.count);
    }
}
```
结果应该是100000，实际上这段代码运行结果并不是100000，因为*count++*操作不是一个原子操作，*++*操作会先获取*count*变量然后对其加一刷新到主内存
多线程情况下可能多个线程同时获取了该变量对其操作然后刷新到主内存。例如数据是5，2条线程同时获取了该变量对其+1，同时将6刷新到主内存，这时主内存的数据是6但我们期望的是7
要解决这个问题可以用*synchronized*和*ReentrantLock*对要操作的数据加同步锁解决此问题

#### synchronized解决方式
synchronized方式通过java内置字节码指令*monitorenter*和*monitorexit*实现的
```java
public class VolatileTest {
    private volatile int count = 0;
    private volatile Object countMutex = new Object();
    public static void main(String[] args) throws Exception {
        VolatileTest v = new VolatileTest();
        List<Thread> threads = new ArrayList<>(10);
        // 创建10个线程
        for (int i = 0; i < 10; i++) {
            threads.add(new Thread(() -> {
                // 每个线程增加10000
                for (int j = 0; j< 10000; j++) {
                    // 加锁
                    synchronized (v.countMutex) {
                        v.count++;
                    }
                }
            }));
        }
        // 启动
        threads.forEach(Thread::start);
        for (Thread thread : threads) {
            thread.join();
        }
        System.out.println(v.count);
    }
}
````

#### ReentrantLock解决方式
ReentrantLock方式通过*CAS*方式实现
```java
public class VolatileTest {
    private volatile int count = 0;
    public static void main(String[] args) throws Exception {
        VolatileTest v = new VolatileTest();
        List<Thread> threads = new ArrayList<>(10);
        ReentrantLock lock = new ReentrantLock();
        // 创建10个线程
        for (int i = 0; i < 10; i++) {
            threads.add(new Thread(() -> {
                // 每个线程增加10000
                for (int j = 0; j< 10000; j++) {
                    // 加锁
                    lock.lock();
                    v.count++;
                    lock.unlock();
                }
            }));
        }
        // 启动
        threads.forEach(Thread::start);
        for (Thread thread : threads) {
            thread.join();
        }
        System.out.println(v.count);
    }
}
````



