from random import choice, randrange, seed

from nicos.core.status import statuses

description = 'Virtual TMR cooling system'
excludes = ['cooling']
group = 'optional'

seed()

devices = dict(
    mp01 = device('nicos.devices.generic.ManualSwitch',
        description = 'Virtual pump 1.',
        # visibility = ['metadata', 'namespace', 'devlist'],
        # loglevel = 'info',
        # fmtstr = '%.3f',
        # unit = '',
        # maxage = 12,
        # pollinterval = 5,
        # warnlimits = None,
        # fixed = 'reason',
        # fixedby = ('NICOS', 99),
        # requires = {},
        states = ['off', 'on'],
    ),
    mp02 = device('nicos.devices.generic.ManualSwitch',
        description = 'Virtual pump 2.',
        states = ['off', 'on'],
    ),
    mf01 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual mass flow rate sensor 1.',
        # visibility = ['metadata', 'namespace', 'devlist'],
        # loglevel = 'info',
        # fmtstr = '%.3f',
        unit = 'l/s',
        # maxage = 12,
        # pollinterval = 5,
        warnlimits = (250, 750),
        # fixed = 'reason',
        # fixedby = ('NICOS', 99),
        # requires = {},
        # userlimits = (),
        abslimits = (0, 1e3),
        default = randrange(0, 1e6) / 1e3,
    ),
    mf02 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual mass flow rate sensor 2.',
        unit = 'l/s',
        warnlimits = (250, 750),
        abslimits = (0, 1e3),
        default = randrange(0, 1e6) / 1e3,
    ),
    t01 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual temperature sensor 1.',
        unit = 'degC',
        warnlimits = (25, 75),
        abslimits = (0, 1e2),
        default = randrange(0, 1e5) / 1e3,
    ),
    t02 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual temperature sensor 2.',
        unit = 'degC',
        warnlimits = (25, 75),
        abslimits = (0, 1e2),
        default = randrange(0, 1e5) / 1e3,
    ),
    t03 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual temperature sensor 3.',
        unit = 'degC',
        warnlimits = (25, 75),
        abslimits = (0, 1e2),
        default = randrange(0, 1e5) / 1e3,
    ),
    t04 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual temperature sensor 4.',
        unit = 'degC',
        warnlimits = (25, 75),
        abslimits = (0, 1e2),
        default = randrange(0, 1e5) / 1e3,
    ),
    t05 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual temperature sensor 5.',
        unit = 'degC',
        warnlimits = (25, 75),
        abslimits = (0, 1e2),
        default = randrange(0, 1e5) / 1e3,
    ),
    p01 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual pressure sensor 1.',
        unit = 'mbar',
        warnlimits = (250, 750),
        abslimits = (0, 1e3),
        default = randrange(0, 1e6) / 1e3,
    ),
    p02 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual pressure sensor 2.',
        unit = 'mbar',
        warnlimits = (250, 750),
        abslimits = (0, 1e3),
        default = randrange(0, 1e6) / 1e3,
    ),
    p03 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual pressure sensor 3.',
        unit = 'mbar',
        warnlimits = (250, 750),
        abslimits = (0, 1e3),
        default = randrange(0, 1e6) / 1e3,
    ),
    p04 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual pressure sensor 4.',
        unit = 'mbar',
        warnlimits = (250, 750),
        abslimits = (0, 1e3),
        default = randrange(0, 1e6) / 1e3,
    ),
    p05 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual pressure sensor 5.',
        unit = 'mbar',
        warnlimits = (250, 750),
        abslimits = (0, 1e3),
        default = randrange(0, 1e6) / 1e3,
    ),
    sf01 = device('nicos.devices.generic.ManualMove',
        description = 'Virtual water level sensor 1.',
        unit = 'mm',
        warnlimits = (25, 75),
        abslimits = (0, 1e2),
        default = randrange(0, 1e5) / 1e3,
    ),
    hv01 = device('nicos.devices.generic.VirtualMotor',
        description = 'Virtual globe valve 1.',
        # visibility =,
        # fmtstr = '%.3f',
        unit = '%',
        # maxage = 12,
        # pollinterval = 5,
        # warnlimits = (),
        # fixed = 'reason',
        # fixedby = ('NICOS', 99),
        requires = dict(level='admin'),
        # userlimits = (),
        # precision = 0.1,
        # userlimits = (),
        abslimits = (0, 1e2),
        # offset = 0,
        speed = 2,
        # jitter = 0,
        curvalue = randrange(0, 1e5) / 1e3,
        curstatus = (choice(list(statuses)), ''),
        # ramp = 0,
    ),
    hv02 = device('nicos.devices.generic.VirtualMotor',
        description = 'Virtual globe valve 2.',
        unit = '%',
        requires = dict(level='admin'),
        abslimits = (0, 1e2),
        speed = 2,
        curvalue = randrange(0, 1e5) / 1e3,
        curstatus = (choice(list(statuses)), ''),
    ),
    hv03 = device('nicos.devices.generic.VirtualMotor',
        description = 'Virtual globe valve 3.',
        unit = '%',
        requires = dict(level='admin'),
        abslimits = (0, 1e2),
        speed = 2,
        curvalue = randrange(0, 1e5) / 1e3,
        curstatus = (choice(list(statuses)), ''),
    ),
    hv04 = device('nicos.devices.generic.VirtualMotor',
        description = 'Virtual globe valve 4.',
        unit = '%',
        requires = dict(level='admin'),
        abslimits = (0, 1e2),
        speed = 2,
        curvalue = randrange(0, 1e5) / 1e3,
        curstatus = (choice(list(statuses)), ''),
    ),
    hv05 = device('nicos.devices.generic.VirtualMotor',
        description = 'Virtual globe valve 5.',
        unit = '%',
        requires = dict(level='admin'),
        abslimits = (0, 1e2),
        speed = 2,
        curvalue = randrange(0, 1e5) / 1e3,
        curstatus = (choice(list(statuses)), ''),
    ),
    sc = device('nicos.devices.generic.ManualMove',
        description = 'Virtual electric conductance sensor.',
        unit = 'mS',
        warnlimits = (250, 750),
        abslimits = (0, 5e2),
        default = randrange(0, 5e5) / 1e3,
    ),
    sp = device('nicos.devices.generic.ManualMove',
        description = 'Virtual pH sensor.',
        unit = 'pH',
        warnlimits = (3, 11),
        abslimits = (0, 14),
        default = randrange(0, 14e3) / 1e3,
    ),
)
