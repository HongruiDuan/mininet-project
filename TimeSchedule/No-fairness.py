# -*- coding:utf-8 -*-
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
from EH.energy import energy
from Params.params import getDistance

import thread
import threading
import time
import json
import random
from NewGame import game

"线程函数"
def command(host, arg):
    result = host.cmd(arg)
    return result

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
'''
第一轮时初始化，在结束时将信息写入自己的缓存文件
如何更新信息

'''
class UE:
    count = 0
    def __init__(self, host, name, ip, port, link_e, gains=0.0, F_BS=0.0, F_UE=0.0, N1=0.0, b=0.0, Power = 50, rank=0, flag=False):
        self.host = host
        self.name = name
        self.ip = ip
        self.port = port
        self.link_e = link_e
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
    "ip位置只能有1位，因此20个设备需要分成两部分初始化"
    for i in range(1,21):
        #创建中继设备节点
        temphost = net.addStation('DU%d'%i, position='%d,5,0'%i, ip='10.0.0.%d'%i, mac='00:00:00:00:00:%02d'%i)
        #创建中继设备类对象
        temp = UE(temphost,'UE%d'%i,'10.0.0.%d'%i, 'DU%d-wlan0' %i,0.05+0.03*i) #丢包率已经初始化完毕
        UES.append(temp)
    
    #打印出设备池中的设备信息
    for i in range(0,20):
        print(UES[i].name,UES[i].ip,UES[i].port,'\n')
    


    #还没有解决send.py和receive.py的根据IP来确定文件名的想法
    # for i in range(10,21):
    #     #创建中继设备节点
    #     temphost = net.addStation('DU%d'%i, position='%d,5,0'%i, ip='10.0.1.%d'%(i-10), mac='00:00:00:00:00:%02d'%i)
    #     #创建中继设备类对象
    #     temp = UE(temphost,'UE%d'%i,'10.0.1.%d'%(i-10), 'DU%d-wlan0' %d,0.05+0.03*i)
    #     UES.append(temp)

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
    "总共进行10轮数据传输"
    Total_r = 10
    round = 0

    while round<Total_r:

        # info("***%d round AP collect info of UEs\n"% round)
        # try:
        #     thread.start_new_thread(command,(AP,"python RInfo.py 10.1.0.1 AP-wlan0"))
        #     print("python SInfo.py %s %s 10.1.0.1" % (UES[0].ip, UES[0].port))
        #     # print("python RInfo.py 10.1.0.1 AP-wlan0\n")
        #     thread.start_new_thread(command,(AP,"python RInfo.py 10.1.0.1 AP-wlan0"))
        #     for i in range(0,9):
        #         # print("python SInfo.py %s %s 10.1.0.1"%(UES[i].ip,UES[i].port))
        #         threading._start_new_thread(command,(UES[i].host,"python SInfo.py %s %s 10.1.0.1"%(UES[i].ip,UES[i].port)))   
        # except:
        #     print("%d round error\n" %round)
        # time.sleep(2.0 * UE.count) #根据中继设备的数量来确定等待时间
        # info("*** %d round info collect finish\n" % round)
        #统计完设备信息之后将信息从文件中读取
        #先采取直接对数据操作而不是真正的发送和接收包
        # filename1 = "/home/shlled/mininet-wifi/Log/BSLog.json"
        # with open(filename1,'r') as f1:
        #     buffer = f1.readlines()
        #     lenth = len(buffer)
        #     while lenth>0:
        #         temp = buffer[lenth-1]
        #         temp = json.loads(temp)
        #         # print(temp,"\n")
        #         #todo:如何确定所有的设备都已经接收完毕 

        #根据设备的丢包率来计算博弈结果，写入中继设备
        for i in range(0,20):
            result = game(UES[i].link_e)
            UES[i].F_BS = result[2]
            UES[i].F_UE = result[3]
            UES[i].N1 = result[0]
            UES[i].b = result[1]
        
        #根据设备能够达到的基站的效益对所有中继设备进行排序
        queue = sorted(UES, key = lambda UE: UE.F_BS, reverse=True)

        #打印中继设备的信息
        for i in range(0,20):
            print(queue[i].F_BS, queue[i].F_UE, queue[i].N1,'\n')
        
        
        
                
        round += 1

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()

