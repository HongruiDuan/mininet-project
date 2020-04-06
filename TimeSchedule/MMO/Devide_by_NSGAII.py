# -*- coding:utf-8 -*-
import math
import random
import matplotlib.pyplot as plt
import json
import os



from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
from EH.energy import energy
from Params.params import getDistance
import numpy as np
np.set_printoptions(suppress=True)
import thread
import threading
import time



class UE:
    count = 0
    def __init__(self, host, name, ip, port, link_e, gains=0.0, F_BS=0.0, F_UE=0.0, N1=0.0, b=0.0, Power = 0, rank=0, flag=False):
        self.host = host
        self.name = name
        self.ip = ip
        self.port = port
        self.link_e = link_e
        self.Power = random.uniform(0.003, 0.005)
        self.gains = 0
        UE.count += 1



'''
UES(cus):表示当前cell中所有的设备
queue:候选满足传输能量的设备池
'''
def Fairness(UES,s,x): 
    #传入的x是浮点数，要转化成整数
    U_total = 0
    U_link_s = 0  

    relay_num=0
    value=0.0
    
    for i in range(0,len(x)):
        relay_num += x[i]
    norelay_num = len(UES) - relay_num

    gains=[]
    for i in range(0,len(UES)):
        gains.append(UES[i].gains)
        U_link_s += (1-UES[i].link_e)
    #遍历FD
    for i in range(0,len(gains)):
        if x[i] == 1:
            if(relay_num==0):
                gains[i] += 0
            else:
                gains[i] += s[0]/relay_num
        else:
            if(norelay_num==0):
                gains[i] += 0
            else:
                gains[i] += s[1]/norelay_num
        U_total += gains[i]
        
    
    
    X=[]
    for i in range(0,len(UES)):
        Ui_overline = ((1-UES[i].link_e)/U_link_s)*U_total
        if gains[i]<=Ui_overline:
            X.append(gains[i]/Ui_overline)
        else:
            X.append(1.0)
    sum_of_xi = 0
    for i in range(0,len(X)):
        sum_of_xi += X[i]

    sum_of_xi2 = 0
    for i in range(0,len(X)):
        sum_of_xi2 += X[i]**2

    fairness = (sum_of_xi)**2/(len(X)*sum_of_xi2)
    # UES[x].fairness = fairness
    return fairness
#第二个目标函数为整个FogCell的效用
'''
传入一个[],然后计算整个cell的总效用
x是染色体
'''
def Utility(cus,s,RU,cellnum,x):
    #先统计出染色体中 中继设备个数，不中继设备个数
    relay_num=0
    value=0.0
    gains=[]
    for i in range(0,len(cus)):
        gains.append(cus[i].gains)
    for i in range(0,len(x)):
        relay_num += x[i]
    norelay_num = len(gains) - relay_num
    #遍历FD
    for i in range(0,len(gains)):
        if x[i] == 1:
            if(relay_num==0):
                gains[i] += 0
            else:
                gains[i] += s[0]/relay_num
        else:
            if(norelay_num==0):
                gains[i] += 0
            else:
                gains[i] += s[1]/norelay_num
        value += gains[i]
    
    value += RU[cellnum].gains 
    return value

def index_of(a,list):
    for i in range(0,len(list)):
        if list[i] == a:
            return i
    return -1
#按照function的值来排序
#list1的含义
def sort_by_values(list1, values):
    sorted_list = []
    while(len(sorted_list)!=len(list1)):
        if index_of(min(values),values) in list1: #values中最小值的下标
            sorted_list.append(index_of(min(values),values))
        values[index_of(min(values),values)] = float('inf')
    return sorted_list
#NSGA-II's fast non dominated sort,基于帕雷托最优解来计算支配解集
'''
输入：目标1数组，目标2数组

输出：前沿面数组，每一个前沿面中包含的是各个不同的划分解
    [[1,0,1,0,1,0,1],[0,1,0,1,0,1,0,1],[1,0,0,1,0,1,1,0]]

'''
# def NewCRG(s,g,n,depth): 输入应该有餐桌大小、顾客的序号
def fast_non_dominated_sort(values1, values2):
    S=[[] for i in range(0,len(values1))]
    front = [[]]
    n=[0 for i in range(0,len(values1))]
    rank = [0 for i in range(0, len(values1))]
    #对于目标1中的每一个解，计算其支配解集和支配解的个数
    for p in range(0,len(values1)):
        S[p]=[] #p的支配集合
        n[p]=0  #p的支配个数
        for q in range(0, len(values1)):
            #第p个设备的第一个目标大于q
            if  (values1[p] >= values1[q] and values2[p] > values2[q]) or (values1[p] > values1[q] and values2[p] >= values2[q]):
                if q not in S[p]:
                    S[p].append(q)
            #如果一个解被其他解所支配，那么其被支配数+1
            elif (values1[q] >= values1[p] and values2[q] > values2[p]) or (values1[q] > values1[p] and values2[q] >= values2[p]):
                n[p] = n[p] + 1
        #如果一个解的被支配数为0
        if n[p]==0:
            rank[p] = 0
            if p not in front[0]:
                front[0].append(p)
    i = 0
    while(front[i] != []):
        Q=[]
        for p in front[i]:
            for q in S[p]:
                n[q] = n[q] - 1
                if( n[q]==0 ):
                    rank[q]=i+1
                    if q not in Q:
                        Q.append(q)
        i = i+1
        front.append(Q)
    del front[len(front)-1]
    return front
#采用解的距离有问题，不采用归一化两个目标之间距离差值太大，采用标准化，不能从初始值0开始
def crowding_distance(values1, values2, front):
    distance = [0 for i in range(0,len(front))]
    sorted1 = sort_by_values(front, values1[:])
    sorted2 = sort_by_values(front, values2[:])
    distance[0] = 4444444444444444
    distance[len(front) - 1] = 4444444444444444
    #距离计算公式，换种定义
    for k in range(1,len(front)-1):
        if max(values1) == min(values1):
            maxdis = 1
        else:
            maxdis = max(values1)-min(values1)
        distance[k] = distance[k]+ (values1[sorted1[k+1]] - values1[sorted1[k-1]])/maxdis #统一标准化
    for k in range(1,len(front)-1):
        if max(values2) == min(values2):
            maxdis = 1
        else:
            maxdis = max(values2)-min(values2)
        distance[k] = distance[k]+ (values2[sorted2[k+1]] - values2[sorted2[k-1]])/maxdis
    return distance

#交叉,交换两个染色体的前半部分或者后半部分
#这里传入的是solution[1],solution[2]
def crossover(a,b):
    index=int(len(a)/2.0)
    r=random.random()
    if r>0.5:
        for i in range(0,index):
            a[i],b[i] = b[i],a[i]
        # mutation(a)
        # mutation(b)
    else:
        for i in range(index,len(a)):
            a[i],b[i] = b[i],a[i]
        # mutation(a)
        # mutation(b)
    return a

#突变，每一位都有一定概率重新变成0或者1
def mutation(x):
    for i in range(0,len(x)):
        x[i]=random.randint(0,1)
    return x

'''
划分，在FD中找到一个划分，使得两个目标都能够取得一个较优的值

染色体设计 应该与解是一样的[1,0,1,0,1,1,1] 一个n维的数组
为了与CRG的返回结果保持一致，需要变成[[1,3,5],[2,4,6]]中继和非中继

输入：cus是FD的对象序列，s是各个餐桌大小，RU是所有的客户端设备序列，cellnum是RU编号
计算：
输出:[[1,3,5],[2,4,6]]
'''
def devide(cus,s,RU,cellnum):
    '''
    在求解帕累托前沿面之前,将能量不充足的设备从解集中删除掉
    计算fairness的时候需要考虑的是所有设备的效益
    但是求解时不考虑
    '''
    pop_size = 20 #种群数量
    max_gen = 15 #最大的遗传次数
    gen_len=len(cus)#染色体长度
    #初始化染色体
    solution = []      
    for i in range(0,pop_size):
        #随机产生0(不中继)和1(中继)加入到染色体中
        temp = [random.randint(0,1) for i in range(0,gen_len)]
        solution.append(temp)

    gen_no=0
    result=[]
    while(gen_no<max_gen):
        #分别计算每个解得到的两个效用
        #Fairness函数原型
        fairness_values = [Fairness(cus,s,solution[i]) for i in range(0,pop_size)]
        #Utility函数原型 def Utility(cus,s,RU,cellnum,x):
        utility_values = [Utility(cus,s,RU,cellnum,solution[i]) for i in range(0,pop_size)]
        
        # print(fairness_values)
        # print(utility_values)
        non_dominated_sorted_solution = fast_non_dominated_sort(utility_values[:],fairness_values[:])#快速非支配排序返回的front的集合
        # print("第",gen_no, "次繁衍的帕累托最优的设备编号为")
            
        # for valuez in non_dominated_sorted_solution[0]:
            # print(round(solution[valuez],3),end=" ")
        # print("\n")
        crowding_distance_values=[]
        for i in range(0,len(non_dominated_sorted_solution)):
            crowding_distance_values.append(crowding_distance(utility_values[:],fairness_values[:],non_dominated_sorted_solution[i][:]))
        
        #产生子代
        solution2 = solution[:]
        while(len(solution2)!=2*pop_size): #新一代种群数量是原种群数量的两倍
            a1 = random.randint(0,pop_size-1) #从种群中随机选择两个个体
            b1 = random.randint(0,pop_size-1)
            solution2.append(crossover(solution[a1],solution[b1]))
        #从原始的两个个体中交叉产生新的个体
        fairness_values2 = [Fairness(cus,s,solution2[i]) for i in range(0,2*pop_size)]
        utility_values2 = [Utility(cus,s,RU,cellnum,solution2[i])for i in range(0,2*pop_size)]
        non_dominated_sorted_solution2 = fast_non_dominated_sort(utility_values2[:],fairness_values2[:])
        crowding_distance_values2=[]
        for i in range(0,len(non_dominated_sorted_solution2)):
            crowding_distance_values2.append(crowding_distance(utility_values2[:],fairness_values2[:],non_dominated_sorted_solution2[i][:]))
        new_solution= []
        for i in range(0,len(non_dominated_sorted_solution2)):
            non_dominated_sorted_solution2_1 = [index_of(non_dominated_sorted_solution2[i][j],non_dominated_sorted_solution2[i]) for j in range(0,len(non_dominated_sorted_solution2[i]))]
            front22 = sort_by_values(non_dominated_sorted_solution2_1[:], crowding_distance_values2[i][:])
            front = [non_dominated_sorted_solution2[i][front22[j]] for j in range(0,len(non_dominated_sorted_solution2[i]))]
            front.reverse()
            for value in front:
                new_solution.append(value)
                if(len(new_solution) == pop_size):
                    break
            if (len(new_solution) == pop_size):
                break
        solution = [solution2[i] for i in new_solution] # 最中求解出来的solution
        print "-------------------------"
        for i in range(0,len(solution)):
            print solution[i]           
        result = solution 
        gen_no = gen_no + 1   
    
    #前沿面中随机选择一个解
    k = random.randint(0,len(result)-1)
    relay=[]
    norelay=[]
    for i in range(0,len(result[k])):
        if result[k][i]==1:
            relay.append(cus[i].num)
        else:
            norelay.append(cus[i].num)
    print [relay,norelay]
    return [relay,norelay]


if __name__=='__main__':
    pass