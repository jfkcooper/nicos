description = 'Static flippers'
group = 'lowlevel'
display_order = 22

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

#abslimits are defined in .res file!

devices = dict(
    sf_0a = device('nicos.devices.entangle.PowerSupply',
        description = 'Static flipper arm 0 - A',
        tangodevice = '%s/coil/sf_0a' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        #abslimits = (0, 5),
        precision = 0.01,
        unit = 'A',
    ),
    sf_0b = device('nicos.devices.entangle.PowerSupply',
        description = 'Static flipper arm 0 - B',
        tangodevice = '%s/coil/sf_0b' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        #abslimits = (0, 5),
        precision = 0.01,
        unit = 'A',
    ),
    sf_1 = device('nicos.devices.entangle.PowerSupply',
        description = 'Static flipper arm 1',
        tangodevice = '%s/coil/sf_1' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        #abslimits = (0, 5),
        precision = 0.01,
        unit = 'A',
    ),
    hsf_0a = device('nicos.devices.entangle.PowerSupply',
        description = 'Helmholtz mezei flipper arm 0 - A',
        tangodevice = '%s/coil/hsf_0a' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        #abslimits = (0, 5),
        precision = 0.01,
        unit = 'A',
    ),
    hsf_0b = device('nicos.devices.entangle.PowerSupply',
        description = 'Helmholtz mezei flipper arm 0 - B',
        tangodevice = '%s/coil/hsf_0b' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        #abslimits = (0, 5),
        precision = 0.01,
        unit = 'A',
    ),
    hsf_1 = device('nicos.devices.entangle.PowerSupply',
        description = 'Helmholtz mezei flipper arm 1',
        tangodevice = '%s/coil/hsf_1' % tango_base,
        fmtstr = '%.3f',
        tangotimeout = 5.0,
        pollinterval = 60,
        maxage = 120,
        #abslimits = (0, 5),
        precision = 0.01,
        unit = 'A',
    ),
)
