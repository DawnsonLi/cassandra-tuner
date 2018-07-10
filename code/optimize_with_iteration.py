# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import os
import random
import json
'''
功能：使用优化方法在空间中搜索最优参数
'''

'''
类名：sample
功能：读取参数配置文件config.json并进行解析
'''
class sample:
    def __init__(self,config_json):
        json_data = open(config_json)
        data = json.load(json_data)
        self.confjson = data["sample_standard_list"]
    '''
    功能：产生参数列表，但是不包含输入数据和NlogN
    '''
    def sampleconf(self):
        x_sample = []
        for conf in self.confjson:
            if conf['type'] == 'int':
                x = float(random.randrange(int(conf['low-bound']),int(conf['high-bound']),int(conf['interval'])))
                x_sample.append(x)
            elif conf['type'] == 'float':
                f_temp = float(conf['high-bound'])-float(conf['low-bound'])
                x = float(conf['high-bound']) + random.randint(0,int(f_temp / float(conf['interval'])))*float(conf['interval'])
                x_sample.append(x)
        return x_sample   
    '''
    功能：返回json文件中i号参数的步长
    '''
    def getstep(self,i):
        j = 0
        for conf in self.confjson:
            if j == i:
                return float(conf['interval'])
            j+=1
        return -1
    '''
    功能：返回json文件中i号参数的高边界值
    '''
    def get_high_bound(self,i):
        j = 0
        for conf in self.confjson:
            if j == i:
                return float(conf['high-bound'])
            j+=1
        return -1
    '''
    功能：返回json文件中i号参数的低边界值
    '''
    def get_low_bound(self,i):
        j = 0
        for conf in self.confjson:
            if j == i:
                return float(conf['low-bound'])
            j+=1
        return -1
    '''
    功能：返回配置的总数
    '''
    def getnum_of_conf(self):
        j = 0
        for conf in self.confjson:
            j += 1
        return j

def process_line(word ,value):
    '''
    1. 根据行特点进行创建字符串，比如形如“XXX = 12345”
    2. 进行字符串拼接
    '''
    value = int(value)#转化为整数
    line = word + ' : '+ str(value) + '\n'
    return line
def rewrite(file_name, keywords, conf):
    '''
    1. 新建拷贝文件
    2. 逐行读入，查表
    （1）若存在关键字，进行字符串修改
    （2）若不存在，直接写入新拷贝文件
    '''
    with open(file_name ,"r") as f:
        lines = f.readlines()  
    with open(file_name ,"w") as f_w:
        for line in lines:
            if "#" not in line:#如果包含注释项，直接略过

                for i in range(len(keywords)):
                    word = keywords[i]
                    if word in line:
                        line = process_line(word, conf[i])#传入需要修改的值
                        break
                     
            f_w.write(line)
   
import re
def get_lantency():
    with open('./stress.log' ,"r") as f_w:
        for line in f_w:
            if "latency mean" in line:#找到lantency并提取出时间
                result = re.findall('\d+\.\d+', line)# 查找数字
                if len(result)> 0:
                    return  float(result[0])
                return 9999999 #big int
import time
def restart_test():
    '''
    调用脚本重启cassandra
    重新进行任务测验
    '''
    os.system('./stop.sh')
    print 'INFO:restart cassandra to make parameters settings effective********************************'
    time.sleep(60)
    print 'INFO:restart and sleep waking up********************************'
    os.system('./restart.sh')#调用重启脚本
     
    
    
def generate_test(file_name, conf):
    '''
    1. 修改配置文件：
    （1）找到配置文件关键字
    （2）修改
    2. 重启集群
    3. 重新运行任务
    '''
    #关键词列表，需要与配置项一一对应
    keywords = ['concurrent_reads', 'concurrent_writes']
    rewrite(file_name, keywords, conf)
    print 'INFO: parameters are updated in file: cassandra.yaml'
    restart_test()
    return get_lantency()
    
'''
模拟退火优化算法
参数名称：config_json:配置参数,T为温度，cool为降低温度的比例(幅度)
'''
import  math


def optimizer(config_json, T, cool, file_name, iter_num):
  
    s = sample(config_json)
    vec = s.sampleconf()#取一组配置参数
    parameters_lst = []
    time_lst = []
    print "testing parameters:", vec, " ******************************"
    ea = generate_test(file_name, vec)
    parameters_lst.append(vec)
    time_lst.append(ea)

    conflen = s.getnum_of_conf()#获取配置参数的总数
    counter = 0

    while T > 0.1 and counter < iter_num:
        counter += 1
        while True:

            i = random.randint(0, conflen - 1)  # 随机选择一个参数进行值的修改
            step = s.getstep(i)  # 获取选定参数的步长
            dis = random.randint(-1, 1) * step  # 移动的距离
            vecb = []
            for tmp in vec:
                vecb.append(tmp)
            vecb[i] += dis#将指定位置的参数进行修改
            if vecb[i] < s.get_low_bound(i):
                vecb[i] = s.get_low_bound(i)
                #print i,':out of index of low'
            elif vecb[i] > s.get_high_bound(i):
                vecb[i] = s.get_high_bound(i)
            #print i, ':out of index of high'
            flag = 1
            for para in parameters_lst:
                if para == vecb:
                    flag = 0
                    break
            if flag:
                break
        print "testing parameters:", vecb, " ******************************"
        eb = generate_test(file_name, vecb)
        parameters_lst.append((vecb))
        print parameters_lst
        time_lst.append(eb)
        if (eb<ea or random.random()<pow(math.e,-(eb-ea)/T)):
            vec = vecb[:]
        T = T*cool
    if T <= 0.1:
        return  vec
    print time_lst
    print parameters_lst
    min_pos = time_lst.index(min(time_lst))
    return  parameters_lst[min_pos]


filename = '/usr/local/cassandra/conf/cassandra.yaml'
conf = optimizer('./config.json', 100000.0, 0.95, filename, 3)
