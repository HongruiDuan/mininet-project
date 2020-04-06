# -*- coding:utf-8 -*-
'''
    博弈递归函数参数
    @param:s 各个餐桌大小
    @param:g 各个餐桌人数
    @param:n 顾客序号数组
    上一版本中每次递归到最后一个顾客做出选择，其时间复杂度太大
    加入递归深度与预测精度的比较，当预测深度达到一定值的时候，其预测精度不会有太大的提升
'''
import copy
import matplotlib.pyplot as plt

#直接作出选择的
def group(s, g, n):
    if(len(n)==0): 
        return g
    max=0.0
    index=0
    for i in range(0,len(s)):
        utility=s[i]/(len(g[i])+1.0)
        if(utility>max):
            max=utility
            index=i
    g[index].append(n[0])
    del n[0]
    return group(s, g, n)

#不带递归深度的CRG
def CRG(s, g, n):
    if (len(n) == 0):
        # print("finish")
        return g
    else:
        tableNum = len(s)
        res = []
        for i in range(0, tableNum):
            temp_g = copy.deepcopy(g) #列表完全复制
            t = len(g)
            size = []
            for j in range(0, t):
                size.append(len(g[j]))

            temp_g[i].append(n[0])
            temp_n = n[:] #列表的复制,但是只能复制一维的列表
            del temp_n[0]

            temp_res = CRG(s, temp_g, temp_n)
            res.append(s[i] / len(temp_res[i]))
        maxAction = max(res)
        index = res.index(maxAction)

        g[index].append(n[0])
        del n[0]
        return CRG(s, g, n)
'''
@param depth 当前用户预测的深度
@param result 全预测的结果
'''
def PredCRG(s, g, n, depth):
    if len(n)==0:
        # print("11111prediction depth:%d end,customer size:%d" % (depth, len(n)), "group", g)
        return g
    #预测的最后一个顾客是不理性的，它只基于当前的用户分组来进行选择，避免了一直递归到最后一个
    elif depth==0:
        max_utility = 0.0
        index = 0
        for i in range(0, len(s)):
            utility = s[i] / (len(g[i]) + 1.0)
            if (utility > max_utility):
                max_utility = utility
                index = i
        g[index].append(n[0])
        del n[0]
        return g
    else :
        tableNum = len(s)
        res = []
        for i in range(0, tableNum):
            temp_g = copy.deepcopy(g)  # 列表完全复制
            t = len(g)
            size = []
            for j in range(0, t):
                size.append(len(g[j]))

            temp_g[i].append(n[0])
            temp_n = n[:]  # 列表的复制,但是只能复制一维的列表
            del temp_n[0]

            temp_res = PredCRG(s, temp_g, temp_n,depth-1)
            res.append(s[i] / len(temp_res[i]))
        maxAction = max(res)
        index = res.index(maxAction)
        g[index].append(n[0])
        del n[0]
        return PredCRG(s,g,n,depth-1)

def NewCRG(s,g,n,depth):
    if(len(n)==0):
        return g
    else:
        tableNum = len(s)
        res = []
        for i in range(0, tableNum):
            temp_g = copy.deepcopy(g)  # 列表完全复制
            t = len(g)
            temp_g[i].append(n[0])
            temp_n = n[:]  # 列表的复制,但是只能复制一维的列表
            del temp_n[0]
            temp_res = PredCRG(s, temp_g, temp_n, depth)
            res.append(float(s[i]) / float(len(temp_res[i])))
        maxAction = max(res)
        index = res.index(maxAction)
        # print "each action result:",res,"index:",index
        # print("size of n:",len(n))
        g[index].append(n[0])
        # print "%d customer choose %d table" % (n[0], index)
        del n[0]
        return NewCRG(s, g, n, depth)

if __name__== '__main__':
    
    s=[13.2,4.0]
    g=[[],[]]
    n=[1,4,8,2,6,3,7,5]

    t1_n = n[:]
    t1_g = copy.deepcopy(g)
    t2_n = n[:]
    t2_g = copy.deepcopy(g)
    t3_n = n[:]
    t3_g = copy.deepcopy(g)
    seq=group(s,t1_g,t1_n)
    print "sequtial choose:",seq
    res=CRG(s,t2_g,t2_n)
    print "Total CRG result:",res
    newres=NewCRG(s,t3_g,t3_n,0)
    print "NewCRG result:",newres
    # acc=[]
    # max_dep=1
    # for i in range(0,max_dep):
    #     temp_n = n[:]
    #     temp_g = copy.deepcopy(g)
    #     predict=NewCRG(s,temp_g,temp_n,i)

    #     #统计predict的准确率
    #     count=0.0
    #     '计算方法一，相同的选择'
    #     # for j in range(1,len(n)+1):
    #     #     #都在1号餐桌上或者都在2号餐桌上
    #     #     for k in range(0,len(s)):
    #     #         if ((j in res[k]) and (j in predict[k])):
    #     #             count+=1.0
    #     #             break
    #     '计算方法二，相同的效用'
    #     # for j in range(1,len(n)+1):
    #     #     for k in range(0,len(s)):
    #     #         tablenum1=0
    #     #         tablenum2=0
    #     #         for l in range(0,len(res)):
    #     #             if j in res[l]:
    #     #                 tablenum1=l
    #     #         for m in range(0,len(predict)):
    #     #             if j in predict[m]:
    #     #                 tablenum2=m
    #     #         print(j,res[tablenum1],predict[tablenum2])
    #     #         if ((s[tablenum1]/len(res[tablenum1])==s[tablenum2]/len(predict[tablenum2]))):
    #     #             count+=1.0
    #     #             break
    #     t_acc=count/len(n)
    #     print ("predict depth:%d" %i,"predict:",predict,"accuracy:%f"%t_acc)
    #     acc.append(t_acc)
    # #绘制准确率变化图像
    # plt.figure()
    # x = [j for j in range(0,max_dep)]
    # y = acc
    # plt.plot(x,y,marker = '*',label="accuracy")
    # plt.show()