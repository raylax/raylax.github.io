---
title: JAVA-JDK和CGLIB动态代理使用
date: 2019-01-20 18:50:33
tags:
	- java
categories:
	- java
---
### 代理模式
代理模式即给某一对象生成一个代理对象，来对原对象进行一些访问控制
通过代理模式可以有效的将具体的实现与调用方进行解耦，通过面向接口进行编码完全将具体的实现隐藏在内部
### 应用场景
鉴权、事物、日志、异常处理...
### 静态代理
优点：面向接口编程屏蔽内部实现，如需修改实现类直接修改代理类即可
缺点：每个代理类只能为一个接口服务，需要为每个接口创建代理。实现类与代理类都实现了相同的接口，如增加一个方法所有代理类都需要进行修改，增加了维护的复杂度

```java
interface Person {
    void doAction();
}

class RealPerson implements Person {
    @Override
    public void doAction() {
        System.out.println("do action !");
    }
}

class ProxyPerson implements Person {
    private Person person = new RealPerson();
    @Override
    public void doAction() {
        System.out.println("method start");
        try {
            person.doAction();
            System.out.println("method complete");
        } catch (Exception e) {
            System.out.println("method error");
        }
    }
}

public void call() {
    Person person = new ProxyPerson();
    person.doAction();
}
```
### JDK动态代理
需要用到的类`java.lang.reflect.InvocationHandler`和`java.lang.reflect.Proxy`
`Proxy`为原对象的代理对象
`InvocationHandler#invoke`方法会在代理对象被调用时调用，可以在此处做处理
`Proxy#newProxyInstance`方法的第二个参数必须为接口，所以JDK动态代理只能为实现了接口的类生成代理

```java
interface Person {
    void doAction();
}

class RealPerson implements Person {
    @Override
    public void doAction() {
        System.out.println("do action !");
    }
}

class ProxyClass implements InvocationHandler {
    private Object realObject;
    ProxyClass(Object realObject) {
        this.realObject = realObject;
    }
    public Object newProxy() {
        // 生成代理对象
        return Proxy.newProxyInstance(
                realObject.getClass().getClassLoader(),
                realObject.getClass().getInterfaces(),
                this);
    }
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("method start");
        try {
            // 使用反射调用原对象方法
            Object result = method.invoke(realObject, args);
            System.out.println("method complete");
            return result;
        } catch (Exception e) {
            System.out.println("method error");
            throw e;
        }
    }
}

public void call() {
    Person person = (Person) new ProxyClass(new RealPerson()).newProxy();
    person.doAction();
}
```
### CGLib动态代理
CGLib动态代理底层采用ASM字节码生成框架，使用字节码技术生成代理类，原理是生成目标类的子类。CGLib可以为未实现接口的类生成代理，但无法为`final`类生成代理

```java
class RealPerson {
    public void doAction() {
        System.out.println("do action !");
    }
}

class ProxyClass implements MethodInterceptor {
    public Object newProxy(Class clazz) {
        Enhancer enhancer = new Enhancer();
        enhancer.setSuperclass(clazz);
        enhancer.setCallback(this);
        return enhancer.create();
    }

    @Override
    public Object intercept(Object obj, Method method, Object[] args, MethodProxy proxy) throws Throwable {
        System.out.println("method start");
        try {
            // 调用父类方法
            Object result = proxy.invokeSuper(obj, args);
            System.out.println("method complete");
            return result;
        } catch (Exception e) {
            System.out.println("method error");
            throw e;
        }
    }
}

public void call() {
    RealPerson person = (RealPerson) new ProxyClass().newProxy(RealPerson.class);
    person.doAction();
}
```

