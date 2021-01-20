---
title: Java并发之AQS相关代码分析-ReentrantLock
date: 2021-01-12 14:17:28
tags:
	- java
	- AQS
categories:
	- java
---

# 概述

> Provides a framework for implementing blocking locks and related synchronizers (semaphores, events, etc) that rely on first-in-first-out (FIFO) wait queues. This class is designed to be a useful basis for most kinds of synchronizers that rely on a single atomic int value to represent state. Subclasses must define the protected methods that change this state, and which define what that state means in terms of this object being acquired or released. Given these, the other methods in this class carry out all queuing and blocking mechanics. Subclasses can maintain other state fields, but only the atomically updated int value manipulated using methods `getState`, `setState` and `compareAndSetState` is tracked with respect to synchronization.

AQS类是了一个实现了阻塞锁的抽象队列同步器，是`ReentrantLock`、`Semaphore`、`CountDownLatch`的基础
内部维护一个`state`状态值和一个`FIFO`队列

# 内部变量

```java
// 共享资源
private volatile int state
// 获取状态
protected final int getState();
// 设置状态
protected final void setState(int newState);
// CAS设置状态
protected final boolean compareAndSetState(int expect, int update);
// FIFO对列头
private transient volatile Node head;
// FIFO对列尾
private transient volatile Node tail;
```


# 详解
`ReentrantLock`是依赖`AQS`实现的一个可重入锁，我们通过分析`ReentrantLock`工作流程来分析`AQS`实现
`ReentrantLock`中实现了公平和非公平两种形似，暂且只分析公平锁

## lock
`lock`方法直接调用`AQS#acquire(int arg)`方法
```java
public final void acquire(int arg) {
	// 如果获取到资源直接返回
    if (!tryAcquire(arg) &&
    	// 如果获取资源失败进入等待对列
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg))
        selfInterrupt();
}
```
### tryAcquire
`tryAcquire`方法由子类`ReentrantLock.FairSync`类实现
```java
protected final boolean tryAcquire(int acquires) {
	// 获取当前线程
    final Thread current = Thread.currentThread();
    // 获取资源
    int c = getState();
    // 如果状态是未锁定
    if (c == 0) {
    	// 如果不需要排队等待则CAS设置state值
        if (!hasQueuedPredecessors() 
        	&& compareAndSetState(0, acquires)) {
        	// 设置独占线程
            setExclusiveOwnerThread(current);
            return true;
        }
    }
    // 如果资源已经锁定并且独占线程是当前线程
    else if (current == getExclusiveOwnerThread()) {
    	// 增加state值
        int nextc = c + acquires;
        // 判断是否溢出
        if (nextc < 0)
            throw new Error("Maximum lock count exceeded");
        // 设置状态值
        // 只有独占的同一个线程才能进入这个分支，所以这里无需使用CAS
        setState(nextc);
        return true;
    }
    // 如果上述条件都不符合说明获取失败
    return false;
}
```
#### hasQueuedPredecessors
```java
// 判断队列中是否有正在等待的
public final boolean hasQueuedPredecessors() {
	// 根据enq方法可知，如果head和tail二者只有一个为null只有可能是head不为null，tail为null
    Node t = tail;
    Node h = head;
    Node s;
    // h == t
    // h == t == null   未初始化过
    // h == t != null   对列中只有一个等待者
    return h != t &&
        ((s = h.next) == null || s.thread != Thread.currentThread());
}
```
### addWaiter
```java
// 加入等待对列
private Node addWaiter(Node mode) {
	// 创建节点
    Node node = new Node(Thread.currentThread(), mode);
    // 如果对列尾不为null，说明已经初始化过
    Node pred = tail;
    if (pred != null) {
        node.prev = pred;
        // 设置新节点为尾节点
        if (compareAndSetTail(pred, node)) {
            pred.next = node;
            return node;
        }
    }
    // 如果没有初始化或者设置失败则进入自旋
    enq(node);
    return node;
}
```
#### enq
```java
private Node enq(final Node node) {
	// 自旋
    for (;;) {
        Node t = tail;
        if (t == null) { // 初始化
            if (compareAndSetHead(new Node()))
            	// 如果此时发生并发则head不为null，tail为null
                tail = head;
        } else {
            node.prev = t;
            if (compareAndSetTail(t, node)) {
                t.next = node;
                return t;
            }
        }
    }
}
```
### acquireQueued
```java
// 等待获取
final boolean acquireQueued(final Node node, int arg) {
	// 是否失败
    boolean failed = true;
    try {
    	// 是否中断
        boolean interrupted = false;
        for (;;) {
        	// 获取前置节点
            final Node p = node.predecessor();
            // 如果前置节点是头节点则尝试获取
            if (p == head && tryAcquire(arg)) {
            	// 如果获取成功则将当前节点设置成头节点
                setHead(node);
                p.next = null; // help GC
                failed = false;
                return interrupted;
            }
            // 判断是否需要挂起
            if (shouldParkAfterFailedAcquire(p, node) &&
            	// 挂起当前线程
                parkAndCheckInterrupt())
                interrupted = true;
        }
    } finally {
    	// 如果失败取消获取
        if (failed)
            cancelAcquire(node);
    }
}
```
#### shouldParkAfterFailedAcquire
```java
private static boolean shouldParkAfterFailedAcquire(Node pred, Node node) {
	// 前置节点状态 0初始状态 小于0表示节点有效 大于0表示已取消
    int ws = pred.waitStatus;
    // 如果waitStatus已经设置好了直接返回
    if (ws == Node.SIGNAL)
        return true;
    // 如果前置节状态无效
    if (ws > 0) {
    	// 依次向前查找有效节点
        do {
            node.prev = pred = pred.prev;
        } while (pred.waitStatus > 0);
        // 设置前置节点
        pred.next = node;
    } else {
    	// 设置waitStatus信号量
        compareAndSetWaitStatus(pred, ws, Node.SIGNAL);
    }
    return false;
}
```
#### cancelAcquire
```java
private void cancelAcquire(Node node) {
	// 如果节点已经不存在，直接忽略
    if (node == null)
        return;
    // 清除线程
    node.thread = null;
    // 前置节点
    Node pred = node.prev;
    // 循环向前寻找有效节点
    while (pred.waitStatus > 0)
        node.prev = pred = pred.prev;
    // 前置节点的下一个节点
    Node predNext = pred.next;
    // 设置节点为无效状态
    node.waitStatus = Node.CANCELLED;
    // 如果当前节点是尾节点，则直接设置尾节点为当前节点前第一个有效节点
    if (node == tail && compareAndSetTail(node, pred)) {
    	// 设置前置节点的next为null
        compareAndSetNext(pred, predNext, null);
    } else {
        int ws;
        // 前置节点不是头节点
        if (pred != head &&
        	// 如果前置节点等于SIGNAL或者可以设置为SIGNAL，并且前置节点的线程不是null
            ((ws = pred.waitStatus) == Node.SIGNAL ||
             (ws <= 0 && compareAndSetWaitStatus(pred, ws, Node.SIGNAL))) &&
            pred.thread != null) {
        	// 将当前节点的后置节点设置为前置节点的后置节点
            Node next = node.next;
            if (next != null && next.waitStatus <= 0)
                compareAndSetNext(pred, predNext, next);
        } else {
        	// 如果前置节点是头节点则唤醒后置节点
            unparkSuccessor(node);
        }

        node.next = node;
    }
}
```
##### unparkSuccessor
```java
// 唤醒节点的后置节点
private void unparkSuccessor(Node node) {
    int ws = node.waitStatus;
    // 如果是正常状态则设置为初始状态
    if (ws < 0)
        compareAndSetWaitStatus(node, ws, 0);

    // 取后置节点
    Node s = node.next;
    // 如果后置节点不是null并且后置节点状态无效
    if (s == null || s.waitStatus > 0) {
        s = null;
        // 从尾部向前遍历有效节点
        for (Node t = tail; t != null && t != node; t = t.prev)
            if (t.waitStatus <= 0)
                s = t;
    }
    // 如果节点存在，唤醒节点
    if (s != null)
        LockSupport.unpark(s.thread);
}
```

## unlock
`lock`方法直接调用`AQS#release(int arg)`方法

```java
public final boolean release(int arg) {
	// 尝试释放
    if (tryRelease(arg)) {
        Node h = head;
        // 如果释放成功并且waitStatus不是初始状态
        if (h != null && h.waitStatus != 0)
        	// 唤醒后置及节点
            unparkSuccessor(h);
        return true;
    }
    return false;
}
```
### tryRelease
```java
protected final boolean tryRelease(int releases) {
	// 更后的state
    int c = getState() - releases;
    // 如果当前线程不是锁的拥有者，直接抛出异常
    if (Thread.currentThread() != getExclusiveOwnerThread())
        throw new IllegalMonitorStateException();
    boolean free = false;
    if (c == 0) {
        free = true;
        // 清除独占
        setExclusiveOwnerThread(null);
    }
    // 设置新的state
    setState(c);
    return free;
}
```

## 非公平模式

> 上面讲了公平模式`ReentrantLock`也可以设置为非公平模式，主要区别在获取时并不判断当前线程是否是等待队列头

```java
final boolean nonfairTryAcquire(int acquires) {
    // 当前线程
    final Thread current = Thread.currentThread();
    // 当前状态
    int c = getState();
    // 如果未锁定状态
    if (c == 0) {
        // CAS设置状态
        if (compareAndSetState(0, acquires)) {
            // 设置独占线程
            setExclusiveOwnerThread(current);
            return true;
        }
    }
    // 如果独占线程是当前线程，增加状态
    else if (current == getExclusiveOwnerThread()) {
        int nextc = c + acquires;
        // 判断溢出
        if (nextc < 0) // overflow
            throw new Error("Maximum lock count exceeded");
        // 设置状态
        setState(nextc);
        return true;
    }
    return false;
}
```