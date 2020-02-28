# -*- coding:utf-8 -*-

'''
绘制设备的能量和效用变化图，并保存
@param UES:设备池
@param round:总运行轮数
@param
'''
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
def drawPowAndGain(UES,round):
    #按照时间创建图片目录
    #path='../Figures/'+str(datetime.date.today())
    path='Figures/'+str(datetime.date.today()) #在net.py中调用是相对于net.py的目录
    # os.mkdir(path) 只mk 一次在net中mk
    #对每一个设备的能量和效用绘制图像
    for i in range(0,len(UES)):   
        fig = plt.figure()
        #绘制能量变化图
        plt.subplot(211)
        plt.xlabel('round')
        plt.ylabel('Power(J) of %d-th FD'%UES[i].num) 
        data_x = [j for j in range(0,len(UES[i].powhis))]
        data_pow = UES[i].powhis
        labelx = range(0,round+1)
        plt.xticks(data_x,labelx,fontsize=14)
        plt.plot(data_x,data_pow,marker = '*',label='%d-th pow'%UES[i].num)
        plt.legend() #给图像加上图例
        #绘制效用变化图
        plt.subplot(212)
        plt.xlabel('round')
        plt.ylabel('Gain of %d-th FD'%UES[i].num) 
        data_x = [j for j in range(0,len(UES[i].gainhis))]
        data_gain = UES[i].gainhis
        labelx = range(0,round+1)
        plt.xticks(data_x,labelx,fontsize=14)
        plt.plot(data_x,data_gain,marker = '^',label='%d-th gain'%UES[i].num)

        plt.legend() #给图像加上图例
        plt.tight_layout() #解决重叠问题
        fig.savefig("%s/%d-th device.png"%(path,UES[i].num)) #保存图片
        plt.close()


if __name__=='__main__':
    fig = plt.figure()
    x=np.arange(0,100)
    #作图1
    plt.subplot(211)
    plt.xlabel('round')
    plt.plot(x, x**2)
    #作图2
    plt.subplot(212)
    plt.xlabel('fairness')
    plt.grid(color='r', linestyle='--', linewidth=1,alpha=0.3)
    plt.plot(x, -x)
    #保存图片
    plt.tight_layout() #解决重叠问题
    
    print datetime.datetime.today()
    path='../Figures/'+str(datetime.datetime.today())
    os.mkdir(path)
    fig.savefig("%s/test.png"%path)
