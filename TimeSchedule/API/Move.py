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
from math import sin, cos, radians

#单功能函数实现
def move(locate,speed,direct):
    # 设备二位移动
    if direct > 360:
        while direct > 360:
            direct = direct - 360
    elif direct < 0:
        while direct < 0:
            direct = direct + 360
    angel = radians(direct)
    x = locate[0]
    y = locate[1]
    #  第一象限
    if 0.0 <= angel <= 90.0:
        x = x + speed * cos(angel)
        y = y + speed * sin(angel)
    #  第二象限
    if 90.0 < angel <= 180.0:
        x = x - speed * cos(angel)
        y = y + speed * sin(angel)
    #  第三象限
    if 180.0 < angel <= 270.0:
        x = x - speed * cos(angel)
        y = y - speed * sin(angel)
    #  第四象限
    if 270.0 < angel <= 360.0:
        x = x - speed * cos(angel)
        y = y + speed * sin(angel)
    x = int(x)
    y = int(y)
    return [x, y]

    return [x,y]


#功能单元测试
if __name__=='__main__':
    locate=[0,0]
    speed=10
    direct=180
    res=move(locate,speed,direct)
    print res


