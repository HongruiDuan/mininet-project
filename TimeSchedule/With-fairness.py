# -*- coding:utf-8 -*-
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
import json
import random
from NewGame import game
from fairness import Fairness
from RankByNSGA import Rank

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
def topology():
    #创建网络和设备初始化
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       wmediumd_mode=interference)
    #设备初始化
    ap1 = net.addAccessPoint('ap1', ssid="ap1-ssid", mode="g",
                             channel="1", position='5,6,0',range=40)
    AP = net.addStation('AP', position='5,10,0', ip='10.1.0.1', mac='00:00:00:00:00:EE') 

    UES = []
    for i in range(1,21):
        #创建中继设备节点
        temphost = net.addStation('DU%d'%i, position='%d,5,0'%(i+37), ip='10.0.0.%d'%i, mac='00:00:00:00:00:%02d'%i)
        #创建中继设备类对象
        temp = UE(temphost,'UE%d'%i,'10.0.0.%d'%i, 'DU%d-wlan0' %i,0.05+0.03*i) #丢包率已经初始化完毕
        UES.append(temp)
    
    #打印出设备池中的设备信息
    # for i in range(0,20):
    #     print(UES[i].name,UES[i].ip,UES[i].port,UES[i].Power,'\n')
    

    c0 = net.addController('c0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Adding Link\n")
    net.addLink(AP, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    for i in range(0,9):
        net.addLink(UES[i].host, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    #设备初始化完毕，开始进行调度
    "总共进行50轮数据传输"
    Total_r = 50
    round = 0
    fair_result = []
    while round<Total_r:
        #根据设备的丢包率来计算博弈结果，写入中继设备
        for i in range(0,20):
            result = game(UES[i].link_e)
            UES[i].F_BS = result[2]
            UES[i].F_UE = result[3]
            UES[i].N1 = result[0]
            UES[i].b = result[1]
        
        #根据设备能够达到的基站的效益对所有中继设备进行排序
        queue = sorted(UES, key = lambda UE: UE.F_BS, reverse=True)

        #根据多目标优化方法对中继设备计算rank值（todo:只用rank作为排序有些不合理）
        '''
        在进行NSGA——II求解之前先判断能量是否足够传输,满足能量需求的中继设备才是候选解集
        '''
        len_que = len(queue)
        for i in range(0,len_que):
            if (queue[i].N1*0.00004) > queue[i].Power:
                del queue[i]
                len_que-=1

        num = Rank(UES,queue)
        #打印中继设备的信息
        # for i in range(0,20):
        #     print(queue[i].rank,queue[i].F_BS,queue[i].F_UE, queue[i].N1,queue[i].gains,queue[i].Power)
        
        #开始发送信息
        
        
        if (queue[num].N1*0.00004) < queue[num].Power:
            print('the %d-th device has been selected' % num)
            TotalTime = 10 #时间片大小
            # FileIndex = 0 #发送文件位置
            dst = []
            for i in range(0,20):
                dst.append(queue[i].ip)
            #随机一个中继设备为RU
            dev_num = random.randint(0,20)
            #先不采用广播的方法
            for i in range(0,TotalTime):  #有100个最小时隙，AP广播100轮，DU选择接收能量和信息，RU直接接收信息  
                "此处AP应该改成广播，APsend 的 dst应该不止一个"                  
                # t1 = threading.Thread(target=command, args = (AP,"python APBroadCast.py 10.1.0.1 AP-wlan0 '%s' %s" %(dst,FileIndex)))#AP广播一个数据包                    
                #一个随机设备请求信息，因此其只接收信息                    
                # t2 = threading.Thread(target=command, args = (queue[dev_num].host,"python Receive.py %s %s 0.5"%(queue[dev_num].ip,queue[dev_num].port)))                    
                #其他的中继设备按照自身的丢包率来进行能量和信息收集
                "先采用的是直接数值模拟，并没有进行实际的发送和接收包"
                for j in range(0,20):
                    if j != dev_num:
                        top1 = int(100-100*queue[j].link_e)
                        key1 = random.randint(1,1000)
                        "中继设备随机接收信息或者能量"
                        if key1 in range(1,top1):
                            pass
                            # info("DU%d infomation\n"% j)
                        else:
                            pass
                            # info("DU%d energy\n"% j)
                            egy = energy(UES[j].host, AP, 0.011/TotalTime)
                            UES[j].Power += egy 
                                                   
            #被选中的中继设备将传输满足博弈均衡的有效信息量给请求的客户端设备
            #中继设备的发射功率为4mw，一个数据包为1k，中继设备的发射速率为100k/s
            "选中的中继设备通过中继减少能量，增加收益"
            queue[num].Power -= queue[num].N1*0.00004
            queue[num].gains += queue[num].F_UE

            print("在第%d轮中，各中继设备的状态信息" % round)
            for i in range(0,20):
                    print(UES[i].rank,UES[i].F_BS,UES[i].F_UE,UES[i].N1,UES[i].gains,UES[i].Power)

            
        #如果所有中继设备能量都不够，则基站自己传输
        if num == 21:
            pass    
        #计算当前轮的fairness指数
        fair_result.append(Fairness(UES))
        
        round += 1

    info("*** Fairness")
    print(fair_result)
    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()

