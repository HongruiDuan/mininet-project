# -*- coding:utf-8 -*-
import numpy as numpy
from sympy import  *
from math import log

'''
新的博弈模型，

'''
def game(S):

    C = 3 #RU对包的基本支付单价
    C_DU = 2 #DU传输一个包的成本
    C_BS = 1    #BS传输一个包的成本
    N = 32  #总包数
    a = 12  #满足因子
    e = 0.1  #丢包率
    # S = 1-e
    x = Symbol('x') 
    expr1 = C_BS + (1/log(a))*C*N*S/(a+S*x)
    expr2 = 1/x + C_DU
    N_1 = solve(expr1-expr2,x)
    lenth = len(N_1)
    N1 = round(N_1[0])
    b = 1/float(N1) + C_DU
    U_DU = N1 * (b-C_DU)
    for i in (0,lenth-1):
        t_N = round(N_1[i])
        t_b = 1/float(t_N)+C_DU
        t_U = t_N*(t_b-C_DU)
        if t_U> U_DU:
            U_DU = t_U
            N1 = t_N
            b = t_b
    U_BS = C*N*log(a,a+S*N1)-b*N1-(N-N1)*C_BS
    result = [N1,b,U_BS,U_DU]
    return result


