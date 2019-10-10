# -*- coding:utf-8 -*-
import math
import random
import matplotlib.pyplot as plt
import json
import os

# from fairness import Fairness #计算公平性指数的函数，第一个目标函数


class UserEqu:
    Count = 0
    def __init__(self, name, ip, link_e, gains, F_BS, F_UE, N1, b):
        self.name = name
        self.ip = ip 
        self.link_e = link_e
        self.gains = gains
        self.F_BS = F_BS
        self.F_UE = F_UE
        self.N1 = N1
        self.b = b
        self.rank = 0
        UserEqu.Count += 1
#中继设备初始化
UE1 = UserEqu('UE1', '10.0.0.1', 0.10, 0.1, 195.43396778377053 , 78.65153714963657, 28, 5.808983469629878)
UE2 = UserEqu('UE2', '10.0.0.2', 0.15, 0.1, 225.13105279816864 , 100.58333991774799, 26, 6.868589996836461)
UE3 = UserEqu('UE3', '10.0.0.3', 0.20, 0.1, 247.54588421179346, 114.93967520628291, 24, 7.789153133595121)
UE4 = UserEqu('UE4', '10.0.0.4', 0.25, 0.1, 263.82627716639126, 125.27621813097173, 22, 8.694373551407805)
UE5 = UserEqu('UE5', '10.0.0.5', 0.30, 0.1, 281.2885847713523, 133.2092290621777, 21, 9.343296622008463)
UE6 = UserEqu('UE6', '10.0.0.6', 0.35, 0.1, 295.65261736458785, 139.53538286618212, 20, 9.976769143309106)
UE7 = UserEqu('UE7', '10.0.0.7', 0.40, 0.1, 307.3441330874717, 144.74137184593536, 19, 10.617966939259755)
UE8 = UserEqu('UE8', '10.0.0.8', 0.45, 0.1, 316.6832853264184, 149.12205673189075, 18, 11.284558707327264)
UE9 = UserEqu('UE9', '10.0.0.9', 0.50, 0.1, 323.907429967555, 152.86335767704668, 17, 11.991962216296864)

UE10 = UserEqu('UE10', '10.0.0.10', 0.52, 0.1, 329.8844332053065, 154.24242304735702, 17, 12.07308370866806)
UE11 = UserEqu('UE11', '10.0.0.11', 0.54, 0.1, 335.7181156256853 , 155.5376096652692, 17, 12.149271156780541)
UE12 = UserEqu('UE12', '10.0.0.12', 0.56, 0.1, 341.41466557149556 , 156.7563442953185, 17, 12.220961429136382)
UE13 = UserEqu('UE13', '10.0.0.13', 0.58, 0.1, 346.97993469709525, 157.90520206630933, 17, 12.288541298018195)
UE14 = UserEqu('UE14', '10.0.0.14', 0.60, 0.1, 342.7357413827916, 159.03272265564206, 16, 12.939545165977629)
UE15 = UserEqu('UE15', '10.0.0.15', 0.62, 0.1, 347.94883457954006, 160.1011383304499, 16, 13.00632114565312)
UE16 = UserEqu('UE16', '10.0.0.16', 0.64, 0.1, 353.05137533349597, 161.11368913337236, 16, 13.069605570835773)
UE17 = UserEqu('UE17', '10.0.0.17', 0.66, 0.1, 358.0476844677814, 162.074644990923, 16, 13.129665311932687)
UE18 = UserEqu('UE18', '10.0.0.18', 0.68, 0.1, 352.41945368621595, 162.99002514186787, 15, 13.866001676124526)
UE19 = UserEqu('UE19', '10.0.0.19', 0.70, 0.1, 357.1187768684793, 163.89821349547668, 15, 13.926547566365112)
UE20 = UserEqu('UE20', '10.0.0.20', 0.72, 0.1, 361.72767429801195, 164.76383052001006, 15, 13.984255368000671)

UES = [UE1,UE2,UE3,UE4,UE5,UE6,UE7,UE8,UE9,UE10,UE11,UE12,UE13,UE14,UE15,UE16,UE17,UE18,UE19,UE20]

def Fairness(x): #x表示的是传入设备的编号，也即染色体
    #传入的x是浮点数，要转化成整数
    # x = round(x)
    U_total = 0
    U_link_s = 0     
    for i in range(0,len(UES)):
        U_total += UES[i].gains
        U_link_s += (1-UES[i].link_e)
    #加上采用第i个中继设备时的收益来计算fairness
    U_total += UES[x].F_UE
    X=[]
    for i in range(0,len(UES)):
        Ui_overline = ((1-UES[i].link_e)/U_link_s)*U_total
        if UES[i].name == UES[x].name:
            if (UES[i].gains+UES[x].F_UE)<=Ui_overline:
                X.append(UES[i].gains/Ui_overline)
            else:
                X.append(1.0)
        elif UES[i].gains<=Ui_overline:
            X.append(UES[i].gains/Ui_overline)
        else:
            X.append(1.0)
    sum_of_xi = 0
    for i in range(0,len(X)):
        sum_of_xi += X[i]

    sum_of_xi2 = 0
    for i in range(0,len(X)):
        sum_of_xi2 += X[i]**2

    fairness = (sum_of_xi)**2/(len(X)*sum_of_xi2)
    UES[x].fairness = fairness
    return fairness
#第二个目标函数，传输参数为序号
def Utility(x):
    # x= round(x)
    value = UES[x].F_BS
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
        values[index_of(min(values),values)] = math.inf
    return sorted_list
#NSGA-II's fast non dominated sort,基于帕雷托最优解来计算支配解集
'''
输入：目标1数组，目标2数组

输出：前沿面数组，每一个前沿面中包含的是设备序号

'''
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
    #删除
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
        distance[k] = distance[k]+ (values1[sorted1[k+1]] - values1[sorted1[k-1]])/(max(values1)-min(values1)) #统一标准化
    for k in range(1,len(front)-1):
        distance[k] = distance[k]+ (values2[sorted2[k+1]] - values2[sorted2[k-1]])/(max(values2)-min(values2))
    return distance

#交叉
def crossover(a,b):
    r=random.random()
    if r>0.5:
        return mutation((a+b)/2)
    else:
        return mutation((a-b)/2)

#突变
def mutation(solution):
    mutation_prob = random.random()
    if mutation_prob <1:
        solution = min_x+(max_x-min_x)*random.random()
    return solution

'''
排序函数,供考虑fairness时调用
输入：已知博弈信息后的设备池UES(已经按照基站的收益进行了排序)
计算：采用各个解能够达到的两个目标的大小来对各个中继设备来进行排序
输出:已经更新了Rank值的设备池UES

'''
def RankByNSGA(UES):

    #只用求出所有中继设备的rank值不需要进行遗传求出最优解
    obj1 = [Utility(i) for i in range(0,len(UES))]
    obj2 = [Fairness(i) for i in range(0,len(UES))]
    front = fast_non_dominated_sort(obj1[:],obj2[:])
    # print(front)
    for i in range(0,len(front)):
        for j in range(0,len(front[i])):
            UES[front[i][j]].rank = i
    # for i in range(0,len(UES)):
    #     print(UES[i].rank)        
    return UES

if __name__=='__main__':
    
    RankByNSGA(UES)
