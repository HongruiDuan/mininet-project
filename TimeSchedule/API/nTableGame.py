# -*- coding:utf-8 -*-

'''
    博弈递归函数参数
    @param:s 各个餐桌大小
    @param:g 各个餐桌人数
    @param:n 顾客序号数组
    要考虑到后面顾客的行为，因此每个顾客的决策是考虑到后面顾客的决定之后再做出的选择
    自己选择每个餐桌的 +后面的人数 作为子博弈 一直递归到最后一名顾客再决定哪个选择的效用比较高
    递归时间复杂度 对于每一个用户都要预测到最后一个用户n^n
    优化方法：存储最终的情况？ 但是对于第i个用户，选择不同的动作，到达的最终情况不同
'''
import copy

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
if __name__== '__main__':
    s=[4.0,5.0,6.0]
    g=[[],[],[]]
    n=[1,2,3,4,5,6,7,8,9,10]
    
    res=CRG(s,g,n)
    print res
        

        
