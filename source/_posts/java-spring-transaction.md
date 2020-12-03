---
title: Spring-事物传播方式/机制
date: 2019-01-20 18:55:03
tags:
	- java
	- spring
categories:
	- java
---
### 概述
Spring在`org.springframework.transaction.TransactionDefinition`中定义了七中事物传播方式，规定了需要执行事物的方法和事物发生嵌套时如何进行传播

| 传播方式   				| 描述 		       	|
| ------------------------- | -----------------	|
| PROPAGATION_REQUIRED 		| 支持当前事务，如果没有事务则创建一个事务 |
| PROPAGATION_SUPPORTS 		| 支持当前事务，如果没有事务则已非事务方式执行 |
| PROPAGATION_MANDATORY 	| 支持当前事务，如果没有事务则抛异常 |
| PROPAGATION_REQUIRES_NEW 	| 创建新事务，如果已存在事务则挂起 |
| PROPAGATION_NOT_SUPPORTED | 不支持当前事务，如果存在则以非事务方式执行 |
| PROPAGATION_NEVER 		| 不支持当前事务，如果存在则抛出异常 |
| PROPAGATION_NESTED 		| 如果当前存在事务则执行嵌套事务，否则以类似PROPAGATION_REQUIRED方式执行 |
### 详解
> 除了`PROPAGATION_REQUIRES_NEW`和`PROPAGATION_NESTED`其他都很好理解，主要解释下这两者的区别
#### PROPAGATION_REQUIRES_NEW
创建一个独立的"内部"事务，挂起原有事务，此事务与原事务互不依赖
```java
// UserServiceAImpl.java
@Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRES_NEW)
@Override
public void addUser(UserEntity user) {
    logger.info("UserServiceAImpl#addUser begin");
    userRepository.save(user);
    userServiceB.updateUser(user);
    logger.info("UserServiceAImpl#addUser complete");
}
// UserServiceBImpl.java
@Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRES_NEW)
@Override
public void updateUser(UserEntity user) {
    logger.info("UserServiceBImpl#updateUser begin");
    userRepository.save(user);
    logger.info("UserServiceBImpl#updateUser complete");
}
// Test.java
UserEntity user = new UserEntity("raylax");
userServiceA.addUser(user);
```
截取部分运行日志
```
# 创建事务
Creating new transaction with name [UserServiceAImpl.addUser]: PROPAGATION_REQUIRED,ISOLATION_DEFAULT
Opened new EntityManager [SessionImpl(254041053<open>)] for JPA transaction
Exposing JPA transaction as JDBC [HibernateConnectionHandle@580902cd]
# 进入addUser方法
UserServiceAImpl#addUser begin
Found thread-bound EntityManager [SessionImpl(254041053<open>)] for JPA transaction
Participating in existing transaction
Found thread-bound EntityManager [SessionImpl(254041053<open>)] for JPA transaction
# 挂起当前事务
Suspending current transaction, creating new transaction with name [UserServiceBImpl.updateUser]
# 创建新事务
Opened new EntityManager [SessionImpl(40626598<open>)] for JPA transaction
Exposing JPA transaction as JDBC [HibernateConnectionHandle@4d518c66]
# 进入updateUser方法
UserServiceBImpl#updateUser begin
Found thread-bound EntityManager [SessionImpl(40626598<open>)] for JPA transaction
Participating in existing transaction
# 退出updateUser方法
UserServiceBImpl#updateUser complete
# 提交新事务
Initiating transaction commit
Committing JPA transaction on EntityManager [SessionImpl(40626598<open>)]
Closing JPA EntityManager [SessionImpl(40626598<open>)] after transaction
# 恢复被挂起的事务
Resuming suspended transaction after completion of inner transaction
# 退出addUser方法
UserServiceAImpl#addUser complete
# 提交原事务
Initiating transaction commit
Committing JPA transaction on EntityManager [SessionImpl(254041053<open>)]
```
#### PROPAGATION_NESTED
如果当前存在事务则执行嵌套事务，否则以类似PROPAGATION_REQUIRED方式执行
嵌套事务创建同时会创建一个`savepoint`如果该事务发生异常会回滚到`savepoint`
嵌套事务会跟随父事务commit/rollback
> NESTED需要基于`JDBC3.0`并且事务支持`savepoint`

```java
// UserServiceAImpl.java
@Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRES_NEW)
@Override
public void addUser(UserEntity user) {
    logger.info("UserServiceAImpl#addUser begin");
    jdbcTemplate.execute("insert into t_user values(1, '"  + user.getName() + "')");
    userServiceB.updateUser(user);
    logger.info("UserServiceAImpl#addUser complete");
}
// UserServiceBImpl.java
@Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRES_NEW)
@Override
public void updateUser(UserEntity user) {
    logger.info("UserServiceBImpl#updateUser begin");
    jdbcTemplate.update("update t_user set name = '" + user.getName() + "-updated'");
    logger.info("UserServiceBImpl#updateUser complete");
}
// Test.java
UserEntity user = new UserEntity("raylax");
userServiceA.addUser(user);

```
截取部分运行日志
```
# 创建事务
Acquired Connection [HikariProxyConnection@183304529 wrapping ConnectionImpl@400d912a] for JDBC transaction
Switching JDBC Connection [HikariProxyConnection@183304529 wrapping ConnectionImpl@400d912a] to manual commit
# 进入addUser方法
UserServiceAImpl#addUser begin
Executing SQL statement [insert into t_user values(1, 'raylax')]
# 创建嵌套事务，创建保存点
Creating nested transaction with name [UserServiceBImpl.updateUser]
# 进入updateUser方法
UserServiceBImpl#updateUser begin
Executing SQL update [update t_user set name = 'raylax-updated' where id = null]
# 退出updateUser方法
UserServiceBImpl#updateUser complete
# 释放保存点
Releasing transaction savepoint
# 退出addUser方法
UserServiceAImpl#addUser complete
# 提交事务，嵌套事务会跟随提交
Initiating transaction commit
Committing JDBC transaction on Connection [HikariProxyConnection@183304529 wrapping ConnectionImpl@400d912a]
Releasing JDBC Connection [HikariProxyConnection@183304529 wrapping ConnectionImpl@400d912a] after transaction
```
### 注意事项
> 事务默认以`PROPAGATION_REQUIRED`方式执行
事务传播的控制基于`AOP`，所以只有调用spring管理的实例方法时生效，调用this指向方法不生效
例如ClassA调用methodA，methodA中调用了ClassB的methodB此时传播控制才生效
如ClassA调用methodA，methodA中调用调用了内部的methodB则会以`PROPAGATION_REQUIRED`方式执行，传播控制不生效
#### 生效示例
```java
// ClassA.java
public void methodA() {
    classB.methodB();
}
// ClassB.java
public void methodB() {

}
// Test.java
classA.methodA();
```
#### 不生效示例
```java
// ClassA.java
public void methodA() {
    methodB();
}
public void methodB() {
    
}
// Test.java
classA.methodA();
```

