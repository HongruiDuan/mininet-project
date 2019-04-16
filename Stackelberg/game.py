# -*- coding: utf8 -*-
import random
import numpy as np
from sympy import *
from math import log
'''
a_i :the price of per unit rate
R_k :the rate from k-th UE to Client that can be realized
b_k :the price that k-th UE demands
P_k :the Pow that BS buy from k-th UE device 
P_k_max: input params 
'''
P_k_max = 10.0 # use for test
P_k_min = 1 # the min POW that guarantee the QOS of D2D
D = 1.0 # the improtance of every packet
W = 10.0  # BandWidth
b_k = Symbol('b_k')
P_k = Symbol('P_k')

a = 10.0
R_k = 6.0
beta_k = 10.0
G_k = 10.0
c = 2.0
P_c = 2.0
G_c = 2.0
sigma = 1.0
alpha = a * W / log(2)
g_k = (P_c * G_c + sigma **2) / G_k
P_k_star = alpha * D / b_k - g_k
b_k_min = alpha * D / (g_k + P_k_max)
b_k_max = alpha * D / (g_k + P_k_min)
b_k_star =  ( alpha * c * D / ( beta_k * g_k ) ) ** 0.5

P_k_star = ( alpha * D * beta_k * g_k / c) ** 0.5 -g_k

A_k = (alpha * D * beta_k /c) ** 0.5

x1 = ( (A_k + (A_k **2 - 4*P_k_max ) **0.5 )/ 2)  ** 0.5

x2 = ( (A_k - (A_k **2 - 4*P_k_max ) **0.5 )/ 2)  ** 0.5

x3 = ( (A_k + (A_k **2 - 4*P_k_min ) **0.5 )/ 2)  ** 0.5

x4 = ( (A_k + (A_k **2 - 4*P_k_max ) **0.5 )/ 2)  ** 0.5


if A_k **2 >= 4 * P_k_max:
    if g_k <= x3 or g_k >=x4:
        pass
    elif (g_k > x3 and g_k < x2) or (g_k > x1 and g_k < x4):
        pass
    else:
        pass
elif A_k **2 > 4 * P_k_min:
    if g_k <= x3 or g_k >= x4:
        pass
    else:
        pass
else:
    pass
