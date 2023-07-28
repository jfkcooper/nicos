start_mcart = 3150.
end_mcart = 3780.

import numpy as np
import yaml

upper_limits=yaml.safe_load(open('data_artur/upper_limits.yaml','r'))
driver1_1_adjust.userlimits=(-100000, 100000)
driver1_2_adjust.userlimits=(-100000, 100000)

REFERENCE_20230725_1 = [3508.8, 233.4]


def measure_wait():
    multiline.single_measurement=1
    sleep(1.)
    while multiline.doReadSingle_Measurement() in ['START', 'RUNNING']:
        sleep(0.1)


def scan_measure(axis, astart, aend, asteps, channels=[ch17, ch18, ch21, ch22, ch27, ch28]):
    with manualscan(axis, *channels):
        for i in range(asteps):
            try:
                axis.maw(astart+i/(asteps-1)*(aend-astart))
            except Exception as e:
                axis.warning("Error in positioning: %s"%e, exc_info=True)
            measure_wait()
            count(1)

{'HexScrewFullyOut': 0, 'HexScrewInTransition': 1, 'HexScrewInserted': 2, 'HexScrewMissed': 3, 'HexScrewCollided': 4, 'HexScrewIllegalState': 5}
    
def test_range(robot=1):
    if robot==2:
        adjust=driver1_2_adjust
    else:
        adjust=driver1_1_adjust
    try:
        adjust.maw(-4000)
    except Exception:
        pass
    low=adjust()
    for i in range(10):
        if adjust.status()[0]==240:
            adjust.reset()
            try:
                adjust.maw(0)
            except Exception:
                pass
    try:
        adjust.maw(4000)
    except Exception:
        pass
    high=adjust()
    for i in range(10):
        if adjust.status()[0]==240:
            adjust.reset()
            try:
                adjust.maw(-20)
            except Exception:
                pass
    adjust.maw(2.5)
    adjust.maw(0.0)
    return low, high

#upper_limits={}
def reference_all():
    global upper_limits
    # run through all screws to reference their center positoin, then check the available angular range forward
    for group in range(1, 16):
        if not group in upper_limits:
            upper_limits[group]={}
        for item in [1,2,3,4,5,6]:
            if item in upper_limits[group]:
                continue
            maw(sr1, (item, group))
            if item in [3,5,6]:
                # wedge mover have smaller range
                res=sr1.reference_screw(nrot0=7)
            else:
                res=sr1.reference_screw(nrot0=15)
            if res:
                sr1._engage()
                try:
                    sr1._adjust.maw(15000)
                except Exception as e:
                    pass
                upper_limits[group][item]=sr1._adjust()
                for i in range(5):
                    try:
                        sr1._adjust.reset()
                        sr1.adjust(0)
                    except Exception as e:
                        continue
                    else:
                        break

def drive_to_max():
    for group in range(1, 16):
        if not group in upper_limits:
            upper_limits[group]={}
        for item in [1,2,4]:
            if sr1._rotations[item][group]>1000:
                # skip already moved items
                continue
            max_angle=upper_limits[group][item]
            maw(sr1, (item, group))
            for i in range(1,10):
                try:
                    sr1.adjust(max_angle-i*90)
                except Exception as e:
                    sr1._adjust.reset()
                else:
                    break
    print("Done, don't forget to save the rotation positions before a restart")
            