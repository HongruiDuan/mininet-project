


if __name__=="__main__":
    i=[1,2,3,4,5,6]
    del i[0]
    print len(i)
    res=[]
    res.append(i[0])
    print res
    for i in range(0,3):
        print i