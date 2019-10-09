# -*- coding:utf-8 -*-
import math
import random
import matplotlib.pyplot as plt
import json
import os

from fairness import Fairness #计算公平性指数的函数

def Utility(x):
    x= round(x)
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
def fast_non_dominated_sort(values1, values2):
    S=[[] for i in range(0,len(values1))]
    front = [[]]
    n=[0 for i in range(0,len(values1))]
    rank = [0 for i in range(0, len(values1))]
    #先计算出第一次的前沿面
    for p in range(0,len(values1)):
        S[p]=[] #p的支配集合
        n[p]=0  #p的支配个数
        for q in range(0, len(values1)):
            if (values1[p] > values1[q] and values2[p] > values2[q]) or (values1[p] >= values1[q] and values2[p] > values2[q]) or (values1[p] > values1[q] and values2[p] >= values2[q]):
                if q not in S[p]:
                    S[p].append(q)
            elif (values1[q] > values1[p] and values2[q] > values2[p]) or (values1[q] >= values1[p] and values2[q] > values2[p]) or (values1[q] > values1[p] and values2[q] >= values2[p]):
                n[p] = n[p] + 1
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

if __name__=='__main__':
    pop_size = 20
    max_gen = 100
    #初始化
    min_x = 0
    max_x = 19
    cicle = 1
    rand_fair = [0]
    result_fair = [0]
    result_UBS = [] #最终保存 BS效益的数组
    result_URD = [] #最终保存的设备
    result_NRD = []
    while cicle <20:
    #random.random()产生一个(0,1)的随机数,此处在X范围内随机产生一个数
        solution=[min_x+(max_x-min_x)*random.random() for i in range(0,pop_size)] #产生从0到20设备编号解
        gen_no=0
        result=[]
        while(gen_no<max_gen):
            fairness_values = [Fairness(solution[i])for i in range(0,pop_size)]
            utility_values = [Utility(solution[i])for i in range(0,pop_size)]
            non_dominated_sorted_solution = fast_non_dominated_sort(fairness_values[:],utility_values[:])#快速非支配排序返回的front的集合
            print("第",gen_no, "次繁衍的帕累托最优的设备编号为")
            #保存最后一轮的结果
            result = solution
            for valuez in non_dominated_sorted_solution[0]:
                print(round(solution[valuez],3),end=" ")
            print("\n")
            crowding_distance_values=[]
            for i in range(0,len(non_dominated_sorted_solution)):
                crowding_distance_values.append(crowding_distance(fairness_values[:], utility_values[:], non_dominated_sorted_solution[i][:]))
            solution2 = solution[:]
            #产生子代
            while(len(solution2)!=2*pop_size): #新一代种群数量是原种群数量的两倍
                a1 = random.randint(0,pop_size-1) #从种群中随机选择两个个体
                b1 = random.randint(0,pop_size-1)
                solution2.append(crossover(solution[a1],solution[b1]))#从原始的两个个体中交叉产生新的个体
            fairness_values2 = [Fairness(solution2[i])for i in range(0,2*pop_size)]
            utility_values2 = [Utility(solution2[i])for i in range(0,2*pop_size)]
            non_dominated_sorted_solution2 = fast_non_dominated_sort(fairness_values2[:],utility_values2[:])
            crowding_distance_values2=[]
            for i in range(0,len(non_dominated_sorted_solution2)):
                crowding_distance_values2.append(crowding_distance(fairness_values2[:],utility_values2[:],non_dominated_sorted_solution2[i][:]))
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
            solution = [solution2[i] for i in new_solution] 
            gen_no = gen_no + 1
        #图示显示每一轮的帕累托前沿面
        fairness = [i  for i in fairness_values]
        utility = [j  for j in utility_values]
        # plt.xlabel('Fairness', fontsize=15)
        # plt.ylabel('F_BS', fontsize=15)
        # plt.scatter(fairness, utility)
        # plt.show()
        #在显示完plot之后，从前沿面中选择出一个点作为解，更新其gains值
        # print(result)
        #version1先从中选取
        IntResult = []
        for i in range(0,len(result)-1):
            IntResult.append(int(round(result[i],0)))
        #从前沿面中随机选择一个点更新其，gains
        k = random.randint(0,len(IntResult)-1)
        # print(len(result))
        print("k:",k)
        print("NO.",IntResult[k])

        #随机选取设备时的fairness
        #numpy中的random模块和random中的random的范围不同，这里也包含右边界
        num = random.randint(0,19)
        UES2[num].gains += UES2[num].F_UE
        rand_fair.append(Fairness(num))
        #采用博弈策略后的fairness
        UES[IntResult[k]].gains += UES[IntResult[k]].F_UE
        # UBS += UES[IntResult[k]].F_BS
        result_fair.append(Fairness(IntResult[k]))
        result_NRD.append(IntResult[k])
        result_UBS.append(UES[IntResult[k]].F_BS)
        result_URD.append(UES[IntResult[k]].F_UE)
        # print(IntResult)
        # os.system("pause")
        cicle += 1
        # append the result to the graph
    # 绘制fairness图
    plt.xlabel('round',fontsize = 15)
    plt.xlim(0,20)
    plt.ylim(0,1)
    plt.ylabel('fairness',fontsize = 15)
    cicle = [i for i in range(0,20)]

    # game_fair = [0, 0.05, 0.1, 0.15, 0.15, 0.2, 0.2, 0.25, 0.3, 0.35, 0.4, 0.4, 0.45, 0.45,
                #   0.49999725808766626, 0.5490915372696149, 0.5494345676331145, 0.5986329518439101, 0.6434627526049957, 0.6822118090289238]
    plt.plot(cicle,result_fair,marker = '*',color = 'black',label='MOO')
    plt.plot(cicle,game_fair,marker = 'o',linestyle=':',color = 'black',label='Game-only')
    # #绘制BS和UD的效用图
    # plt.xlabel('round ',fontsize=15)
    # plt.xlim(0,20)
    # plt.ylabel('U_BS/U_RD',fontsize=15)
    # cicle = [i for i in range(1,20)]
    # print(result_NRD)
    # print(cicle)
    # print(result_fair)
    # plt.plot(cicle, result_UBS, marker='o', label="$U_BS$")
    # plt.plot(cicle, result_URD, marker='*', label="$U_RD$")
    # for i in range(0,19):
    #     plt.annotate(result_NRD[i], (cicle[i], result_UBS[i]))
    #     plt.annotate(result_NRD[i], (cicle[i], result_URD[i]))
    labelx = range(0,21)
    plt.xticks(cicle,labelx)
    plt.grid()
    plt.legend()
    plt.show()
