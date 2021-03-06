---
title: Java HashMap源码之树化
date: 2021-02-22 14:17:28
tags:
	- java
categories:
	- java
---

> hashmap会在hash冲突达到特定阈值之后将链表转换成红黑树

# TreeNode<K, V>
```java
static final class TreeNode<K,V> extends LinkedHashMap.Entry<K,V> {
    TreeNode<K,V> parent;  // red-black tree links
    TreeNode<K,V> left;
    TreeNode<K,V> right;
    TreeNode<K,V> prev;    // needed to unlink next upon deletion
    boolean red;
    TreeNode(int hash, K key, V val, Node<K,V> next) {
        super(hash, key, val, next);
    }

    // 查找根节点
    final TreeNode<K,V> root() {
        for (TreeNode<K,V> r = this, p;;) {
            if ((p = r.parent) == null)
                return r;
            r = p;
        }
    }

    // 将根节点设置为table相对应的位置
    static <K,V> void moveRootToFront(Node<K,V>[] tab, TreeNode<K,V> root) {
        int n;
        if (root != null && tab != null && (n = tab.length) > 0) {
        	// 计算index
            int index = (n - 1) & root.hash;
            // 原链表头结点
            TreeNode<K,V> first = (TreeNode<K,V>)tab[index];
            // 如果原链表头结不等于根节点
            if (root != first) {
            	// 后继节点
                Node<K,V> rn;
                // 将根节点放入table
                tab[index] = root;
                // root的前驱节点
                TreeNode<K,V> rp = root.prev;
                // 如果root存在后继节点，则将他的前驱节点设置为root的前驱节点
                if ((rn = root.next) != null)
                    ((TreeNode<K,V>)rn).prev = rp;
                // 如果root存在前驱节点，则将他的后继节点设置为root的后继节点
                if (rp != null)
                    rp.next = rn;
                // 如果原始节点存在
                if (first != null)
                    first.prev = root;
                // 将根节点的后继节点设置为原始节点
                root.next = first;
                // 将根节点的前置节点设置为null
                root.prev = null;
            }
            // 验证红黑树准确性
            assert checkInvariants(root);
        }
    }

    // 查找
    // h  = hash value 
    // k  = key 
    // kc = key class
    final TreeNode<K,V> find(int h, Object k, Class<?> kc) {
        TreeNode<K,V> p = this; // 当前节点
        do {
            int ph; // hash值
            int dir; // 方向
            K pk; // key
            TreeNode<K,V> pl = p.left; // 左子节点
            TreeNode<K,V> pr = p.right; // 右子节点
            TreeNode<K,V> q; // 要找的对象
            // 如果当前节点的hash值大于要找的hash值则让左子节点进行下一轮查找
            if ((ph = p.hash) > h)
                p = pl;
            // 如果当前节点的hash值小于要找的hash值则让右子节点进行下一轮查找
            else if (ph < h)
                p = pr;
            // 如果hash值相等并且key值相等，说明找到了，直接返回
            else if ((pk = p.key) == k || (k != null && k.equals(pk)))
                return p;
            // 如果hash值相等并且左子节点为空让右子节点进行下一轮查找
            else if (pl == null)
                p = pr;
            // 如果hash值相等并且右子节点为空让左子节点进行下一轮查找
            else if (pr == null)
                p = pl;
            // 使用comparable接口进行比较来选择向左还是右查找
            else if ((kc != null ||
                      (kc = comparableClassFor(k)) != null) &&
                     (dir = compareComparables(kc, k, pk)) != 0)
                p = (dir < 0) ? pl : pr;
            // 如果comparable比较后还是相等则使用右子树进行递归查找
            else if ((q = pr.find(h, k, kc)) != null)
                return q;
            // 如果右子树查找不到，则使用左子树进行下一轮查找
            else
                p = pl;
        } while (p != null);
        return null;
    }

    // 获取key所在的node
    final TreeNode<K,V> getTreeNode(int h, Object k) {
        return ((parent != null) ? root() : this).find(h, k, null);
    }

    // 比较两个对象返回-1或1
    static int tieBreakOrder(Object a, Object b) {
        int d;
        if (a == null || b == null ||
            (d = a.getClass().getName().
             compareTo(b.getClass().getName())) == 0)
            d = (System.identityHashCode(a) <= System.identityHashCode(b) ?
                 -1 : 1);
        return d;
    }

    // 树化
    final void treeify(Node<K,V>[] tab) {
    	// 根节点
        TreeNode<K,V> root = null; 
        // 遍历链表，x指向当前节点，next指向下一个节点
        for (TreeNode<K,V> x = this, next; x != null; x = next) {
            next = (TreeNode<K,V>)x.next;
            x.left = x.right = null;
            if (root == null) { // 如果还没有根节点
                x.parent = null; // 设置父节点为空
                x.red = false; // 设置为黑色
                root = x; // 将当前节点设置为根节点
            }
            else {
                K k = x.key; // 当前节点的key
                int h = x.hash; // 当前节点的hash
                Class<?> kc = null; // 当前key的class
                for (TreeNode<K,V> p = root;;) { // 从根节点遍历
                    int dir; // 方向
                    int ph; // p hash
                    K pk = p.key; // p key
                    // 如果p hash大于当前节点的hash设置dir为-1表示向左插入
                    if ((ph = p.hash) > h)
                        dir = -1;
                    // 如果p hash小于当前节点的hash设置dir为1表示向右插入
                    else if (ph < h)
                        dir = 1;
                    // 如果相等，使用comparable接口比较
                    else if ((kc == null &&
                              (kc = comparableClassFor(k)) == null) ||
                             (dir = compareComparables(kc, k, pk)) == 0)
                    	// 如果comparable接口比较还是相等
                        dir = tieBreakOrder(k, pk);
                    // 保存p节点
                    TreeNode<K,V> xp = p;
                    // 如果dir小于0一定放入当前节点的左侧
                    // 如果dir大于0一定放入当前节点的右侧
                    // 如果要插入的左侧节点为null或者要插入的右侧节点为null，执行插入逻辑
                    // 否则将p设置为left或者right进行下一次循环
                    if ((p = (dir <= 0) ? p.left : p.right) == null) {
                    	// 当前节点的父节点设置为p
                        x.parent = xp;
                        // 如果小于0，设置为左子节点
                        if (dir <= 0)
                            xp.left = x;
                        // 如果大于0，设置为右子节点
                        else
                            xp.right = x;
                        // 执行红黑树平衡插入并且重新设置root
                        root = balanceInsertion(root, x);
                        break;
                    }
                }
            }
        }
        // 将root节点设置到table
        moveRootToFront(tab, root);
    }

    // 取消树化
    final Node<K,V> untreeify(HashMap<K,V> map) {
        Node<K,V> hd = null; // 链表头
        Node<K,V> tl = null; // 链表尾
        // 遍历链表
        for (Node<K,V> q = this; q != null; q = q.next) {
        	// 将treenode转换成普通node
            Node<K,V> p = map.replacementNode(q, null);
            // 如果链表尾没初始化将头设置为当前节点
            if (tl == null)
                hd = p;
            // 如果已经初始化将当前节点拼接到链表尾
            else
                tl.next = p;
            // 将链表尾设置为当前节点
            tl = p;
        }
        // 返回链表头
        return hd;
    }

    /**
     *  map   = hashmap对象
     *  table = table
     *  h     = hash值
     *  k     = key
     *  v     = value
     */
    final TreeNode<K,V> putTreeVal(HashMap<K,V> map, Node<K,V>[] tab,
                                   int h, K k, V v) {
        // key class
        Class<?> kc = null;
        // 是否搜索过一次
        boolean searched = false;
        // 获取根节点
        TreeNode<K,V> root = (parent != null) ? root() : this;
        // 遍历红黑树
        for (TreeNode<K,V> p = root;;) {
            int ph; // hash值
            int dir; // 方向
            K pk; // key
            // 如果当前节点hash值大于key的hash值向左查找
            if ((ph = p.hash) > h)
                dir = -1;
            // 如果当前节点hash值小于key的hash值向有查找
            else if (ph < h)
                dir = 1;
            // 如果hash值相等并且key相等，返回当前节点
            else if ((pk = p.key) == k || (k != null && k.equals(pk)))
                return p;
            // 如果hash值相等但是key不相等
            else if ((kc == null &&
                      (kc = comparableClassFor(k)) == null) ||
                     (dir = compareComparables(kc, k, pk)) == 0) {
                // 如果没有搜索过则向左右搜索
                if (!searched) {
                    TreeNode<K,V> q, ch;
                    searched = true;
                    // 分别向左右查找
                    if (((ch = p.left) != null &&
                         (q = ch.find(h, k, kc)) != null) ||
                        ((ch = p.right) != null &&
                         (q = ch.find(h, k, kc)) != null))
                        // 如果找到直接返回
                        return q;
                }
                // 判断方向
                dir = tieBreakOrder(k, pk);
            }

            TreeNode<K,V> xp = p; // 保存当前节点
            // 如果dir所指的方向为null，说明需要创建新节点
            if ((p = (dir <= 0) ? p.left : p.right) == null) {
                Node<K,V> xpn = xp.next; // 保存当前节点的后继节点
                // 创建一个新节点将当前节点的后继节点设置为新节点的后继节点
                TreeNode<K,V> x = map.newTreeNode(h, k, v, xpn);
                // 如果向左插入将当前节点的左节点设置为新节点
                if (dir <= 0)
                    xp.left = x;
                // 如果向右插入将当前节点的有节点设置为新节点
                else
                    xp.right = x;
                // 将当前节点后继节点设置为新节点
                xp.next = x;
                // 将新节点的父节点和前置节点设置为当前节点
                x.parent = x.prev = xp;
                // 如果当前节点的后继节点不是null将当前节点的前置节点拼接到新节点
                if (xpn != null)
                    ((TreeNode<K,V>)xpn).prev = x;
                // 插入红黑树
                moveRootToFront(tab, balanceInsertion(root, x));
                return null;
            }
        }
    }

    
    final void removeTreeNode(HashMap<K,V> map, Node<K,V>[] tab,
                              boolean movable) {
        int n; // table长度
        // 如果table为空直接返回
        if (tab == null || (n = tab.length) == 0)
            return;
        // 根据hash值计算index
        int index = (n - 1) & hash;
        // 头节点
        TreeNode<K,V> first = (TreeNode<K,V>)tab[index];
        // 根节点
        TreeNode<K,V> root = first;
        // 左子节点
        TreeNode<K,V> rl;
        // 当前节点的后驱节点
        TreeNode<K,V> succ = (TreeNode<K,V>)next;
        // 当前节点的前驱结点
        TreeNode<K,V> pred = prev;

        // 维护双向链表
        // 如果前驱节点为空说明是头节点，将头节点设置为当前节点的后驱节点
        if (pred == null)
            tab[index] = first = succ;
        // 前驱节点不为空，将前驱节点的后驱节点设置为当前节点的后驱节点
        else
            pred.next = succ;

        // 如果后驱节点不为空，将后驱节点的前驱节点设置为当前节点的前驱节点
        if (succ != null)
            succ.prev = pred;

        // 如果头节点为空直接返回
        if (first == null)
            return;

        // 如果root不是根节点，重新获取根节点
        if (root.parent != null)
            root = root.root();
        /**
         * 当以下三个条件任一满足时，当满足红黑树条件时，说明该位置元素的长度少于6（UNTREEIFY_THRESHOLD），需要对该位置元素链表化
         * 1. root == null 根节点为空，树节点数量为0
         * 2. root.right == null 右孩子为空，树节点数量最多为2
                 +----+                                                                                             
                 | 1  |                                                                                             
                 +----+                                                                                             
                   /\                                                                                               
                  /  \                                                                                              
            +-----    -----+                                                                                        
            | 2  |    |NULL|                                                                                        
            +----+    +----+
         * 3. (rl = root.left) == null || rl.left == null)
         *    (rl = root.left) == null：左孩子为空，树节点数最多为2
                 +----+                                                                                             
                 | 1  |                                                                                             
                 +----+                                                                                             
                   /\                                                                                               
                  /  \                                                                                              
            +-----    -----+                                                                                        
            |NULL|    |2   |                                                                                        
            +----+    +----+ 
         *    rl.left == null：左孩子的左孩子为NULL，树节点数最多为6
                       +----+                                                                                                  
                       | 1  |                                                                                                  
                       +----+                                                                                                  
                        /--\                                                                                                   
                      /-    -\                                                                                                 
               +----+          +----+                                                                                          
               |2   |          |3   |                                                                                          
               +----+          +----+                                                                                          
                 /\              /\                                                                                            
                /  \            /  \                                                                                           
          +----+    +----++----+    +----+                                                                                     
          |NULL|    |4   ||5   |    |6   |                                                                                     
          +----+    +----++----+    +----+ 
        */
        if (root == null
            || (movable
                && (root.right == null
                    || (rl = root.left) == null
                    || rl.left == null))) {
            // 链表化
            tab[index] = first.untreeify(map);  // too small
            return;
        }
        TreeNode<K,V> p = this; // 当前节点
        TreeNode<K,V> pl = left; // 左子节点
        TreeNode<K,V> pr = right;  // 右子节点
        TreeNode<K,V> replacement;
        // 如果左右子节点都不为n空
        if (pl != null && pr != null) {

            // 查找右子树的最左节点，即当前节点的后继节点
            TreeNode<K,V> s = pr, sl;
            while ((sl = s.left) != null) // find successor
                s = sl;

            // 与当前节点交换颜色
            boolean c = s.red;
            boolean s.red = p.red;
            boolean p.red = c;

            // 后继节点的右子树（后继节点肯定不存在左子树）
            TreeNode<K,V> sr = s.right;
            // 当前节点的父节点
            TreeNode<K,V> pp = p.parent;

            // 如果右子节点等于后继节点说明当前节点只有一个右子节点
            if (s == pr) {
                // 交换两个节点
                p.parent = s;
                s.right = p;
            }
            // 如果右节点不仅只有一个
            else {
                TreeNode<K,V> sp = s.parent; // 后继节点的父节点
                // 将当前节点的父节点设置为后继节点的父节点
                if ((p.parent = sp) != null) {
                    // 如果后继节点是后继节点父节点的左子节点
                    if (s == sp.left)
                        sp.left = p; // 将后继节点的左节点设置为当前节点
                    else
                        sp.right = p;
                }
                if ((s.right = pr) != null)
                    pr.parent = s;
            }
            p.left = null;
            if ((p.right = sr) != null)
                sr.parent = p;
            if ((s.left = pl) != null)
                pl.parent = s;
            if ((s.parent = pp) == null)
                root = s;
            else if (p == pp.left)
                pp.left = s;
            else
                pp.right = s;
            if (sr != null)
                replacement = sr;
            else
                replacement = p;
        }
        else if (pl != null)
            replacement = pl;
        else if (pr != null)
            replacement = pr;
        else
            replacement = p;
        if (replacement != p) {
            TreeNode<K,V> pp = replacement.parent = p.parent;
            if (pp == null)
                root = replacement;
            else if (p == pp.left)
                pp.left = replacement;
            else
                pp.right = replacement;
            p.left = p.right = p.parent = null;
        }

        TreeNode<K,V> r = p.red ? root : balanceDeletion(root, replacement);

        if (replacement == p) {  // detach
            TreeNode<K,V> pp = p.parent;
            p.parent = null;
            if (pp != null) {
                if (p == pp.left)
                    pp.left = null;
                else if (p == pp.right)
                    pp.right = null;
            }
        }
        if (movable)
            moveRootToFront(tab, r);
    }

        /**
         * Splits nodes in a tree bin into lower and upper tree bins,
         * or untreeifies if now too small. Called only from resize;
         * see above discussion about split bits and indices.
         *
         * @param map the map
         * @param tab the table for recording bin heads
         * @param index the index of the table being split
         * @param bit the bit of hash to split on
         */
        final void split(HashMap<K,V> map, Node<K,V>[] tab, int index, int bit) {
            TreeNode<K,V> b = this;
            // Relink into lo and hi lists, preserving order
            TreeNode<K,V> loHead = null, loTail = null;
            TreeNode<K,V> hiHead = null, hiTail = null;
            int lc = 0, hc = 0;
            for (TreeNode<K,V> e = b, next; e != null; e = next) {
                next = (TreeNode<K,V>)e.next;
                e.next = null;
                if ((e.hash & bit) == 0) {
                    if ((e.prev = loTail) == null)
                        loHead = e;
                    else
                        loTail.next = e;
                    loTail = e;
                    ++lc;
                }
                else {
                    if ((e.prev = hiTail) == null)
                        hiHead = e;
                    else
                        hiTail.next = e;
                    hiTail = e;
                    ++hc;
                }
            }

            if (loHead != null) {
                if (lc <= UNTREEIFY_THRESHOLD)
                    tab[index] = loHead.untreeify(map);
                else {
                    tab[index] = loHead;
                    if (hiHead != null) // (else is already treeified)
                        loHead.treeify(tab);
                }
            }
            if (hiHead != null) {
                if (hc <= UNTREEIFY_THRESHOLD)
                    tab[index + bit] = hiHead.untreeify(map);
                else {
                    tab[index + bit] = hiHead;
                    if (loHead != null)
                        hiHead.treeify(tab);
                }
            }
        }

        /* ------------------------------------------------------------ */
        // Red-black tree methods, all adapted from CLR

        static <K,V> TreeNode<K,V> rotateLeft(TreeNode<K,V> root,
                                              TreeNode<K,V> p) {
            TreeNode<K,V> r, pp, rl;
            if (p != null && (r = p.right) != null) {
                if ((rl = p.right = r.left) != null)
                    rl.parent = p;
                if ((pp = r.parent = p.parent) == null)
                    (root = r).red = false;
                else if (pp.left == p)
                    pp.left = r;
                else
                    pp.right = r;
                r.left = p;
                p.parent = r;
            }
            return root;
        }

        static <K,V> TreeNode<K,V> rotateRight(TreeNode<K,V> root,
                                               TreeNode<K,V> p) {
            TreeNode<K,V> l, pp, lr;
            if (p != null && (l = p.left) != null) {
                if ((lr = p.left = l.right) != null)
                    lr.parent = p;
                if ((pp = l.parent = p.parent) == null)
                    (root = l).red = false;
                else if (pp.right == p)
                    pp.right = l;
                else
                    pp.left = l;
                l.right = p;
                p.parent = l;
            }
            return root;
        }

        static <K,V> TreeNode<K,V> balanceInsertion(TreeNode<K,V> root,
                                                    TreeNode<K,V> x) {
            x.red = true;
            for (TreeNode<K,V> xp, xpp, xppl, xppr;;) {
                if ((xp = x.parent) == null) {
                    x.red = false;
                    return x;
                }
                else if (!xp.red || (xpp = xp.parent) == null)
                    return root;
                if (xp == (xppl = xpp.left)) {
                    if ((xppr = xpp.right) != null && xppr.red) {
                        xppr.red = false;
                        xp.red = false;
                        xpp.red = true;
                        x = xpp;
                    }
                    else {
                        if (x == xp.right) {
                            root = rotateLeft(root, x = xp);
                            xpp = (xp = x.parent) == null ? null : xp.parent;
                        }
                        if (xp != null) {
                            xp.red = false;
                            if (xpp != null) {
                                xpp.red = true;
                                root = rotateRight(root, xpp);
                            }
                        }
                    }
                }
                else {
                    if (xppl != null && xppl.red) {
                        xppl.red = false;
                        xp.red = false;
                        xpp.red = true;
                        x = xpp;
                    }
                    else {
                        if (x == xp.left) {
                            root = rotateRight(root, x = xp);
                            xpp = (xp = x.parent) == null ? null : xp.parent;
                        }
                        if (xp != null) {
                            xp.red = false;
                            if (xpp != null) {
                                xpp.red = true;
                                root = rotateLeft(root, xpp);
                            }
                        }
                    }
                }
            }
        }

        static <K,V> TreeNode<K,V> balanceDeletion(TreeNode<K,V> root,
                                                   TreeNode<K,V> x) {
            for (TreeNode<K,V> xp, xpl, xpr;;) {
                if (x == null || x == root)
                    return root;
                else if ((xp = x.parent) == null) {
                    x.red = false;
                    return x;
                }
                else if (x.red) {
                    x.red = false;
                    return root;
                }
                else if ((xpl = xp.left) == x) {
                    if ((xpr = xp.right) != null && xpr.red) {
                        xpr.red = false;
                        xp.red = true;
                        root = rotateLeft(root, xp);
                        xpr = (xp = x.parent) == null ? null : xp.right;
                    }
                    if (xpr == null)
                        x = xp;
                    else {
                        TreeNode<K,V> sl = xpr.left, sr = xpr.right;
                        if ((sr == null || !sr.red) &&
                            (sl == null || !sl.red)) {
                            xpr.red = true;
                            x = xp;
                        }
                        else {
                            if (sr == null || !sr.red) {
                                if (sl != null)
                                    sl.red = false;
                                xpr.red = true;
                                root = rotateRight(root, xpr);
                                xpr = (xp = x.parent) == null ?
                                    null : xp.right;
                            }
                            if (xpr != null) {
                                xpr.red = (xp == null) ? false : xp.red;
                                if ((sr = xpr.right) != null)
                                    sr.red = false;
                            }
                            if (xp != null) {
                                xp.red = false;
                                root = rotateLeft(root, xp);
                            }
                            x = root;
                        }
                    }
                }
                else { // symmetric
                    if (xpl != null && xpl.red) {
                        xpl.red = false;
                        xp.red = true;
                        root = rotateRight(root, xp);
                        xpl = (xp = x.parent) == null ? null : xp.left;
                    }
                    if (xpl == null)
                        x = xp;
                    else {
                        TreeNode<K,V> sl = xpl.left, sr = xpl.right;
                        if ((sl == null || !sl.red) &&
                            (sr == null || !sr.red)) {
                            xpl.red = true;
                            x = xp;
                        }
                        else {
                            if (sl == null || !sl.red) {
                                if (sr != null)
                                    sr.red = false;
                                xpl.red = true;
                                root = rotateLeft(root, xpl);
                                xpl = (xp = x.parent) == null ?
                                    null : xp.left;
                            }
                            if (xpl != null) {
                                xpl.red = (xp == null) ? false : xp.red;
                                if ((sl = xpl.left) != null)
                                    sl.red = false;
                            }
                            if (xp != null) {
                                xp.red = false;
                                root = rotateRight(root, xp);
                            }
                            x = root;
                        }
                    }
                }
            }
        }

        /**
         * Recursive invariant check
         */
        static <K,V> boolean checkInvariants(TreeNode<K,V> t) {
            TreeNode<K,V> tp = t.parent, tl = t.left, tr = t.right,
                tb = t.prev, tn = (TreeNode<K,V>)t.next;
            if (tb != null && tb.next != t)
                return false;
            if (tn != null && tn.prev != t)
                return false;
            if (tp != null && t != tp.left && t != tp.right)
                return false;
            if (tl != null && (tl.parent != t || tl.hash > t.hash))
                return false;
            if (tr != null && (tr.parent != t || tr.hash < t.hash))
                return false;
            if (t.red && tl != null && tl.red && tr != null && tr.red)
                return false;
            if (tl != null && !checkInvariants(tl))
                return false;
            if (tr != null && !checkInvariants(tr))
                return false;
            return true;
        }
    }
```
