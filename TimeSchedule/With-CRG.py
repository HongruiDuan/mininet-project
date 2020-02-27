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
import datetime
import os #创建文件夹
import shutil #删除文件夹
import copy #深拷贝赋值
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
from API.Move import move
from API.DrawLocate import drawLocate

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
    def __init__(self, host, name, ip, port, link_e, num ,cellnum,
                gains=0.0, F_BS=0.0, F_UE=0.0, N1=0.0, b=0.0, Power = 0, online=True,relay = False):
        self.host = host
        self.name = name
        self.ip = ip
        self.port = port
        self.link_e = link_e
        self.locate=[self.host.params['position'][0],self.host.params['position'][1]]
        self.speed=random.randint(1,10)
        self.num = num
        self.Power = random.uniform(0.001, 0.0015)
        self.cellnum=cellnum #为0的时候不加入fogcell
        self.gains = 0
        self.rank = 0
        self.online=True
        self.relay = False
        self.powhis = [self.Power]
        self.gainhis = [self.gains]
        UE.count += 1

  

def topology(DeviceNum,RUnum,Total_r):
    #创建网络和设备初始化
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       wmediumd_mode=interference)
    #设备初始化
    AP = net.addStation('AP', position='0,25,0', ip='10.1.0.1', mac='00:00:00:00:00:EE')
    #创建RU
    RU=[]
    for i in range(0,RUnum):
        t=i+1
        temphost = net.addStation('RU%d'% t, position='%d,%d,0' % (random.randint(20, 30), random.randint(20, 30)), 
                                    ip='10.2.0.%d' % t,mac='00:00:00:00:0E:%02d'%t)
        #对于每一个设备遍历在其D2D通信范围内的RU,寻求一个丢包率最小的RU的Fogcell加入
        temp=UE(temphost, 'RU%d' % t, '10.0.0.%d' % t, 'RU%d-wlan0' % t, 0.0, t, -1)
        RU.append(temp)
        # RU2 = net.addStation('RU2', position='25,15,0', ip='10.1.0.3',mac='00:00:00:00:00:DF')
    #创建FD
    UES = []
    for i in range(0, DeviceNum):
        t=i+1
        # 创建中继设备节点
        temphost = net.addStation('DU%d' % t, position='%d,%d,0' % (random.randint(10, 40), random.randint(10, 40)),
                                  ip='10.0.0.%d' % t, mac='00:00:00:00:00:%02d' % t)
        
        # 根据位置确定到达哪个RU的丢包率比较小，加入其cell
        min=1 #选择一个丢包率最小的
        index=0
        for j in range(0,len(RU)):
            t_loss=LossRate_FDS_RU(temphost, RU[j].host)
            if t_loss<=min:
                min=t_loss
                index=j
        print "in %d-th FD, %d-RU has been choosed,min loos:%d" %(t,index,t_loss)
        temp = UE(temphost, 'DU%d' % t, '10.0.0.%d' % t, 'DU%d-wlan0' % t, 0.0, t, -1) #初始化的时候先不管
        UES.append(temp)
    
    #打印出设备池中的设备信息
    for i in range(0,RUnum):
        print RU[i].name,RU[i].locate
    for i in range(0,DeviceNum):
        print UES[i].name,UES[i].Power,UES[i].locate,"cellnum:",UES[i].cellnum
    

    c0 = net.addController('c0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()
    

    info("*** Adding Link\n")
    net.addLink(AP, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    for i in range(0,len(RU)):
        net.addLink(RU[i].host, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    # net.addLink(RU1, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')

    for i in range(0,len(UES)):
        net.addLink(UES[i].host, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    
    net.plotGraph(max_x=50, max_y=50)

    info("*** Starting network\n")
    net.build()
    c0.start()
    
    #设备初始化完毕，开始进行调度
    
    round = 0
    fair_result=[]
    path='Figures/'+str(datetime.date.today()) #在net.py中调用是相对于net.py的目录
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    while round<Total_r:
        #显示当前的设备分布
        # net.plotGraph(max_x=50, max_y=50) #无返回值，不能保存，只能修改源码,同时写在此处调用无反应，只能自己实现绘制地理位置
        # print "locate when start"
        # for i in range(0,DeviceNum):
        #     print UES[i].name,UES[i].host.params['position'][0],UES[i].host.params['position'][1]
        "自己实现绘制各个设备的地理位置图像，二维的"
        drawLocate(AP,RU,UES,round)
        "根据这一轮开始时设备的地理位置来计算最小的Fogcell加入"
        for i in range(0, DeviceNum):
            t=i+1
            # 根据位置确定到达哪个RU的丢包率比较小，加入其cell
            min=1 #选择一个丢包率最小的
            index=0
            for j in range(0,len(RU)):
                t_loss=LossRate_FDS_RU(temphost, RU[j].host)
                if t_loss<=min:
                    min=t_loss
                    index=j
            print "in %d-th FD, %d-RU has been choosed,min loos:%d" %(t,index,t_loss)
            UES[i].link_e=t_loss
            UES[i].cellnum=index
        "根据设备的丢包率来计算博弈结果，写入中继设备"
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
        "根据设备丢包率将UES,排成队列"
        queue = sorted(UES, key = lambda UE: UE.link_e, reverse=True)
        queue_num=[]
        for i in range(0,DeviceNum):
            queue_num.append(queue[i].num)
        print "queue:",queue_num

        '''
        根据哪个提升通信速率比较大来决定是否进行中继,CRG问题
        总共的频谱大小为20Mhz,RU购买15Mhz 剩余5Mhz
        '''
        #进餐人数
        cus_number=[]
        for i in range(0,DeviceNum):
            if(UES[i].online):
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

        "AP广播期间，中继收集信息收集能量，不做中继的收集能量"
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
        "中继传输信息阶段"
        for i in range(0,DeviceNum):
            #成为中继依次给RU发送信息
            if(queue[i].relay == True):
                info("FD %d start sending  " % queue[i].num) 
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
                info("FD %d end\n" % queue[i].num)
                queue[i].Power -= (queue[i].N1*0.00004)/len(CRG_result[0])
                queue[i].gains += queue[i].F_UE/len(CRG_result[0])
            else:
                #不参与中继的设备继续进行能量收集
                egy = energy(UES[i].host, AP, 0.03125/TotalTime)
                UES[i].Power += egy #第j个设备收集能量
            

        fair_result.append(Fairness(UES))

        #round +1之前移动设备和 设备持续时间
        for i in range(0,DeviceNum):
            #更新能量信息
            UES[i].powhis.append(UES[i].Power)#不管是否发送都要增加记录
            UES[i].gainhis.append(UES[i].gains)
            #更新位置信息
            direct=random.randint(0,360)
            res=move(UES[i].locate,UES[i].speed,direct)
            UES[i].host.params['position'][0]=res[0]
            UES[i].host.params['position'][1]=res[1]
            UES[i].locate=res
            #位置更新了更新丢包率,在传输开始的时候更新丢包率
            # UES[i].link_e=LossRate_FDS_RU(UES[], RU1)
     
        
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
    DeviceNum=10 #FD总数量
    RUnum=3 #RU总数量
    Total_r=2  #进行轮数  
    topology(DeviceNum,RUnum,Total_r)


