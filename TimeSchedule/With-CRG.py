# -*- coding:utf-8 -*-
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference


from EH.newenergy import energy
from Params.params import getDistance
import numpy as np
np.set_printoptions(suppress=True)
import thread
import threading
import time
import json
import random
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size': 10}) # 改变所有字体大小，改变其他性质类似
from API.fairness import Fairness
from API.RankByNSGA import Rank
from API.NewGame import game
from EH.LossRate import LossRate_FDS_RU
from API.nTableGame import CRG
from API.DrawPow import drawPowAndGain


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
#设备类，存储设备的信息
random.seed(2)

class UE:
    count = 0
    def __init__(self, host, name, ip, port, link_e, num ,gains=0.0, F_BS=0.0, F_UE=0.0, N1=0.0, b=0.0, Power = 0, relay = False,flag=False):
        self.host = host
        self.name = name
        self.ip = ip
        self.port = port
        self.link_e = link_e
        self.num = num
        self.Power = random.uniform(0.001, 0.0015)
        self.gains = 0
        self.rank = 0
        self.relay = False
        self.powhis = [self.Power]
        self.gainhis = [self.gains]
        UE.count += 1

  

def topology(DeviceNum,Total_r):
    #创建网络和设备初始化
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       wmediumd_mode=interference)
    #设备初始化
    AP = net.addStation('AP', position='5,10,0', ip='10.1.0.1', mac='00:00:00:00:00:EE') 
    RU = net.addStation('RU', position='25,25,0', ip='10.1.0.2',mac='00:00:00:00:00:FF')


    UES = []
    for i in range(0, DeviceNum):
        temp=i+1
        # 创建中继设备节点
        temphost = net.addStation('DU%d' % temp, position='%d,%d,0' % (random.randint(3, 45), random.randint(3, 45)),
                                  ip='10.0.0.%d' % temp, mac='00:00:00:00:00:%02d' % temp)
        # 创建中继设备类对象
        # temp = UE(temphost,'UE%d'%i,'10.0.0.%d'%i, 'DU%d-wlan0' %i,0.05+0.03*i,i) #丢包率已经初始化完毕
        # 根据位置确定丢包率
        temp = UE(temphost, 'DU%d' % temp, '10.0.0.%d' % temp, 'DU%d-wlan0' % temp, LossRate_FDS_RU(temphost, RU), temp)
        UES.append(temp)
    
    #打印出设备池中的设备信息
    for i in range(0,DeviceNum):
        print UES[i].name,UES[i].ip,UES[i].port,UES[i].Power
    

    c0 = net.addController('c0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()
    

    info("*** Adding Link\n")
    net.addLink(AP, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    net.addLink(RU, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    for i in range(0,len(UES)):
        net.addLink(UES[i].host, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')

    info("*** Starting network\n")
    net.build()
    c0.start()
    
    #设备初始化完毕，开始进行调度
    
    round = 0
    fair_result=[]
    while round<Total_r:
        #显示当前的设备分布
        locate=net.plotGraph(max_x=50, max_y=50)

        #根据设备的丢包率来计算博弈结果，写入中继设备
        total_e=0
        for i in range(0,DeviceNum):
            total_e += UES[i].link_e
        result = game(1-total_e/20)
        for i in range(0,DeviceNum):
            UES[i].F_BS = result[2]
            UES[i].F_UE = result[3]
            UES[i].N1 = result[0]
            UES[i].b = result[1]
        print 'result:',UES[i].F_UE,UES[0].N1,UES[0].b
        #根据设备丢包率将UES,排成队列
        queue = sorted(UES, key = lambda UE: UE.link_e, reverse=True)
        queue_num=[]
        for i in range(0,DeviceNum):
            queue_num.append(queue[i].num)
        print "queue:",queue_num
        #根据哪个提升通信速率比较大来决定是否进行中继
        '''
        总共的频谱大小为20Mhz,RU购买15Mhz 剩余5Mhz
        '''
        #进餐人数
        cus_number=[]
        for i in range(0,DeviceNum):
            cus_number.append(UES[i].num)
        
        #各餐桌大小
        band_price = 10 #每单位频谱的售价
        desk_relay = UES[0].F_UE/band_price + 15*6/25
        desk_norelay = 8
        table_size=[desk_relay,desk_norelay]
        g=[[],[]]
        #调用CRG求得各个餐桌上分组情况
        CRG_result=CRG(table_size,g,cus_number)

        print "CRG_result",CRG_result
        for i in range(0,DeviceNum):
            if (UES[i].num in CRG_result[0]):
                UES[i].relay=True

        #AP广播期间，中继收集信息收集能量，不做中继的收集能量
        TotalTime=10#基站广播时间10ms
        for i in range(0,TotalTime):                    
            for j in range(0,len(UES)):
                if UES[j].relay==True:
                    top1 = int(100-100*UES[j].link_e)
                    key1 = random.randint(1,100)
                    "中继设备随机接收信息或者能量"
                    if key1 in range(1,top1):
                        pass
                    else:      
                        egy = energy(UES[j].host, AP, 0.03125/TotalTime)
                        UES[j].Power += egy #第j个设备收集能量
                else:
                    #不参与中继的设备每个时隙都在进行能量收集
                    egy = energy(UES[j].host, AP, 0.03125/TotalTime)
                    UES[j].Power += egy #第j个设备收集能量
        #中继传输信息阶段
        for i in range(0,DeviceNum):
            #成为中继依次给RU发送信息
            if(queue[i].relay == True):
                info("FD %d start sending  " % queue[i].num) 
                # def send(src, iface, dst, loss, index,send_pkt=[]):
                t1 = threading.Thread(target=command, args = (queue[i].host,"python Send.py '%s' %s 10.1.0.2 0.1 %d" % (queue[i].ip,queue[i].port,i)))#AP广播一个数据包                                      
                # def receive(ip, iface, loss,filter="icmp", rc_pkt=[]):
                t2 = threading.Thread(target=command, args = (RU,"python Receive.py 10.1.0.2 RU-wlan0 0.1"))
                t2.start()
                t1.start()
                t1.join()
                t2.join()
                info("FD %d end\n" % queue[i].num)
                queue[i].Power -= (queue[i].N1*0.00004)/len(CRG_result[0])
                queue[i].gains += queue[i].F_UE/len(CRG_result[0])
            else:
                #不参与中继的设备继续进行能量收集
                egy = energy(UES[i].host, AP, 0.03125/TotalTime)
                UES[i].Power += egy #第j个设备收集能量

        for k in range(0,DeviceNum):
            UES[k].powhis.append(UES[k].Power)#不管是否发送都要增加记录
            UES[k].gainhis.append(UES[k].gains)

        fair_result.append(Fairness(UES))
        round += 1
    
    "绘制每个设备的能量和效用变化图像"
    drawPowAndGain(UES,Total_r)


    info("*** Fairness")
    print(fair_result)

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
     #"创建网络拓扑，定义网络参数"
    DeviceNum=5  #FD总数量
    Total_r=2  #进行轮数  
    topology(DeviceNum,Total_r)


