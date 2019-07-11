# -*- coding:utf-8 -*-
'''
先采用1秒模拟1ms，所有文件sleep 1s 避免线程之间错乱
'''

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


def topology():
    "Create a network."
    net = Mininet_wifi(controller=Controller, link=wmediumd,
                       wmediumd_mode=interference)

    info("*** Creating nodes\n")
    ap1 = net.addAccessPoint('ap1', ssid="ap1-ssid", mode="g",
                             channel="1", position='5,6,0',range=40)
    info("*** Creating nodes\n")
    AP = net.addStation('AP', position='5,10,0', ip='10.0.0.0', mac='00:00:00:00:00:01')

    UE1 = net.addStation('UE1', position='30,5,0', ip='10.0.0.1', mac='00:00:00:00:00:02')#第一轮的接收方

    UE2 = net.addStation('UE2', position='15,15,0', ip='10.0.0.2', mac='00:00:00:00:00:03')#第一轮的中继
    UE3 = net.addStation('UE3', position='15,15,0', ip='10.0.0.3', mac='00:00:00:00:00:04')
    UE4 = net.addStation('UE4', position='15,15,0', ip='10.0.0.4', mac='00:00:00:00:00:05')
    # UE5 = net.addStation('UE5', position='15,15,0', ip='10.0.0.6', mac='00:00:00:00:00:06')

    c0 = net.addController('c0')

    net.setPropagationModel(model="logDistance", exp=5)
    
    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Adding Link\n")
    net.addLink(AP, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    net.addLink(UE1, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    net.addLink(UE2, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    net.addLink(UE3, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    net.addLink(UE4, cls=adhoc, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')
    #划分时间线来确定每一时隙需要完成的任务
    timeline = 0

    info("*** Starting network ***\n")
    net.build()
    c0.start()
    ap1.start([c0])
# -----------------------------AP收集信息与DU博弈阶段---------------------------    
    #AP收集DU信息
    # print("AP收集DU信息")
    info("*** AP collect information from DU ***\n")
   
    tc1 = threading.Thread(target=command, args=(AP,"python RInfo.py 10.0.0.0 AP-wlan0"))
    tc1.start()
    tc2 = threading.Thread(target=command, args=(UE2,"python SInfo.py 10.0.0.2 UE2-wlan0 10.0.0.0"))
    tc2.start()
    tc3 = threading.Thread(target=command, args=(UE3,"python SInfo.py 10.0.0.3 UE3-wlan0 10.0.0.0"))    
    tc3.start()
    tc4 = threading.Thread(target=command, args=(UE4,"python SInfo.py 10.0.0.4 UE4-wlan0 10.0.0.0"))
    tc4.start()

    tc2.join()
    tc3.join()
    tc4.join()
    tc1.join()#AP接收线程最长 
    print("first cycle finish")
    #AP创建中继状态信息字典   (这一段写得没啥扩展性，思考一下如何提升可扩展性)
    BSLog = {
        "UE1":{},
        "UE2":{},
        "UE3":{},
        "UE4":{}
    }
    BSLog["UE1"]["flag"] = False
    BSLog["UE2"]["flag"] = False
    BSLog["UE3"]["flag"] = False
    BSLog["UE4"]["flag"] = False
    filename1 = "/home/shlled/mininet-project-duan/TimeSchedule/Log/BSLog.json"
    with open(filename1,'r+') as f1:
        buffer = f1.readlines()
        lenth = len(buffer)
        while lenth>0:
            temp=buffer[lenth-1]
            temp=json.loads(temp)
            if temp[0]["UEIP"] == "10.0.0.1" and BSLog["UE1"]["flag"] == False:
                BSLog["UE1"]["flag"] = True
                BSLog["UE1"]["IP"] = temp[0]["UEIP"]
                BSLog["UE1"]["POWER"] = temp[0]["UEPOWER"]
                BSLog["UE1"]["Integrity"] = temp[0]["Integrity"] #这个链路状态如何设定
                BSLog["UE1"]["MAX"] = temp[0]["UEMAX"]
            elif temp[0]["UEIP"] == "10.0.0.2" and BSLog["UE2"]["flag"] == False:
                BSLog["UE2"]["flag"] = True
                BSLog["UE2"]["IP"] = temp[0]["UEIP"]
                BSLog["UE2"]["POWER"] = temp[0]["UEPOWER"]
                BSLog["UE2"]["Integrity"] = temp[0]["Integrity"]
                BSLog["UE2"]["MAX"] = temp[0]["UEMAX"]
            elif temp[0]["UEIP"] == "10.0.0.3" and BSLog["UE3"]["flag"] == False:
                BSLog["UE3"]["flag"] = True
                BSLog["UE3"]["IP"] = temp[0]["UEIP"]
                BSLog["UE3"]["POWER"] = temp[0]["UEPOWER"]
                BSLog["UE3"]["Integrity"] = temp[0]["Integrity"]
                BSLog["UE3"]["MAX"] = temp[0]["UEMAX"]
            elif temp[0]["UEIP"] == "10.0.0.4" and BSLog["UE4"]["flag"] == False:
                BSLog["UE4"]["flag"] = True
                BSLog["UE4"]["IP"] = temp[0]["UEIP"]
                BSLog["UE4"]["POWER"] = temp[0]["UEPOWER"]
                BSLog["UE4"]["Integrity"] = temp[0]["Integrity"]
                BSLog["UE4"]["MAX"] = temp[0]["UEMAX"]
            lenth -= 1
            if BSLog["UE1"]["flag"] == True and BSLog["UE2"]["flag"] == True and BSLog["UE3"]["flag"]==True and BSLog["UE4"]["flag"] == True:
               break
    print(BSLog)
    #在收集好各个设备的信息后进行博弈，然后将中继设备排成优先级队列
    Balance = []
    for i in range(2,4):
        #统计每一个中继设备的链路状态，并计算博弈均衡时的策略
        print("UE%d" % i)
        result = game(BSLog["UE%d" % i]["Integrity"]) #博弈函数，传入参数为上一轮的完整性因子 ,完整性因子 与丢包率之间的关系？？？？
        BSLog["UE%d" % i]["P_k"] = result[0]#将返回结果写入字典
        BSLog["UE%d" % i]["b_k"] = result[1]
        BSLog["UE%d" % i]["F_BS"] = result[2]
        BSLog["UE%d" % i]["F_UE"] = result[3]
        Balance.append(BSLog["UE%d" % i])
    Balance = sorted(Balance,key = lambda x:x['F_BS'],reverse = True)#将中继设备按照基站收益排序
    print(Balance)
    "确定用哪个中继设备来进行传输"
    index = 0 
    K = len(Balance)
    while index < K:
        Power = Balance[index]["POWER"]
        Pow = Balance[index]["P_k"]
        if Power > Pow:
            UEIP = Balance[index]["IP"]
            break
        index += 1
    if UEIP == '10.0.0.1':
        host = UE1
        hostip = '10.0.0.1'
        hostname = 'UE1'
        P_k = Balance[0]["P_k"]
        F_UE = Balance[0]["F_UE"]
    elif UEIP == '10.0.0.2':
        host = UE2
        hostip = '10.0.0.2'
        hostname = 'UE2'
        P_k = Balance[0]["P_k"]
        F_UE = Balance[0]["F_UE"]
    elif UEIP == '10.0.0.3':
        host = UE3
        hostip = '10.0.0.3'
        hostname = 'UE3'
        P_k = Balance[0]["P_k"]
        F_UE = Balance[0]["F_UE"]
    elif UEIP == '10.0.0.4':
        host = UE4
        hostip = '10.0.0.4'
        hostname = 'UE4'
        P_k = Balance[0]["P_k"]
        F_UE = Balance[0]["F_UE"]
    else :
        "基站的功率和收益怎么计算还没想好"
        host = AP
        hostip = '10.0.0.0'
        hostname = 'AP'
        P_k = 0
        F_UE = 0
    print("best choice:",hostname)

    #在给UE1发送信息之前先清空UE1的缓存文件
    filename1 = '/home/shlled/mininet-project-duan/TimeSchedule/Log/2.txt'
    with open(filename1,'r+') as f1:
        f1.truncate()

# ------------------------------AP、DU、RU收发信息阶段------------------------------------------------
    info("***AP start broadcasting ***\n")
    #DU,RU 随机接收信息还是接收能量
    '''
    约束条件
    1.DU接收到的有效信息量比RU多博弈决策的N1
    2.DU的能量要能够保障在后一阶段能够发送足够的数据包
    
    计算出时隙比值来设置概率
    e1=0.4 e2=0.1
    '''
    p1 = 0.2 #DU1接收到但是RU没有接收到的概率，先设置为定值后再考虑与丢包率的关系，设置合理的丢包率
    p2 = 0.3 #DU2
    TotalTime = 10#时间片大小
    FileIndex = 0 #发送文件位置
    dst = ['10.0.0.2','10.0.0.3','10.0.0.4']
    for i in range(0,TotalTime):  #有100个最小时隙，AP广播100轮，DU选择接收能量和信息，RU直接接收信息  
        "此处AP应该改成广播，APsned 的 dst应该不止一个"  
        t1 = threading.Thread(target=command, args = (AP,"python APBroadCast.py 10.0.0.0 AP-wlan0 '%s' %s" %(dst,FileIndex)))#AP广播一个数据包
        t2 = threading.Thread(target=command, args = (UE1,"python Receive.py 10.0.0.1 UE1-wlan0 0.5"))
        top1 = int(100-100*p1)
        key1 = random.randint(1,100)
        "中继设备随机接收信息或者能量"
        if key1 in range(1,top1):
            info("UE2 infomation\n")
            t3 = threading.Thread(target = command,args = (UE2,"python Receive.py 10.0.0.2 UE2-wlan0 0.1"))
        else:
            info("UE2 energy\n")
            t3 = threading.Thread(target = energy,args = (UE2,AP,1))
        t3.start()

        top2 = int(100-100*p2)
        key2 = random.randint(1,100)

        if key2 in range(1,top2):
            info("UE3 infomation\n")
            t4 = threading.Thread(target=command,args=(UE3,"python Receive.py 10.0.0.3 UE3-wlan0 0.2"))
        else:
            info("UE3 energy\n")
            t4 = threading.Thread(target = energy,args = (UE3,AP,1) )
        t4.start()
        #先开始监听进程再开始发送进程
        t2.start()
        t1.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        FileIndex += 1 
    
    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
