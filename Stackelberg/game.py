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
P_k = 0
b_k = 0

P_k_max = 10.0 # use for test
P_k_min = 1 # the min POW that guarantee the QOS of D2D
D = 36 # the improtance of every packet
W = 15.0  # BandWidth

a = 2.8 * (10e-11)

print(a)

R_k = 6.0
beta_k = 1.0
G_k = 10.0
c = 0.4
P_c = 24
G_c = 2.0
sigma = 1.0
alpha = a * W / log(2)

print(alpha)

g_k = (P_c * G_c + sigma **2) / G_k

b_k_min = alpha * D / (g_k + P_k_max)
b_k_max = alpha * D / (g_k + P_k_min)
b_k_star =  ( alpha * c * D / ( beta_k * g_k ) ) ** 0.5

P_k_star = ( alpha * D * beta_k * g_k / c) ** 0.5 -g_k

A_k = (alpha * D * beta_k /c) ** 0.5
print(A_k)

print(A_k **2 - 4*P_k_max)

x1 = ( (A_k + (A_k **2 - 4*P_k_max ) **0.5 )/ 2)  ** 2

x2 = ( (A_k - (A_k **2 - 4*P_k_max ) **0.5 )/ 2)  ** 2

x3 = ( (A_k + (A_k **2 - 4*P_k_min ) **0.5 )/ 2)  ** 2

x4 = ( (A_k + (A_k **2 - 4*P_k_max ) **0.5 )/ 2)  ** 2


if A_k **2 >= 4 * P_k_max:
    if g_k <= x3 or g_k >=x4:
        P_k = P_k_min
        b_k = b_k_max
    elif (g_k > x3 and g_k < x2) or (g_k > x1 and g_k < x4):
        
        b_k = b_k_star
        # P_k_star = alpha * D / b_k - g_k
        P_k = P_k_star

    else:
        P_k = P_k_max
        b_k = b_k_min
elif A_k **2 > 4 * P_k_min:
    if g_k <= x3 or g_k >= x4:
        P_k = P_k_min
        b_k = b_k_max
    else:
        
        b_k = b_k_star
        # P_k_star = alpha * D / b_k - g_k
        P_k = P_k_star
else:
    
    b_k = b_k_star
    # P_k_star = alpha * D / b_k - g_k
    P_k = P_k_star
result = []
result.append(P_k)
result.append(b_k)
print(result)
