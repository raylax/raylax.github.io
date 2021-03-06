---
title: MySQL-事务隔离级别
date: 2019-01-21 14:18:25
tags: 
	- mysql
categories:
	- database
---
### 事务ACID特性
- **原子性(Atomicity)**
一个事物内的所有操作视为一个不可分割的操作，事务内所有操要么全执行成功要么全失败
例如：一个事务内A给B转账，先从A账户中扣钱，然后向B账户中加对应的钱数，这两次数据库操作要么全成功要么全失败，不能某个操作成功了，其他的失败了
- **一致性(Consistency)**
一个事务可以封装状态改变（除非它是一个只读的）。事务必须始终保持系统处于一致的状态，不管在任何给定的时间并发事务有多少(摘自百度)
例如：一共有2个账户，这些账户的总余额为100，无论如何进行并发操作最终这2个账户的余额的和必须为100
- **隔离性(Isolation)**
隔离状态执行事务，使它们好像是系统在给定时间内执行的唯一操作
- **持久性(Durability)**
在事务完成以后，该事务对数据库所作的更改便持久的保存在数据库之中，并不会被回滚

### 事务隔离级别
> **完全隔离**是不现实的，因为完全隔离会使事务串行化，严重影响并发性能，所以引入隔离级别来控制并发访问

MySQl支持4中隔离级别

隔离级别						| 描述 					
--							| --
读未提交(read uncommitted)	| 一个事务可以读其他事务未提交的数据
读已提交(read committed)		| 一个事务只能读其他事务已提交的数据
可重复读(repeatable read)	| 一个事务内多次读同一数据必须一致(MySQL默认隔离级别)
串行化(serializable) 		| 事务串行化，同一个表同时只能有一个事务进行操作

### 并发引发问题
- **脏读**
A事务读取了B事务未提交的数据并在此基础上进行操作，结果B事务回滚了，那么A所进行的操作就是有问题的
- **不可重复读**
不可重复读指同一事务中两次读取的数据不一致，A事务读取了一条数据，B事务修改了数据并且提交了，A事务又读了此条数据结果与上一读取的数据不一致
- **幻读**
事务A统计了数据量，事务B添加了N条记录，事务B又查了一次，结果两次结果数量不一致

### 隔离级别对应问题
> 隔离级别越往下并发效率越低，**可重复读**行级锁，**串行化**表级锁

级别\问题					| 脏读	| 不可重复读	| 幻读					
--							| :--:	| :--:		| :--:
读未提交(read uncommitted)	| x		| x			| x
读已提交(read committed)		| √		| x			| x
可重复读(repeatable read)	| √		| √			| x
串行化(serializable) 		| √		| √			| √
### 总结
只有`InnoDB`引擎支持事务并且支持行级锁，`MyISAM`引擎并不支持事务且仅支持表级锁
`InnoDB`适合频繁update业务场景(交易系统)，`MyISAM`适用于大量select、insert业务场景(日志类系统)
处理数据库并发问题并非只能依靠数据来处理，可以结合代码进行合理的加锁，例如依靠外部`redis/zookeeper`做分布式锁



