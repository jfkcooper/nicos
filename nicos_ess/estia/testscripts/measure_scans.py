from nicos.core.device import Readable
from nicos.core.params import Param


class DifferenceChannel(Readable):
    parameters = {
        'index':       Param('Channel index to retrieve', type=int,
                              default=0, settable=True),
    }
    
    def doRead(self, maxage=0):
        return sm2.last_delta[self.index]

try:
    RemoveDevice('s2dv1')
    RemoveDevice('s2dv2')
    RemoveDevice('s2dh1')
    RemoveDevice('s2dh2')
except:
    pass

s2dv1 = DifferenceChannel(name='s2dv1', unit='mm', index=0)
s2dv2 = DifferenceChannel(name='s2dv2', unit='mm', index=1)
s2dh1 = DifferenceChannel(name='s2dh1', unit='mm', index=2)
s2dh2 = DifferenceChannel(name='s2dh2', unit='mm', index=3)

with manualscan(mcart2, ch17, ch18, ch19, ch20, ch21, ch22, ch23, ch24, s2dv1, s2dv2, s2dh1, s2dh2):
    sm2.move( (1, 1))
    mcart2.wait()
    sm2.wait()
    sm2.measure()
    sm2.wait()
    count(t=1)
    
    for group in range(2, 15):
        for screw in [-1, 1]:
            sm2.move( (screw, group))
            mcart2.wait()
            sm2.wait()
            sm2.measure()
            sm2.wait()
            count(t=1)

    sm2.move( (-1, 15))
    mcart2.wait()
    sm2.wait()
    sm2.measure()
    sm2.wait()
    count(t=1)
    