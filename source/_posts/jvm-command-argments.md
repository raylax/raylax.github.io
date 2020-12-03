---
title: jvm命令行参数
date: 2019-06-05 09:49:03
tags:
	- java
	- jvm
---

### jvm命令行参数

#### 标准参数

> **标准参数**以`-`开头，所有jvm都实现了该参数的功能

- -jar
指定运行一个jar包，jar包中manifest文件中必须指定Main-class
- -cp
指定classpath路径
- -Dproperty=value
设置系统属性键值对，使用`System.getProperty("property")`可以获得`value`
- -verbose
打印jvm载入类的相关信息
- -verbose:gc
打印gc信息
- -verbose:jni
打印native方法调用信息

#### 非标准参数

> **非标准参数**以`-X`开头，默认jvm实现这些参数的功能，但是并不保证所有jvm实现都满足

- -Xms
`-Xms1g` 指定jvm初始内存为1g，避免频繁扩容
- -Xmx
`-Xmx1g` 指定jvm最大可用内存为1g
- -Xmn
`-Xmn1g` 指定年轻代大小为1g，整个堆 = 年轻代 + 年老代 + 持久代，增加年轻代容量会缩小年老代容量
- -Xss
`-Xss1m` 设置线程堆栈大小，默认1m。增加此值会减少可创建的线程数量，反而能增加可创建线程数量。可创建线程数量也受操作系统限制
- -Xloggc
`-Xloggc:gc.log` 将gc日志记录到`gc.log`中
- -Xprof
 跟踪正运行的程序，并将跟踪数据在标准输出输出

#### 非Stable参数

> **非Stable参数**以`-XX`开头

- -XX:PermSize
指非堆内存初始大小
- -XX:MaxPermSize
指对非堆内存上限
- -XX:-UseSerialGC
使用串行GC
- -XX:-UseParallelGC
使用并行GC
- -XX:-UseConcMarkSweepGC
对老年代使用CMS`Concurrent Mark And Sweep` GC

|参数|描述|
|--|--|
|-XX:LargePageSizeInBytes=4m|设置用于Java堆的大页面尺寸|
|-XX:MaxHeapFreeRatio=70|GC后java堆中空闲量占的最大比例|
|-XX:MaxNewSize=size|新生成对象能占用内存的最大值|
|-XX:MaxPermSize=64m|老生代对象能占用内存的最大值|
|-XX:MinHeapFreeRatio=40|GC后java堆中空闲量占的最小比例|
|-XX:NewRatio=2|新生代内存容量与老生代内存容量的比例|
|-XX:NewSize=2.125m|新生代对象生成时占用内存的默认值|
|-XX:ReservedCodeCacheSize=32m|保留代码占用的内存容量|
|-XX:ThreadStackSize=512|设置线程栈大小，若为0则使用系统默认值|
|-XX:+UseLargePages|使用大页面内存|
|-XX:-CITime|打印消耗在JIT编译的时间|
|-XX:ErrorFile=./hs_err_pid<pid>.log|保存错误日志或者数据到文件中|
|-XX:-ExtendedDTraceProbes|开启solaris特有的dtrace探针|
|-XX:HeapDumpPath=./java_pid<pid>.hprof|指定导出堆信息时的路径或文件名|
|-XX:-HeapDumpOnOutOfMemoryError|当首次遭遇OOM时导出此时堆中相关信息|
|-XX:OnError="<cmd args>;<cmd args>"|出现致命ERROR之后运行自定义命令|
|-XX:OnOutOfMemoryError="<cmd args>;<cmd args>"|当首次遭遇OOM时执行自定义命令|
|-XX:-PrintClassHistogram|遇到Ctrl-Break后打印类实例的柱状信息，与jmap -histo功能相同|
|-XX:-PrintConcurrentLocks|遇到Ctrl-Break后打印并发锁的相关信息，与jstack -l功能相同|
|-XX:-PrintCommandLineFlags|打印在命令行中出现过的标记|
|-XX:-PrintCompilation|当一个方法被编译时打印相关信息|
|-XX:-PrintGC|每次GC时打印相关信息|
|-XX:-PrintGC Details|每次GC时打印详细信息|
|-XX:-PrintGCTimeStamps|打印每次GC的时间戳|
|-XX:-TraceClassLoading|跟踪类的加载信息|
|-XX:-TraceClassLoadingPreorder|跟踪被引用到的所有类的加载信息|
|-XX:-TraceClassResolution|跟踪常量池|
|-XX:-TraceClassUnloading|跟踪类的卸载信息|
|-XX:-TraceLoaderConstraints|跟踪类加载器约束的相关信息|
