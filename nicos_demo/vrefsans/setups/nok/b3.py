description = 'B3 aperture devices'

group = 'optional'

includes = ['aperture_last']

lprecision = 0.01

devices = dict(
    b3 = device('nicos_mlz.refsans.devices.nok_support.DoubleSlitSequence',
        description = 'b3 and h3 inside Samplechamber',
        fmtstr = '%.3f mm, %.3f mm',
        unit = '',
        nok_start = -1,
        nok_length = -1,
        nok_end = -1,
        nok_gap = -1,
        inclinationlimits = (-1000, 1000),
        masks = dict(
            slit = [84.044, 50.4169, 0.10, 16.565],
            pinhole = [84.044, 50.4169, 0.00, 45.22],
            gisans = [84.044, 50.4169, 0.00, 45.22],
        ),
        slit_r = 'b3r',
        slit_s = 'b3s',
        # nok_motor = [-1, -1],
    ),
    b3r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
       description = 'b3 slit, reactor side',
       lowlevel = True,
       motor = 'b3_r',
       nok_start = -1,
       nok_length =-1,
       nok_end = -1,
       nok_gap = -1,
       masks = {
           'slit': 36.32,
           'point': 36.32,
           'gisans': 36.32,
       },
       unit = 'mm',
    ),
    b3s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
       description = 'b3 slit, sample side',
       lowlevel = True,
       motor = 'b3_s',
       nok_start = -1,
       nok_length =-1,
       nok_end = -1,
       nok_gap = -1,
       masks = {
           'slit': 36.404,
           'point': 36.404,
           'gisans': 36.404,
       },
       unit = 'mm',
    ),
    b3_r = device('nicos.devices.generic.Axis',
        description = 'b3, reactorside',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-393.0, 330.0),
            speed = 1.,
        ),
        offset = 0.0,
        precision = lprecision,
        lowlevel = True,
    ),
    b3_s = device('nicos.devices.generic.Axis',
        description = 'b3, sampleside',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-102.0, 170.0),
            speed = 1.,
        ),
        offset = 0.0,
        precision = lprecision,
        lowlevel = True,
    ),
)

alias_config = {
    'last_slit': {'b3': 100},
}