description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='Fluco',
    experiment='Exp',
    datasinks=['conssink', 'filesink', 'daemonsink',],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands.epics']

devices = dict(
    Fluco=device('nicos.devices.instrument.Instrument',
             description='instrument object',
             instrument='Fluco',
             responsible='S. Body <some.body@ess.eu>',
             ),

    Sample=device('nicos.devices.sample.Sample',
                  description='The currently used sample',
                  ),

    Exp=device('nicos.devices.experiment.Experiment',
               description='experiment object',
               dataroot='/opt/nicos-data',
               sendmail=True,
               serviceexp='p0',
               sample='Sample',
               ),

    filesink=device('nicos.devices.datasinks.AsciiScanfileSink',
                    ),

    conssink=device('nicos.devices.datasinks.ConsoleScanSink',
                    ),

    daemonsink=device('nicos.devices.datasinks.DaemonSink',
                      ),

    Space=device('nicos.devices.generic.FreeSpace',
                 description='The amount of free space for storing data',
                 path=None,
                 minfree=5,
                 ),
)
