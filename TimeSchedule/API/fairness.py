# -*- coding:utf-8 -*-

"传入所有中继设备的信息和选择的中继设备编号"

def Fairness(UES): 
    #计算当前状态的设备的公平状态

    U_total = 0
    U_link_s = 0     
    for i in range(0,len(UES)):
        U_total += UES[i].gains
        U_link_s += (1-UES[i].link_e)
    
    X=[]
    for i in range(0,len(UES)):
        Ui_overline = ((1-UES[i].link_e)/U_link_s)*U_total
        if UES[i].gains<=Ui_overline:
            X.append(UES[i].gains/Ui_overline)
        else:
            X.append(1.0)
        print "%d-th gains:%f  U_over:%f link_s:%f total_s:%f total gains:%f"%(
            UES[i].num, UES[i].gains, Ui_overline, 1-UES[i].link_e, U_link_s, U_total)
                
    sum_of_xi = 0
    for i in range(0,len(X)):
        sum_of_xi += X[i]

    sum_of_xi2 = 0
    for i in range(0,len(X)):
        sum_of_xi2 += X[i]**2
    fairness = (sum_of_xi)**2/(len(X)*sum_of_xi2)
    print "in calcaulte fairness of each",X,"fairness:",fairness
    
    # UES[x].fairness = fairness
    return fairness