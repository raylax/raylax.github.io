---
title: Java HashMap源码
date: 2021-02-21 14:17:28
tags:
	- java
categories:
	- java
---

# 常量
```java
// 默认初始容量2^4，必须为2的N次方
static final int DEFAULT_INITIAL_CAPACITY = 1 << 4;
// 最大容量2^30
static final int MAXIMUM_CAPACITY = 1 << 30;
// 默认扩容因子，当容量达到75%时进行扩容
static final float DEFAULT_LOAD_FACTOR = 0.75f;
// 树化阈值，当链表长度>=8时将链表转换成红黑树 
static final int TREEIFY_THRESHOLD = 8;
// 链表化阈值，当红黑树节点数量<=6时将红黑树转换成链表
static final int UNTREEIFY_THRESHOLD = 6;
// 最小树化阈值，只有map容量大于此值才进行链表树化，否则直接扩容
static final int MIN_TREEIFY_CAPACITY = 64; // 不能小于 4 * TREEIFY_THRESHOLD
```

# 变量
```java
// 存放数据的数组
transient Node<K,V>[] table;
// entity集合
transient Set<Map.Entry<K,V>> entrySet;
// 大小
transient int size;
// 扩容阈值，大于阈值将进行扩容
int threshold; // 容量 * 扩容因子
// 扩容因子
final float loadFactor;
```

# 构造函数
```java
public HashMap(int initialCapacity, float loadFactor) {
    if (initialCapacity < 0)
        throw new IllegalArgumentException("Illegal initial capacity: " +
                                           initialCapacity);
    // 如果初始容量大于最大容量则初始容量等于最大容量
    if (initialCapacity > MAXIMUM_CAPACITY)
        initialCapacity = MAXIMUM_CAPACITY;
    if (loadFactor <= 0 || Float.isNaN(loadFactor))
        throw new IllegalArgumentException("Illegal load factor: " +
                                           loadFactor);
    // 扩容因子
    this.loadFactor = loadFactor;
    // 扩容阈值
    this.threshold = tableSizeFor(initialCapacity);
}
```

## Node
```java
static class Node<K,V> implements Map.Entry<K,V> {
    // 节点hash值
    final int hash;
    // key
    final K key;
    // value
    V value;
    // 链表下一个节点
    Node<K,V> next;
}
```

## tableSizeFor(int cap)
返回大于等于输入参数且最近的2的整数次幂的数
```java
// 规定table数组的长度必须为2的n次方
// 2的n次方的数的特点为第n位为1其他均为0
// -1操作会使第1-(n-1)位全为1
// 假如cap的二进制位01xxxxxx
// 则大于等于cap且最近的2的整数次幂的数的二进制为10xxxxxx
static final int tableSizeFor(int cap) {
    int n = cap - 1;    // 假设n=1xxxxx
    n |= n >>> 1;       // n = 1xxxxx | 01xxxx = 11xxxx
    n |= n >>> 2;       // n = 11xxxx | 0011xx = 1111xx
    n |= n >>> 4;       // n = 1111xx | 000011 = 111111
    n |= n >>> 8;       // n = 111111 | 000000 = 111111
    n |= n >>> 16;      // n = 111111 | 000000 = 111111
    return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1; // +1得出最终的cap
}
```

# put(K key, V value)
向map放入key-value
```java
public V put(K key, V value) {
    return putVal(hash(key), key, value, false, true);
}
```

## hash(Object key)
```java
// 计算hash值
static final int hash(Object key) {
    int h;
    // 如果key为null则hash值为0
    // 否则调用key的hashCode方法获取hash值
    // 然后与其高16位进行异或返回
    // 这样做的原因是当数组很短的时候只有低位参与了运算
    // 让高十六位特征参与运算会更好的减少散列冲突
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

## putVal(int hash, K key, V value, boolean onlyIfAbsent, boolean evict)
```java
/**
 * @param hash hash值
 * @param key key
 * @param value value
 * @param onlyIfAbsent 如果是true则不改变已有值
 * @param evict 如果是false则为创建模式
 * @return 返回改变之前的值
 */
final V putVal(int hash, K key, V value, boolean onlyIfAbsent, boolean evict) {
    Node<K,V>[] tab; // 局部变量table
    Node<K,V> p; // 原始node
    int n; // table长度
    int i; // node在table中的位置

    // 判断table是否等于null或者为空
    // 如果为空则进行扩容
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;

    // 对hash值进行取模得到i
    // 当hash为2的次幂，x % hash == x & (hash - 1)
    // 位运算效率远远高于取模运算，所以这里使用位运算代替取模
    if ((p = tab[i = (n - 1) & hash]) == null)
        // 如果没有原始值，则new一个新node放入table
        tab[i] = newNode(hash, key, value, null);
    else {
        Node<K,V> e; // 已存在节点e
        K k; // 已存在节点的key
        if (p.hash == hash && ((k = p.key) == key || (key != null && key.equals(k))))
            // 如果hash值相等并且key相等
            e = p;
        else if (p instanceof TreeNode)
            // 如果p是一个红黑树则放入树中
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        else {
            // hash冲突情况，遍历链表
            for (int binCount = 0; ; ++binCount) {
                // 如果到链表尾，将节点添加到链表尾
                if ((e = p.next) == null) {
                    p.next = newNode(hash, key, value, null);
                    // 如果链表长度大于等于阈值则进行树化
                    if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                        treeifyBin(tab, hash);
                    break;
                }
                // 如果hash值相等并且key相等
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                // 设置p为当前链表节点
                p = e;
            }
        }
        // 判断是否存在旧值
        if (e != null) { // existing mapping for key
            V oldValue = e.value;
            // 改变旧值
            if (!onlyIfAbsent || oldValue == null)
                e.value = value;
            afterNodeAccess(e);
            // 返回旧值
            return oldValue;
        }
    }
    ++modCount;
    // 如果长度大于阈值则进行扩容
    if (++size > threshold)
        resize();
    afterNodeInsertion(evict);
    return null;
}
```

### resize()
```java
final Node<K,V>[] resize() {
    Node<K,V>[] oldTab = table;
    int oldCap = (oldTab == null) ? 0 : oldTab.length;
    int oldThr = threshold;
    int newCap, newThr = 0;

    // 如果旧容量大于0
    if (oldCap > 0) {
        // 如果旧容量大于等于最大容量，将扩容阈值改为int最大值
        if (oldCap >= MAXIMUM_CAPACITY) {
            threshold = Integer.MAX_VALUE;
            return oldTab;
        }
        // 新容量等于旧容量x2
        // 如果新容量小于最大容量，新阈值等于旧阈值*2
        else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                 oldCap >= DEFAULT_INITIAL_CAPACITY)
            newThr = oldThr << 1; // double threshold
    }
    // 如果旧阈值大于0，设置容量为阈值
    else if (oldThr > 0)
        newCap = oldThr;
    // 默认容量和阈值
    else {
        newCap = DEFAULT_INITIAL_CAPACITY;
        newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
    }

    // 如果新阈值为0计算新阈值
    if (newThr == 0) {
        float ft = (float)newCap * loadFactor;
        newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                  (int)ft : Integer.MAX_VALUE);
    }
    // 设置新阈值
    threshold = newThr;
    @SuppressWarnings({"rawtypes","unchecked"})
    // 创建新table
    Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
    table = newTab;
    if (oldTab != null) {
        // 遍历旧table
        for (int j = 0; j < oldCap; ++j) {
            // 当前节点
            Node<K,V> e;
            // 如果旧table里的node不为null
            if ((e = oldTab[j]) != null) {
                // 将旧table的node设置为null
                oldTab[j] = null;
                // 如果没有后继节点（即没有hash冲突）
                // 将当前节点放入新的table
                if (e.next == null)
                    newTab[e.hash & (newCap - 1)] = e;
                // 如果当前节点是红黑树，将红黑树拆分放入新的table
                else if (e instanceof TreeNode)
                    ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                else { // 如果有后继节点的情况（即有hash冲突）
                    Node<K,V> loHead = null;
                    Node<K,V> loTail = null;
                    Node<K,V> hiHead = null;
                    Node<K,V> hiTail = null;
                    // 下一个节点
                    Node<K,V> next;
                    do {
                        // 将next设置为当前节点的下一个节点
                        next = e.next;
                        // 如果扩容后index在原来的位置
                        if ((e.hash & oldCap) == 0) {
                            // 如果是初始状态，将当前节点设置为loHead
                            if (loTail == null)
                                loHead = e;
                            // 如果不是初始状态，将当前节点拼接到链表上
                            else
                                loTail.next = e;
                            // 设置loTail为当前节点
                            loTail = e;
                        }
                        // 如果扩容后index不在原来的位置
                        else {
                            // 同上
                            if (hiTail == null)
                                hiHead = e;
                            else
                                hiTail.next = e;
                            hiTail = e;
                        }
                    } while ((e = next) != null);
                    // 将扩容后未改变index的元素复制到新数组
                    if (loTail != null) {
                        loTail.next = null;
                        newTab[j] = loHead;
                    }
                    // 将扩容后改变了index位置的元素复制到新数组
                    if (hiTail != null) {
                        hiTail.next = null;
                        newTab[j + oldCap] = hiHead;
                    }
                }
            }
        }
    }
    return newTab;
}
```

`(e.hash & oldCap) == 0`用来判断扩容后的index是否改变
假设`capacity=8`、`threshold=6`，在添加第7个元素时进行扩容
```python
# 容量
capacity    = 8
# 扩容阈值
threshold   = 6
# 碰撞的index
index       = 5
# 碰撞的hash
keys        = [13, 21, 29, 37, 45, 53, 61]
# 根据index = hash & (n - 1)
#    cap - 1 = 8 - 1 = 0b00001000 - 1 = 0b00000111
# newCap - 1 = 8 - 1 = 0b00010000 - 1 = 0b00001111
# 可知当cap=8时index由后3位决定，当cap=16时index由后4位决定
# 想要判断index是否改变仅需要判断第4位是否为1，因为0xxx & 0111 == 0xxx & 1111

# hash  bin           index(cap=8)    index(cap=16)  &8
# -----------------------------------------------------
# 13    0b001101      0b0101=5        0b1101=13      0b1000
# 21    0b010101      0b0101=5        0b0101= 5      0b0000
# 29    0b011101      0b0101=5        0b1101=13      0b1000
# 37    0b100101      0b0101=5        0b0101= 5      0b0000
# 45    0b101101      0b0101=5        0b1101=13      0b1000
# 53    0b110101      0b0101=5        0b0101= 5      0b0000
# 61    0b111101      0b0101=5        0b1101=13      0b1000

# 如果&8不等于0，计算新index也很简单+0b1000(即旧cap)即可
```
