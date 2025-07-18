description = 'BOA Table 4'

pvprefix = 'SQ:BOA:mcu1:'

devices = dict(
    t4tx = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Table 4 X Translation',
        motorpv = pvprefix + 'T4TX',
        errormsgpv = pvprefix + 'T4TX-MsgTxt',
        precision = 0.05,
        can_disable = True,
    ),
    t4ty = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Table 4 Y Translation',
        motorpv = pvprefix + 'T4TY',
        errormsgpv = pvprefix + 'T4TY-MsgTxt',
        precision = 0.05,
        can_disable = True,
    ),
    Table4 = device('nicos_sinq.boa.devices.boatable.BoaTable',
        description = 'Table 4',
        standard_devices = ['t4tx', 't4ty']
    ),
)
