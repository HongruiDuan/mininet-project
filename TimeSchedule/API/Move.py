# -*- coding:utf-8 -*-
'''
    设备二维移动
    @param:locate [x,y] 二维坐标
    @param:speed  int 速度大小
    @param:direct int 0-360 以自身为原点速度方向 
        分成四个象限分别对应  
        如 direct = 135(度)
        x=x-speed*sin(direct) 
        y=y+speed*sin(direct)
        
    返回新的坐标 [x,y]
    注意计算结果为小数，最后的返回值要求为int型
'''
#单功能函数实现
def move():


    return [x,y]


#功能单元测试
if __name__=='__main__':
    locate=[0,0]
    speed=10
    direct=135
    res=move(locate,speed,direct)
    print res


