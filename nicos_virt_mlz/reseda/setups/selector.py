description = 'setup for the velocity selector'
group = 'lowlevel'

devices = dict(
    selector_speed = device('nicos.devices.generic.VirtualMotor',
        description = 'Selector speed control',
        abslimits = (0, 28500),
        precision = 10,
        unit = 'rpm',
    ),
    selector_tilt = device('nicos.devices.generic.VirtualMotor',
        description = 'Selector tilt',
        abslimits = (-10, 10),
        precision = 0.1,
        unit = 'deg',
    ),
    selector_lambda = device('nicos_mlz.reseda.devices.SelectorLambda',
        description = 'Selector wavelength control',
        seldev = 'selector_speed',
        tiltdev = 'selcradle',
        unit = 'A',
        fmtstr = '%.2f',
        twistangle = 48.27,
        length = 0.25,
        # radius = 0.16,
        beamcenter = 0.115,
        maxspeed = 28500,
    ),
    selector_delta_lambda = device('nicos_mlz.reseda.devices.SelectorLambdaSpread',
        description = 'Selector wavelength spread',
        lamdev = 'selector_lambda',
        unit = '%',
        fmtstr = '%.1f',
        n_lamellae = 64,
        d_lamellae = 0.8,
        diameter = 0.32,
    ),
    selector_rtemp = device('nicos.devices.generic.ManualMove',
        description = 'Temperature of the selector rotor',
        unit = 'degC',
        fmtstr = '%.1f',
        abslimits = (5, 60),
        default = 30,
        warnlimits = (10, 45),
    ),
    selector_winlt = device('nicos.devices.generic.ManualMove',
        description = 'Cooling water temperature at inlet',
        unit = 'degC',
        fmtstr = '%.1f',
        abslimits = (5, 25),
        default = 16,
        warnlimits = (15, 20),
    ),
    selector_woutt = device('nicos.devices.generic.ManualMove',
        description = 'Cooling water temperature at outlet',
        unit = 'degC',
        fmtstr = '%.1f',
        abslimits = (10, 40),
        default = 18,
        warnlimits = (15, 20),
    ),
    selector_wflow = device('nicos.devices.generic.ManualMove',
        description = 'Cooling water flow rate through selector',
        unit = 'l/min',
        fmtstr = '%.1f',
        abslimits = (1, 12),
        default = 2,
        warnlimits = (1.5, 10),
    ),
    selector_vacuum = device('nicos.devices.generic.ManualMove',
        description = 'Vacuum in the selector',
        unit = 'mbar',
        fmtstr = '%.5f',
        abslimits = (0, 1030),
        default = 0.002,
        warnlimits = (0, 0.005),
    ),
    selector_vibrt = device('nicos.devices.generic.ManualMove',
        description = 'Selector vibration',
        unit = 'mm/s',
        fmtstr = '%.2f',
        abslimits = (0, 2),
        default = 0.001,
        warnlimits = (0, 1),
    ),
    selcradle_mot = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector rotation (motor)',
        abslimits = (-10, 10),
        fmtstr = '%.3f',
        unit = 'deg',
        visibility = (),
    ),
    selcradle = device('nicos.devices.generic.Axis',
        description = 'Selector rotation',
        motor = 'selcradle_mot',
        fmtstr = '%.3f',
        precision = 0.1,
    ),
)
