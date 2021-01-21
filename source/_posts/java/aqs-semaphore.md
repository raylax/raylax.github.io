---
title: Java并发之AQS相关代码分析-Semaphore
date: 2021-01-20 12:06:01
tags:
	- java
	- AQS
categories:
	- java
---

# 方法

```java
// 构造方法
public Semaphore(int permits, boolean fair);
// 获取许可
public void acquire() throws InterruptedException;
// 释放许可
public void release();
```

# 源码分析

## 构造方法
```java
public Semaphore(int permits, boolean fair) {
    sync = fair ? new FairSync(permits) : new NonfairSync(permits);
}
// 基础同步器
abstract static class Sync extends AbstractQueuedSynchronizer {
    Sync(int permits) {
        setState(permits); // 设置许可数量
    }
    final int getPermits() {
        return getState(); // 获取许可数量
    }
    // 非公平获取共享状态
    final int nonfairTryAcquireShared(int acquires) {
        for (;;) {
            int available = getState(); // 获取可用许可数量
            int remaining = available - acquires; // 计算剩余许可数量
            if (remaining < 0 ||
                compareAndSetState(available, remaining))
                return remaining; // 如果剩余数量小于0或者CAS设置剩余数量成功返回剩余数量否则自旋
        }
    }
    // 释放共享状态
    protected final boolean tryReleaseShared(int releases) {
        for (;;) {
            int current = getState(); // 获取当前可用许可数量
            int next = current + releases; // 计算释放后许可数量
            if (next < current) // 检查溢出
                throw new Error("Maximum permit count exceeded");
            if (compareAndSetState(current, next)) // CAS设置新的许可数量
                return true;
        }
    }

    // 减少许可数量
    final void reducePermits(int reductions) {
        for (;;) {
            int current = getState(); // 获取当前可用许可数量
            int next = current - reductions; // 计算减少后数量
            if (next > current) // 检查溢出
                throw new Error("Permit count underflow");
            if (compareAndSetState(current, next)) // CAS设置减少后的数量
                return;
        }
    }
    // 清空许可
    final int drainPermits() {
        for (;;) {
            int current = getState();
            if (current == 0 || compareAndSetState(current, 0))
                return current;
        }
    }
}
// 非公平模式
static final class NonfairSync extends Sync {
    private static final long serialVersionUID = -2694183684443567898L;

    NonfairSync(int permits) {
        super(permits);
    }

    // 尝试获取锁
    protected int tryAcquireShared(int acquires) {
        return nonfairTryAcquireShared(acquires);
    }
}

// 公平模式
static final class FairSync extends Sync {
    private static final long serialVersionUID = 2014338818796000944L;

    FairSync(int permits) {
        super(permits);
    }

    // 尝试获取锁
    protected int tryAcquireShared(int acquires) {
        for (;;) {
        	// 如果有前置等待节点直接返回
            if (hasQueuedPredecessors())
                return -1;
            int available = getState(); // 获取可用许可数量
            int remaining = available - acquires; // 计算剩余许可数量
            if (remaining < 0 ||
                compareAndSetState(available, remaining)) // 如果剩余许可小于0或者CAS设置成功直接返回
                return remaining;
        }
    }
}
```

## acquire
调用AQS#acquireSharedInterruptibly(int arg)方法
```java
// AbstractQueuedSynchronizer
public final void acquireSharedInterruptibly(int arg) throws InterruptedException {
	// 判断中断
    if (Thread.interrupted())
        throw new InterruptedException();
    if (tryAcquireShared(arg) < 0) // 调用对应的Sync实现的tryAcquireShared方法
        doAcquireSharedInterruptibly(arg); // 如果小于0说明没有获取到
}
// AbstractQueuedSynchronizer
private void doAcquireSharedInterruptibly(int arg) throws InterruptedException {
	// 添加到等待队列
    final Node node = addWaiter(Node.SHARED);
    boolean failed = true;
    try {
        for (;;) {
        	// 获取前驱节点
            final Node p = node.predecessor();
            if (p == head) { // 如果前驱节点是头结点
                int r = tryAcquireShared(arg); // 尝试获取锁
                if (r >= 0) { // 如果获取成功
                    setHeadAndPropagate(node, r); // 设置当前节点为头结点
                    p.next = null; // help GC
                    failed = false;
                    return;
                }
            }
            if (shouldParkAfterFailedAcquire(p, node) && // 判断是否需要挂起
                parkAndCheckInterrupt()) // 挂起线程等待唤醒
                throw new InterruptedException();
        }
    } finally {
        if (failed)
            cancelAcquire(node); // 清理等待队列
    }
}
```
## releaseShared
在CountDownLatch一章有讲

> 以上所有未详细解释方法在前几章已经讲过