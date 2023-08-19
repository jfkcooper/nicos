# align selene 2 guide vertical mirrors automatically
for group in range(7,16):
    print("Mirror group ", group)
    if group!=15:
        sm2.wait()
        maw(sm2, (1,group), sr2, (5,group))
        sm2.wait()
        sm2.measure()
        sm2.wait()
        corr = sm2.last_delta[0]
        if abs(corr)<0.7:
            sr2.adjust_position(corr)
        sm2.measure()
        maw(sr2, (6,group))
        sm2.wait()
        corr = sm2.last_delta[1]
        if abs(corr)<0.7:
            sr2.adjust_position(corr)
        sm2.measure()
        maw(sr2, (5,group))
        sm2.wait()
        corr = sm2.last_delta[0]
        if abs(corr)<0.7:
            sr2.adjust_position(corr)
    
        sm2.measure()
        sm2.wait()
        print('    result downstream:', sm2.last_delta)
    
    if group!=1:
        maw(sm2, (-1,group), sr2, (3,group))
        sm2.wait()
        sm2.measure()
        sm2.wait()
        corr = (sm2.last_delta[0]+sm2.last_delta[1])/2.
        if abs(corr)<0.7:
            sr2.adjust_position(corr)
        
        sm2.measure()
        sm2.wait()
        print('    result upstream:', sm2.last_delta)
        
    print(sm2.last_delta)
        