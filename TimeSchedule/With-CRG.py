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

from API.NewCRG import NewCRG
from API.DrawPow import drawPowAndGain
from API.Move import move
from API.DrawLocate import drawLocate
from FogCell import fogcell

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
        self.speed=random.randint(1,2)
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
    AP = net.addStation('AP', position='0,0,0', ip='10.1.0.1', mac='00:00:00:00:00:EE')
    #创建RU
    RU=[]
    for i in range(0,RUnum):
        t=i+1
        temphost = net.addStation('RU%d'% t, position='%d,%d,0' % (random.randint(200, 210), random.randint(200, 210)), 
                                    ip='10.2.0.%d' % t,mac='00:00:00:00:0E:%02d'%t)
        #对于每一个设备遍历在其D2D通信范围内的RU,寻求一个丢包率最小的RU的Fogcell加入
        temp=UE(temphost, 'RU%d' % t, '10.0.0.%d' % t, 'RU%d-wlan0' % t, 0.0, t, -1)#初始化的时候参数先不管
        RU.append(temp)
    #创建FD
    UES = []
    for i in range(0, DeviceNum):
        t=i+1
        # 创建中继设备节点
        temphost = net.addStation('DU%d' % t, position='%d,%d,0' % (random.randint(180, 200), random.randint(180, 200)),
                                  ip='10.0.0.%d' % t, mac='00:00:00:00:00:%02d' % t)
        temp = UE(temphost, 'DU%d' % t, '10.0.0.%d' % t, 'DU%d-wlan0' % t, 0.0, t, -1) 
        UES.append(temp)
    
    #打印出设备池中的设备信息
    for i in range(0,RUnum):
        print RU[i].name,RU[i].locate
    
    

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
    
    # net.plotGraph(max_x=300, max_y=300)

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

    #D2D最大的通信距离
    D2DMax_dis=200

    while round<Total_r:
        #显示当前的设备分布
        # net.plotGraph(max_x=50, max_y=50) #无返回值，不能保存，只能修改源码,同时写在此处调用无反应，只能自己实现绘制地理位置
        "自己实现绘制各个设备的地理位置图像，二维的"
        drawLocate(AP,RU,UES,round)
        "根据这一轮开始时设备的地理位置来计算最小的Fogcell加入"
        Fog_cell=[]
        for i in range(0,RUnum):
            Fog_cell.append([])
        for i in range(0, DeviceNum):
            if(UES[i].online) and (UES[i].Power>5*0.00004):  #只有在线的设备才选择加入Fogcell,并且要能量充足，最终的能量值不能为负值
                t=i+1
                # 根据位置确定到达哪个RU的丢包率比较小，加入其cell
                min=1 #选择一个丢包率最小的
                index=0
                for j in range(0,len(RU)):
                    t_loss=LossRate_FDS_RU(UES[i].host, RU[j].host)
                    if t_loss<=min:
                        min=t_loss
                        index=j
                print "in %d-th FD, %d-RU has been choosed,min loos:%f" %(t,index,t_loss)
                UES[i].link_e=t_loss
                #加入Fogcell
                if getDistance(UES[i].host,RU[index].host)<=D2DMax_dis:#D2D传输的最大距离
                    UES[i].cellnum=index
                    Fog_cell[index].append(UES[i])

        # print Fog_cell #打印出来的是各个__main__中各个UE实例的列表
        "在每一次Fogcell开始之前，打印各个设备的信息"
        # print "Before FogCell"
        # for i in range(0,DeviceNum):
        #     print UES[i].name,UES[i].locate,"power:",UES[i].Power,"cellnum:",UES[i].cellnum,"lossrate:",UES[i].link_e

        "对于每一个Fogcell单独进行调用，多线程并行进行"
        thrlist=[]
        for i in range(0,RUnum):
            t = threading.Thread(target=fogcell, args = (AP,Fog_cell[i],RU,i))
            thrlist.append(t)
            t.start()  #老是忘记
        for t in thrlist:
            t.join()
        print "After FogCell"
        for i in range(0,DeviceNum):
            print UES[i].name,UES[i].locate,"power:",UES[i].Power,"cellnum:",UES[i].cellnum,"lossrate:",UES[i].link_e
        
        #round +1之前移动设备和 设备持续时间
        online_device=[]
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

            
            #根据能量来决定是online还是offline
            temp_online=random.randint(0,100)
            if temp_online in range(0,100):
                UES[i].online=True
                online_device.append(UES[i].name)
            else:
                UES[i].online=False
        print "在线设备",online_device
        print "------------------------------------------------------"
        
        fair_result.append(Fairness(UES))
        round += 1
    
    "绘制每个设备的能量和效用变化图像"
    drawPowAndGain(UES,Total_r)
    "最后绘制所有设备的fairness变化"
    # print "fairness:",fair_result
    plt.figure()
    plt.xlabel('round')
    plt.ylabel('Fairness') 
    plt.ylim(0,1)
    data_x = [j for j in range(0,len(fair_result))]
    labelx = range(0,round+1)
    plt.xticks(data_x,labelx,fontsize=14)
    plt.plot(data_x,fair_result,marker = '*')
    plt.legend() #给图像加上图例
    plt.savefig("%s/FairResult.png"% path) #保存图片

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    #"创建网络拓扑，定义网络参数"
    DeviceNum=8 #FD总数量
    RUnum=1 #RU总数量
    Total_r=1  #进行轮数  
    topology(DeviceNum,RUnum,Total_r)


