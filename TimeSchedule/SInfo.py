# -*-  coding:utf-8 -*-
from scapy.all import sniff, sendp
from scapy.all import Packet
from scapy.all import ShortField, IntField, LongField, BitField
from scapy.all import Ether, IP, ICMP

import time

import sys
import fire
import random

def send(src, iface, dst, times=15, send_pkt=[]):

    filename = '/home/shlled/mininet-project-duan/TimeSchedule/Log/UE%s.json' % src[7:8]
    f=open(filename,'r')
    buffer=f.readlines()
    lenth=len(buffer)
    time.sleep(1)
    #将最新的状态信息传递给AP
    alpha=buffer[lenth-1]
    msg = alpha
    send_pkt.append(msg)
    p = Ether() / IP(src=src, dst=dst) / ICMP() / msg
    #随机等待，以免AP接收时碰撞 
    t = random.randint(1,10)
    t = float(t) / 10.0
    time.sleep(t)
    sendp(p, iface = iface)
    f.close()
fire.Fire(send)
