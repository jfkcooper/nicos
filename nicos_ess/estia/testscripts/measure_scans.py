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
except:
    pass

s2dv1 = DifferenceChannel(name='s2dv1', unit='mm', index=0)
s2dv2 = DifferenceChannel(name='s2dv2', unit='mm', index=1)

with manualscan(sr2._adjust, ch17, ch18, s2dv1, s2dv2):
    for i in range(-50, 51):
        sr2.adjust(i*36)
        sm2.measure()
        sm2.wait()
        count(t=1)
