---
title: Actor学习笔记day2-akka框架
date: 2019-02-12 16:49:12
tags: 
	- actor
	- scala
	- akka
categories:
	- actor
---

### 使用akka框架
> 环境 scala sbt
scala是一种运行在jvm平台的一门多范式的编程语言
sbt是简单构建工具(Simple build tool)的缩写，可以从官网获取
akka actor是typesafe(lightbend前身)公司出品的一个Actor框架

创建*akka-demo*文件夹，创建*build.sbt*并添加以下代码
```scala
name := "akka-demo"
version := "0.1"
scalaVersion := "2.12.8"
lazy val akkaVersion = "2.5.20"
libraryDependencies ++= Seq(
	"com.typesafe.akka" %% "akka-actor" % akkaVersion,
	"com.typesafe.akka" %% "akka-testkit" % akkaVersion,
)
```
执行`sbt`命令等待完成
### 编写程序
```scala
package org.inurl.akka

import akka.actor.{Actor, ActorLogging, ActorRef, ActorSystem, Props}

/**
  * @author raylax
  */
class Greeter(message: String, printerActor: ActorRef) extends Actor {
	import Greeter._
	import Printer._

	var greeting = ""

	def receive = {
		// 保存greeting
		case WhoToGreet(who) =>
			greeting = message + ", " + who
		// 向printerActor发送Greeting消息
		case Greet =>
			printerActor ! Greeting(greeting)
	}
}

object Greeter {
	def props(message: String, printerActor: ActorRef): Props = Props(new Greeter(message, printerActor))
	final case class WhoToGreet(who: String)
	case object Greet
}


class Printer extends Actor with ActorLogging {
	import Printer._

	def receive = {
		// 打印greeting
		case Greeting(greeting) =>
			log.info("Greeting received (from " + sender() + "): " + greeting)
	}
}
object Printer {
	def props: Props = Props[Printer]
	final case class Greeting(greeting: String)
}

object ActorDemo extends App {
	import Greeter._

	// 创建Actor系统
	val system: ActorSystem = ActorSystem("helloAkka")
	
	// 创建子Actor对象
	val printer: ActorRef = 
		system.actorOf(Printer.props, "printerActor")
	val howdyGreeter: ActorRef =
		system.actorOf(Greeter.props("Howdy", printer), "howdyGreeter")
	val helloGreeter: ActorRef =
		system.actorOf(Greeter.props("Hello", printer), "helloGreeter")
	val goodDayGreeter: ActorRef =
		system.actorOf(Greeter.props("Good day", printer), "goodDayGreeter")

	// 发送消息
	howdyGreeter ! WhoToGreet("Akka")
	howdyGreeter ! Greet

	howdyGreeter ! WhoToGreet("Lightbend")
	howdyGreeter ! Greet

	helloGreeter ! WhoToGreet("Scala")
	helloGreeter ! Greet

	goodDayGreeter ! WhoToGreet("Play")
	goodDayGreeter ! Greet

}

```
执行程序输出内容
```
[INFO] [02/12/2019 17:03:28.281] [helloAkka-akka.actor.default-dispatcher-5] [akka://helloAkka/user/printerActor] Greeting received (from Actor[akka://helloAkka/user/howdyGreeter#-1189614707]): Howdy, Akka
[INFO] [02/12/2019 17:03:28.293] [helloAkka-akka.actor.default-dispatcher-2] [akka://helloAkka/user/printerActor] Greeting received (from Actor[akka://helloAkka/user/helloGreeter#-140442030]): Hello, Scala
[INFO] [02/12/2019 17:03:28.293] [helloAkka-akka.actor.default-dispatcher-2] [akka://helloAkka/user/printerActor] Greeting received (from Actor[akka://helloAkka/user/howdyGreeter#-1189614707]): Howdy, Lightbend
[INFO] [02/12/2019 17:03:28.297] [helloAkka-akka.actor.default-dispatcher-7] [akka://helloAkka/user/printerActor] Greeting received (from Actor[akka://helloAkka/user/goodDayGreeter#1061792007]): Good day, Play
```