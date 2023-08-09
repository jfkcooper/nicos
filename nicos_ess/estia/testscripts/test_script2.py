import numpy as np
import yaml

#upper_limits=yaml.safe_load(open('data_artur/upper_limits_2.yaml','r'))
    
upper_limits={}
def reference_all():
    global upper_limits
    # run through all screws to reference their center positoin, then check the available angular range forward
    for group in range(1, 16):
        if not group in upper_limits:
            upper_limits[group]={}
        for item in [1,2,3,4,5,6]:
            if item in upper_limits[group]:
                continue
            maw(sr2, (item, group))
            if item in sr2.vertical_screws:
                res=sr2.reference_screw(nrot0=15)
            else:
                # wedge mover have smaller range
                res=sr2.reference_screw(nrot0=7)
            if res:
                sr2._engage()
                try:
                    sr2._adjust.maw(15000)
                except Exception as e:
                    pass
                upper_limits[group][item]=sr2._adjust()
                for i in range(5):
                    try:
                        sr2._adjust.reset()
                        sr2.adjust(0)
                    except Exception as e:
                        continue
                    else:
                        break

