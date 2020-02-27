# -*- coding:utf-8 -*-
'''
博弈递归函数，
参数
g 当前餐桌人数
n 剩余顾客数量
'''
desk_norelay = 5.0
desk_relay = 13.4776494955448
totalCus=22
def group(relay_num,norelay_num,n):
    if(n==0):
        print "finish",relay_num," ",norelay_num
        return [relay_num,norelay_num]
    elif(float(desk_relay/(relay_num+1))>float(desk_norelay/(norelay_num+1))):
        print "select relay",relay_num,"no relay:",norelay_num,"select relay utility:",float(desk_relay/(relay_num+1)),"no relay utility:",float(desk_norelay/(norelay_num+1))
        return group(relay_num+1,norelay_num,n-1)
    else:
        print "select relay",relay_num,"no relay:",norelay_num,"select relay utility:",float(desk_relay/(relay_num+1)),"no relay utility:",float(desk_norelay/(norelay_num+1))
        return group(relay_num,norelay_num+1,n-1)


if __name__== '__main__':
    num_relay = []
    num_norelay = []
    for i in range(0,totalCus):
        n1=len(num_relay)
        n2=len(num_norelay)
        #加入relay餐桌的效用
        res1=group(n1+1,n2,totalCus-1-i)
        #加入不relay餐桌的效用
        res2=group(n1,n2+1,totalCus-1-i)
        if((desk_relay/res1[0])>(desk_norelay/res2[1])):
            num_relay.append(i)
        else:
            num_norelay.append(i)
        print "the %d FD"%i," ",num_relay," ",num_norelay
        

        
