# -*- coding:utf-8 -*-

'''
绘制设备位置图像
@param UES:设备池
    此处单元测试转化为
    locate:[[1,2],[5,5],[7,8],...]
    devname:[1,6,8,...]
@param round:当前运行轮数
绘制出一张包含各个点位置坐标的图片，并且每个点上面包含每个设备的标签
'''
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os


def drawLocate(AP,RU,UES,round):
    path='Figures/'+str(datetime.date.today())
    plt.figure()
    x=[]
    y=[]
    devnum=[]
    count=0
    #添加AP
    x.append(AP.params['position'][0])
    y.append(AP.params['position'][1])
    devnum.append('AP')
    count+=1
    #添加RU
    for i in range(0,len(RU)):
        x.append(RU[i].locate[0])
        y.append(RU[i].locate[1])
        devnum.append(RU[i].name)
        count+=1
    #添加FD
    for i in range(0,len(UES)):
        if(UES[i].online):#只显示在线设备
            x.append(UES[i].locate[0])
            y.append(UES[i].locate[1])
            devnum.append(UES[i].name)
            count+=1
    plt.xlim(0,300)
    plt.ylim(0,300)
    plt.scatter(x,y,c='r')
    #给每个点打上设备编号标签
    for i in range(0,count):
        plt.annotate(devnum[i], (x[i], y[i]))
    plt.savefig("%s/round%d.png"% (path,round)) #保存图片
    plt.close()
    #最后保存图片
