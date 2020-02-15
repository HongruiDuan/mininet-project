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
from NewGame import game
from fairness import Fairness
from RankByNSGA import Rank
from EH.LossRate import LossRate_FDS_RU


"香农公式，根据带宽和信噪比计算理论最大速率"
def rate():
    pass
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
        UE.count += 1
def topology():
    #创建网络和设备初始化
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       wmediumd_mode=interference)
    #设备初始化
    AP = net.addStation('AP', position='5,10,0', ip='10.1.0.1', mac='00:00:00:00:00:EE') 
    RU = net.addStation('RU', position='25,25,0', ip='10.1.0.2',mac='00:00:00:00:00:FF')


    UES = []
    for i in range(1, 21):
        # 创建中继设备节点
        temphost = net.addStation('DU%d' % i, position='%d,%d,0' % (random.randint(3, 45), random.randint(3, 45)),
                                  ip='10.0.0.%d' % i, mac='00:00:00:00:00:%02d' % i)
        # 创建中继设备类对象
        # temp = UE(temphost,'UE%d'%i,'10.0.0.%d'%i, 'DU%d-wlan0' %i,0.05+0.03*i,i) #丢包率已经初始化完毕
        # 根据位置确定丢包率
        temp = UE(temphost, 'UE%d' % i, '10.0.0.%d' % i, 'DU%d-wlan0' % i, LossRate_FDS_RU(temphost, RU), i)
        UES.append(temp)
    
    #打印出设备池中的设备信息
    for i in range(0,20):
        print UES[i].name,UES[i].ip,UES[i].port,UES[i].Power
    

    c0 = net.addController('c0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()
    net.plotGraph(max_x=50, max_y=50)

    info("*** Adding Link\n")
    net.addLink(AP, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    net.addLink(RU, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    for i in range(0,len(UES)):
        net.addLink(UES[i].host, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')

    info("*** Starting network\n")
    net.build()
    c0.start()
    
    #设备初始化完毕，开始进行调度
    
    Total_r = 1
    round = 0

    while round<Total_r:
        #根据设备的丢包率来计算博弈结果，写入中继设备
        total_e=0
        for i in range(0,20):
            total_e += UES[i].link_e
        result = game(1-total_e/20)
        for i in range(0,20):
            UES[i].F_BS = result[2]
            UES[i].F_UE = result[3]
            UES[i].N1 = result[0]
            UES[i].b = result[1]
        print 'result:',UES[i].F_UE,UES[0].N1,UES[0].b
        #根据设备能够达到的基站的效益对所有中继设备进行排序
        queue = sorted(UES, key = lambda UE: UE.link_e, reverse=True)
        queue_num=[]
        for i in range(0,20):
            queue_num.append(queue[i].num)
        print "queue:",queue_num
        #根据哪个提升通信速率比较大来决定是否进行中继
        '''
        总共的频谱大小为20Mhz,RU购买15Mhz 剩余5Mhz

        '''
        relay_num = 0
        norelay_num = 0
        band_price = 10
        #中继的餐桌大小为 
        desk_relay = UES[0].F_UE/band_price + 15*6/25
        desk_norelay = 5
        for i in range(0,20):
            if((desk_relay/(relay_num+1))>(desk_norelay/(norelay_num+1))):
                queue[i].relay = True
                relay_num += 1 
            else:
                norelay_num += 1
        num_relay = []
        num_norelay = []
        for i in range(0,20):
            if(queue[i].relay == True):
                num_relay.append(queue[i].num)
            else:
                num_norelay.append(queue[i].num)
        print "relay:",num_relay
        print "no_relay:",num_norelay
        
        for i in range(0,20):
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


                
        #开始发送信息 
        # if (queue[num].N1*0.00004) < queue[num].Power:
        #     print('the %d-th device has been selected' % queue[num].num)
        #     TotalTime = 20 #时间片大小
        #     # FileIndex = 0 #发送文件位置
        #     dst = []
        #     for i in range(0,len(queue)):
        #         dst.append(queue[i].ip)
        #     #随机一个中继设备为RU
        #     # dev_num = random.randint(0,20)
        #     #先不采用广播的方法
        #     for i in range(0,TotalTime):  #有100个最小时隙，AP广播100轮，DU选择接收能量和信息，RU直接接收信息  
        #         "此处AP应该改成广播，APsend 的 dst应该不止一个"                  
        #         # t1 = threading.Thread(target=command, args = (AP,"python APBroadCast.py 10.1.0.1 AP-wlan0 '%s' %s" %(dst,FileIndex)))#AP广播一个数据包                    
        #         #一个随机设备请求信息，因此其只接收信息                    
        #         # t2 = threading.Thread(target=command, args = (queue[dev_num].host,"python Receive.py %s %s 0.5"%(queue[dev_num].ip,queue[dev_num].port)))                    
        #         #其他的中继设备按照自身的丢包率来进行能量和信息收集
        #         "先采用的是直接数值模拟，并没有进行实际的发送和接收包"
        #         for j in range(0,len(UES)):
        #             if (j+1) == queue[num].num:
        #                 top1 = int(100-100*UES[j].link_e)
        #                 key1 = random.randint(1,100)
        #                 "中继设备随机接收信息或者能量"
        #                 if key1 in range(1,top1):
        #                     pass
        #                 else:      
        #                     egy = energy(UES[j].host, AP, 0.03125/TotalTime)
        #                     UES[j].Power += egy #第j个设备收集能量
        #                 # UES[j].powhis.append(egy)
        #             else:
        #                 egy = energy(UES[j].host, AP, 0.03125/TotalTime)
        #                 UES[j].Power += egy #第j个设备收集能量
                                                   
        #     #被选中的中继设备将传输满足博弈均衡的有效信息量给请求的客户端设备
        #     #中继设备的发射功率为4mw，一个数据包为1k，中继设备的发射速率为100k/s
        #     "选中的中继设备通过中继减少能量，增加收益"
        #     print('the %d-th device has been selected, power from %f to %f' % (queue[num].num,queue[num].Power,queue[num].Power-queue[num].N1*0.00004))
        #     queue[num].Power -= queue[num].N1*0.00004 
        #     queue[num].gains += queue[num].F_UE

        round += 1
    
    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()


