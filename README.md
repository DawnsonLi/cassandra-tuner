# cassandra tuner
Cassandra调优系统系统的设计理念为：generate and test（产生与测试）<br> 
在产生阶段，我们可以使用各种优化方法生成新的参数，比如使用模拟退火方法、遗传编程等等。<br> 
在测试阶段，我们使用具体的测试方法对新参数进行验证，依据验证结果的反馈和记录，我们进行新一轮的产生和测试，从而不断的迭代。<br> 
## cassandra参数优化的难点
Cassandra系统参数调优与hadoop和spark系统参数调优有所不同，cassandra系统参数修改要想生效，必须满足两个条件：<br>
(1)	必须修改conf目录下的cassandra.yaml文件，没有其他修改方式。<br>
(2)	每次修改必须重新启动cassandra系统。<br>
因此，cassandra系统参数调优问题的一大难点就在于如何修改参数并使得参数生效。<br>
## 调优系统经常使用的技术包括：<br>
(1)将屏幕日志输出重定向到文件 <br>
(2)对重定向文件内容进行解析 <br>
(3)python文件与.sh脚本的互相调用 <br>
(4)cassandra启动脚本和关闭脚本的灵活使用 <br>

