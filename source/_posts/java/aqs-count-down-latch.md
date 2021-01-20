---
title: Java并发之AQS相关代码分析-CountDownLatch
date: 2021-01-17 23:06:01
tags:
	- java
	- AQS
categories:
	- java
---

# 方法

```java
// 构造方法
public CountDownLatch(int count);
// 释放
public void countDown();
// 等待
public void await() throws InterruptedException;
// 等待（带超时时间）
public boolean await(long timeout, TimeUnit unit) throws InterruptedException
```

# 源码分析

## 构造方法
```java
// CountDownLatch
public CountDownLatch(int count) {
    if (count < 0) throw new IllegalArgumentException("count < 0");
    this.sync = new Sync(count);
}
// CountDownLatch.Sync
private static final class Sync extends AbstractQueuedSynchronizer {
    Sync(int count) {
    	// 设置state
        setState(count);
    }
}
```

## countDown
调用AQS#releaseShared(int arg)方法
```java
// AbstractQueuedSynchronizer
public final boolean releaseShared(int arg) {
	// 尝试释放共享资源
    if (tryReleaseShared(arg)) {
    	// 如果全部释放完成唤醒等待队列
        doReleaseShared();
        return true;
    }
    return false;
}
// CountDownLatch.Sync
protected boolean tryReleaseShared(int releases) {
	// 自旋
    for (;;) {
    	// 获取当前状态
        int c = getState();
        // 如果释放完了直接返回
        if (c == 0)
            return false;
        // 减一
        int nextc = c-1;
        // 如果CAS设置不成功自旋
        if (compareAndSetState(c, nextc))
            return nextc == 0; // 如果等于0说明全部释放完成
    }
}
// AbstractQueuedSynchronizer
private void doReleaseShared() {
    for (;;) {
        Node h = head;
        if (h != null && h != tail) {
            int ws = h.waitStatus;
            if (ws == Node.SIGNAL) {
                if (!compareAndSetWaitStatus(h, Node.SIGNAL, 0))
                    continue;
                // unparkSuccessor相关源码在ReentrantLock已经讲过
                unparkSuccessor(h); // 如果是SIGNAL并且CAS设置初始状态成功则唤醒线程
            }
            else if (ws == 0 &&
                     !compareAndSetWaitStatus(h, 0, Node.PROPAGATE)) // 如果是初始状态则设置状态为PROPAGATE
                continue;
        }
        if (h == head) // 正常调用过unparkSuccessor后其他线程会竞争改变head，如果head没变跳出循环
            break;
    }
}
```

## await
调用AQS#acquireSharedInterruptibly(int arg)方法
```java
// AbstractQueuedSynchronizer
public final void acquireSharedInterruptibly(int arg) throws InterruptedException {
	// 如果线程被中断，抛出中断异常
    if (Thread.interrupted())
        throw new InterruptedException();
    if (tryAcquireShared(arg) < 0)
        doAcquireSharedInterruptibly(arg); // 如果还有待释放的state值
}
// CountDownLatch.Sync
protected int tryAcquireShared(int acquires) {
	// 如果全部释放返回1否则返回-1
    return (getState() == 0) ? 1 : -1;
}
// AbstractQueuedSynchronizer
private void doAcquireSharedInterruptibly(int arg) throws InterruptedException {
	// 添加到共享等待队列，相关源码在ReentrantLock已经讲过
    final Node node = addWaiter(Node.SHARED);
    boolean failed = true;
    try {
        for (;;) {
        	// 获取当前节点的前驱节点
            final Node p = node.predecessor();
            // 如果前驱节点是头节点，再次尝试获取
            if (p == head) {
                int r = tryAcquireShared(arg);
                // >=0 说明state==0 countdown结束
                if (r >= 0) {
                	// 设置当前节点为head并向后传播
                    setHeadAndPropagate(node, r);
                    p.next = null; // help GC
                    failed = false;
                    return;
                }
            }
            // 如果获取失败
            if (shouldParkAfterFailedAcquire(p, node)  // 判断是否可以挂起线程
            	&& parkAndCheckInterrupt()) // 挂起线程等待唤醒
                throw new InterruptedException();
        }
    } finally {
    	// 如果失败了则取消获取
        if (failed)
            cancelAcquire(node);
    }
}
// AbstractQueuedSynchronizer
private void setHeadAndPropagate(Node node, int propagate) {
	// 保存原始head
    Node h = head;
    // 把当前节点设置为head
    setHead(node);
    // propagate > 0 永远是true
    // 如果头节点是null或者waitStatus是有效地
    if (propagate > 0 || h == null || h.waitStatus < 0 || (h = head) == null || h.waitStatus < 0) {
        Node s = node.next;
        // 如果后继节点是共享的释放共享锁
        if (s == null || s.isShared())
            doReleaseShared();
    }
}
```

## await(long timeout, TimeUnit unit)
调用AQS#tryAcquireSharedNanos(int arg, long nanosTimeout)方法
```java
// AbstractQueuedSynchronizer
public final boolean tryAcquireSharedNanos(int arg, long nanosTimeout) throws InterruptedException {
    if (Thread.interrupted())
        throw new InterruptedException();
    // 如果获取成功直接返回
    return tryAcquireShared(arg) >= 0 ||
        doAcquireSharedNanos(arg, nanosTimeout); //  超时等待
}
// AbstractQueuedSynchronizer
static final long spinForTimeoutThreshold = 1000L;
private boolean doAcquireSharedNanos(int arg, long nanosTimeout) throws InterruptedException {
    if (nanosTimeout <= 0L)
        return false;
    // 计算deadline
    final long deadline = System.nanoTime() + nanosTimeout;
    // 添加到等待队列
    final Node node = addWaiter(Node.SHARED);
    boolean failed = true;
    try {
        for (;;) {
            final Node p = node.predecessor();
            if (p == head) {
            	// 尝试获取
                int r = tryAcquireShared(arg);
                if (r >= 0) {
                    setHeadAndPropagate(node, r);
                    p.next = null; // help GC
                    failed = false;
                    return true;
                }
            }
            // 重新计算超时时间
            nanosTimeout = deadline - System.nanoTime();
            if (nanosTimeout <= 0L)
                return false;
            if (shouldParkAfterFailedAcquire(p, node) &&
                	nanosTimeout > spinForTimeoutThreshold) // 如果超过1000才会挂起线程，否则直接自旋
                LockSupport.parkNanos(this, nanosTimeout); // 带超时挂起线程
            // 如果中断抛出异常
            if (Thread.interrupted())
                throw new InterruptedException();
        }
    } finally {
    	// 如果失败了则取消获取
        if (failed)
            cancelAcquire(node);
    }
}
```


> 以上所有未详细解释方法在ReentrantLock已经讲过