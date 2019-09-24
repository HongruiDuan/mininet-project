# -*- coding:utf-8 -*-
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
from EH.energy import energy
from Params.params import getDistance

import threading
import json
import random
from NewGame import game

"线程函数"
def command(host, arg):
    result = host.cmd(arg)
    return result
#设备类，存储设备的信息
'''
第一轮时初始化，在结束时将信息写入自己的缓存文件
如何更新信息
'''
class UE:
    count = 0
    def __init__(self,host,name,ip,link_e,gains=0.0,F_BS=0.0,F_UE=0.0,N1=0.0,b=0.0,rank=0):
        self.host = host
        self.name = name
        self.ip = ip
        self.link_e = link_e
        UE.count += 1
def topology():
    #创建网络和设备初始化
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       wmediumd_mode=interference)
    #设备初始化
    ap1 = net.addAccessPoint('ap1', ssid="ap1-ssid", mode="g",
                             channel="1", position='5,6,0',range=40)
    AP = net.addStation('AP', position='5,10,0', ip='10.0.0.0', mac='00:00:00:00:00:99') 
    
    UES = []
    for i in range(1,10):
        #创建中继设备节点
        temphost = net.addStation('DU%d'%i, position='%d,5,0'%i, ip='10.0.0.%d'%i, mac='00:00:00:00:00:%02d'%i)
        #创建中继设备类对象
        temp = UE(temphost,'UE%d'%i,'10.0.0.%d'%i,0.05+0.03*i)
        UES.append(temp)

    c0 = net.addController('c0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Adding Link\n")
    net.addLink(AP, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    for i in range(0,9):
        net.addLink(UES[i].host, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    
    info("*** Starting network ***\n")
    net.build()
    c0.start()
    ap1.start([c0])
    
    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()

