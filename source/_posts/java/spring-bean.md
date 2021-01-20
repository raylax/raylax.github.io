---
title: Spring-bean管理
date: 2019-01-22 18:01:56
tags:
	- java
	- spring
categories:
	- java
---
### 前言
> Spring中所有的bean都由IoC容器管理，IoC容器负责创建/销毁bean，Spring中的IoC容器即**BeanFactory**，**BeanFactory**为一个接口，Srping中所有的**ApplicationContext**都实现了此接口。

### 作用域
Spring中定义了4种bean的作用域以适应不同业务场景

作用域		| 描述
--			| --
singleton	| 单例方式存在，只创建一个实例，每次获取都返回该实例(默认)
prototype	| 每次获取都创建一个新实例
request		| 同一请求下每次获取实例都返回同一个实例(仅限于WebApplicationContext)
session		| 同一会话下每次获取实例都返回同一个实例(仅限于WebApplicationContext)
> 其中后两者是只有在web环境下才生效的，基于**WebApplicationContext**

### 生命周期
- **singleton**
容器时启动创建，随容器关闭而销毁，可以设置*@Lazy*注解使其在第一次获取时创建
- **prototype**
该作用域的实例Spring并不负责管理生命周期
- **request**
随每个请求创建/销毁
- **session**
随每个会话创建/销毁

### 生命周期监控
> Spring管理的bean的生命周期可以使用一系列接口/注解来监控bean的生命周期

#### 实例级监控
- **InitializingBean#afterPropertiesSet**
在bean初始化成功后调用
- **DiposableBean#destroy**
在bean销毁前调用
- **@PostConstruct**
该注解修饰的方法会在bean创建后调用
- **@PreDestroy**
该注解修饰的方法会在bean销毁前调用
> `@PostConstruct`修饰的方法先于`InitializingBean#afterPropertiesSet`执行
`@PreDestroy`修饰的方法先于`DiposableBean#destroy`执行

#### 容器级监控
- **BeanPostProcessor#postProcessBeforeInitialization**
方法会在bean初始化前调用，先于`@PostConstruct|InitializingBean#afterPropertiesSet`执行
- **BeanPostProcessor#postProcessAfterInitialization**
方法会在bean初始化前调用，后于`@PostConstruct|InitializingBean#afterPropertiesSet`执行

### 图片描述
![上面这张图完整描述了bean的生命周期(图片来源于网络)](/img/post/spring-bean-lifecycle.jpeg)



