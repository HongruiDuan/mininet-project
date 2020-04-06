# -*- coding:utf-8 -*-

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference


import random
import thread
import threading
import copy
from API.NewCRG import NewCRG
from API.NewGame import game
from EH.newenergy import energy
from MMO.Devide_by_NSGAII import devide

"线程函数"
def command(host, arg):
    result = host.cmd(arg)
    return result
"线程类"
class MyThread(threading.Thread):

    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

'''
    每个FogCell的行为是并行的
    @param AP AP
    @param UES 每个FogCell中的顾客
    @RU FogCell中的RUlist【】，初始一个FogCell中都只有一个RU
    @cellnum 通过RU list 和cellnum可以确定 RU[i] 

'''
def fogcell(AP,UES,RU,cellnum):
    if(len(UES)==0):
        return -1
    "根据设备的丢包率来计算博弈结果，写入中继设备"
    total_e=0
    for i in range(0,len(UES)):
        total_e += UES[i].link_e
    result = game(1-total_e/len(UES))
    for i in range(0,len(UES)):
        UES[i].F_BS = result[2]
        UES[i].F_UE = result[3]
        UES[i].N1 = result[0]
        UES[i].b = result[1]
    "根据设备丢包率将UES,排成队列"
    queue = sorted(UES, key = lambda UE: UE.link_e, reverse=False)
    queue_num=[]
    for i in range(0,len(UES)):
        queue_num.append(queue[i].num)
    print "queue:",queue_num

    '''
    根据哪个提升通信速率比较大来决定是否进行中继,CRG问题
    总共的频谱大小为20Mhz,RU购买15Mhz 剩余5Mhz
    '''
    #进餐人数
    cus_number=[]
    for i in range(0,len(queue)):
        cus_number.append(queue[i].num)

    
    #各餐桌大小
    band_price = 10 #每单位频谱的售价
    #参与中继的餐桌的大小 单位时 MHZ 转化到速率   再转化到效用
    desk_relay = UES[0].F_UE/band_price + 15*6/25
    
    # desk_relay = 4
    #不中继的餐桌大小
    desk_norelay = 4

    table_size=[desk_relay,desk_norelay]
    g=[[],[]]
    #调用CRG求得各个餐桌上分组情况
    # print "in FogCell n:",cus_number

    "CRG 递归深度"
    # # print "exec NewCRG table size:",table_size,"customer:",cus_number
    # CRG_result=NewCRG(table_size,g,cus_number,7)
    


    '采用多目标优化求解这个最优化问题'
    #进餐人数
    cus=[]
    for i in range(0,len(queue)):
        cus.append(queue[i])
    #RU[]和cellnum确定唯一一个RU
    ##"cus值的复制在内部函数完成吧"
    #def devide(cus,s,RU,cellnum):
    CRG_result=[[1,4,8,2,6,3,7],[5]]
    # CRG_result=devide(cus,table_size,RU,cellnum)

    print "CRG_result",CRG_result
    for i in range(0,len(UES)):
        if (UES[i].num in CRG_result[0]):
            UES[i].relay=True

    "AP广播期间，中继收集信息收集能量，不做中继的收集能量"
    TotalTime=10#基站广播时间10ms
    for i in range(0,TotalTime):                    
        for j in range(0,len(UES)):
            if UES[j].relay==True:
                top1 = int(100-100*UES[j].link_e)
                key1 = random.randint(0,100)
                "中继设备随机接收信息或者能量"
                if key1 in range(0,top1):
                    pass
                else:
                    #0.03125含义是基站总的广播时间？      
                    egy = energy(UES[j].host, AP, 0.03125/TotalTime)
                    UES[j].Power += egy #第j个设备收集能量
            else:
                #不参与中继的设备每个时隙都在进行能量收集
                egy = energy(UES[j].host, AP, 0.03125/TotalTime)
                UES[j].Power += egy #第j个设备收集能量
    "中继传输信息阶段"
    for i in range(0,len(UES)):
        #成为中继依次给RU发送信息
        if(queue[i].relay == True):
            info("FD %d start relaying  \n" % queue[i].num) 
            # def send(src, iface, dst, loss, index,send_pkt=[]):
            t1 = threading.Thread(target=command, args = (queue[i].host,"python Send.py '%s' %s '%s' 0.1 %d"
                                                            % (queue[i].ip,queue[i].port,RU[queue[i].cellnum].ip,i)))#AP广播一个数据包                                      
            # def receive(ip, iface, loss,filter="icmp", rc_pkt=[]):
            t2 = threading.Thread(target=command, args = (RU[queue[i].cellnum].host,"python Receive.py '%s' %s 0.1"
                                                                                    % (RU[queue[i].cellnum].ip,RU[queue[i].cellnum].port) ))
            t2.start()
            t1.start()
            t1.join()
            t2.join()
            # info("FD %d end\n" % queue[i].num)
            queue[i].Power -= (queue[i].N1*0.00004)/len(CRG_result[0])
            #效用计算 需要将占用的带宽资源也加入进去
            # queue[i].gains += queue[i].F_UE/len(CRG_result[0])
            
            "desk_realay 的效用,是包括了BS给予的激励的"
            queue[i].gains += ((desk_relay)/len(CRG_result[0]))*10
        else:
            #不参与中继的设备继续进行能量收集
            egy = energy(UES[i].host, AP, 0.03125/TotalTime)
            UES[i].Power += egy #第j个设备收集能量
            
            "desk_norelay 的效用"
            queue[i].gains += ((desk_norelay)/len(CRG_result[1]))*10