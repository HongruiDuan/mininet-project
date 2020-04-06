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
            # print("in %d" % i, "size of g:", size)
            temp_g[i].append(n[0])
            temp_n = n[:] #列表的复制,但是只能复制一维的列表
            del temp_n[0]
            # print("size of n:", len(n))
            temp_res = CRG(s, temp_g, temp_n)
            res.append(s[i] / len(temp_res[i]))
        maxAction = max(res)
        index = res.index(maxAction)
        # print("size of n:",len(n))
        g[index].append(n[0])
        del n[0]
        return CRG(s, g, n)
'''
@param depth 当前用户预测的深度
@param result 全预测的结果
'''
def NewCRG(s, g, n, depth,mdep):
    
    if len(n)==0 and depth==mdep:
        print "CRG game end, customer size:%d and depth:%d"%(len(n),depth),"group:",g
        return g
    elif len(n)==0 and depth<mdep:
        print "prediction depth:%d end,customer size:%d"%(depth,len(n)),"group",g
        return g
    elif len(n)!=0 and depth<0:
        print "prediction depth:%d end,customer size:%d"%(depth,len(n)),"group",g
        return g
    else:
        tableNum = len(s)
        res=[]
        for i in range(0,tableNum):
            temp_g = copy.deepcopy(g) #列表完全复制
            t = len(g)
            temp_g[i].append(n[0])
            temp_n = n[:] #列表的复制,但是只能复制一维的列表
            del temp_n[0]
            temp_res = NewCRG(s, temp_g, temp_n, depth-1,mdep)
            res.append(s[i] / len(temp_res[i]))
        maxAction = max(res)
        index = res.index(maxAction)
        # print("size of n:",len(n))
        g[index].append(n[0])
        print "%d cus choose %d table"%(n[0],index)
        del n[0]
        return NewCRG(s, g, n,depth,mdep)
if __name__== '__main__':
    s=[1.0,1.0]
    g=[[],[]]
    n=[i for i in range(1,8)]

    t1_n = n[:]
    t1_g = copy.deepcopy(g)
    t2_n = n[:]
    t2_g = copy.deepcopy(g)
    seq=group(s,t1_g,t1_n)
    print "sequtial:",seq
    res=CRG(s,t2_g,t2_n)
    print "result:",res
    acc=[]
    max_dep=3
    for i in range(0,max_dep):
        temp_n = n[:]
        temp_g = copy.deepcopy(g)
        predict=NewCRG(s,temp_g,temp_n,i,i)

        #统计predict的准确率
        count=0.0
        for j in range(1,len(n)+1):
            #都在1号餐桌上或者都在2号餐桌上
            for k in range(0,len(s)):
                if ((j in res[k]) and (j in predict[k])):
                    count+=1.0
                    break
        t_acc=count/len(n)
        print 
        print "predict depth:%d" %i,"predict:",predict,"accuracy:%f"%t_acc
        acc.append(t_acc)
    #绘制准确率变化图像
    plt.figure()
    x = [j+1 for j in range(0,max_dep)]
    print x
    y = acc
    print y
    plt.plot(x,y,marker = '*',label="accuracy")
    plt.show()

    
    

        
