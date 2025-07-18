description = 'system setup'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

sysconfig = dict(
    cache = 'localhost',
    instrument = 'xresd',
    experiment = 'Exp',
    datasinks = [
        'conssink',
        'filesink',
        'daemonsink',
        'livesink',
        'rabbitsink',
    ],
    notifiers = [],  # ['email'],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
]

devices = dict(
    xresd = device('nicos.devices.instrument.Instrument',
        description = 'X-ray Residual Stress Diffractometer',
        instrument = 'XReSD',
        responsible = 'Bastian Veltel <bastian.veltel@frm2.tum.de>',
        website = 'https://mlz-garching.de/physics-lab',
        operators = ['MLZ'],
        facility = 'mlz',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = True,
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos_mlz.labs.physlab.xresd.datasinks.LiveViewSink'),
    rabbitsink = device('nicos_mlz.devices.rabbit_sink.RabbitSink',
        rabbit_url = 'amqp://localhost',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/data',
        warnlimits = (5., None),
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/control/log',
        warnlimits = (.5, None),
        minfree = 0.5,
        visibility = (),
    ),
)
