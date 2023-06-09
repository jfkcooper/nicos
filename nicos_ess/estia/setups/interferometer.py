description = 'Prototype interferometer measurement'

etalon_prefix = 'ESTIA-Sel1:Mech-GU-001'

devices = dict(
    pilot_laser=device(
        'nicos_ess.estia.devices.multiline.PilotLaser',
        description='Pilot laser',
        pvprefix=etalon_prefix,
        readpv=f'{etalon_prefix}:LaserReady-R',
        switchstates={
            'enable': 1,
            'disable': 0
        },
        switchpvs={
            'read': f'{etalon_prefix}:RedPilotLaser-S',
            'write': f'{etalon_prefix}:RedPilotLaser-S'
        },
        visibility=()
    ),
    # ih1=device(
    #     'nicos_ess.estia.devices.attocube.IDS3010Axis',
    #     axis=1,
    #     description='Horizontal IF axis top',
    #     readpv='ESTIA-ATTOCUBE-001:Axis1:Displacement_RBV',
    #     pvprefix='ESTIA-ATTOCUBE-001'
    # ),
    # ih2=device(
    #     'nicos_ess.estia.devices.attocube.IDS3010Axis',
    #     axis=2,
    #     description='Horizontal IF axis bottom',
    #     readpv='ESTIA-ATTOCUBE-001:Axis2:Displacement_RBV',
    #     pvprefix='ESTIA-ATTOCUBE-001'
    # ),
    # ih3=device(
    #     'nicos_ess.estia.devices.attocube.IDS3010Axis',
    #     axis=3,
    #     description='Cart position top',
    #     readpv='ESTIA-ATTOCUBE-001:Axis3:Displacement_RBV',
    #     pvprefix='ESTIA-ATTOCUBE-001'
    # ),
    # dhtop=device(
    #     'nicos_ess.estia.devices.attocube.MirrorDistance',
    #     axis='ih1',
    #     description='Horizontal distance top',
    # ),
    # dhbottom=device(
    #     'nicos_ess.estia.devices.attocube.MirrorDistance',
    #     axis='ih2',
    #     description='Horizontal distance bottom',
    # ),
    env_humidity=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Environmental humidity',
        readpv=f'{etalon_prefix}:EnvDataHum-R',
        visibility=(),
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    env_pressure=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Environmental pressure',
        readpv=f'{etalon_prefix}:EnvDataPress-R',
        visibility=(),
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    env_temperature=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Environmental temperature',
        readpv=f'{etalon_prefix}:EnvDataTemp-R',
        visibility=(),
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    temp_1=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='First temperature sensor',
        readpv=f'{etalon_prefix}:TempSensorS1-R'
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    temp_2=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Second temperature sensor',
        readpv=f'{etalon_prefix}:TempSensorS2-R'
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    temp_3=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Third temperature sensor',
        readpv=f'{etalon_prefix}:TempSensorS3-R'
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    temp_4=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Fourth emperature sensor',
        readpv=f'{etalon_prefix}:TempSensorS4-R'
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    multiline=device(
        'nicos_ess.estia.devices.multiline.MultilineController',
        description='Multiline interferometer controller',
        pvprefix=etalon_prefix,
        readpv=f'{etalon_prefix}:SelectedChannels-R',
        pilot_laser='pilot_laser',
        temperature='env_temperature',
        pressure='env_pressure',
        humidity='env_humidity'
    ),
)

channels = [17, 18, 19, 20, 21, 22, 23, 24, 27, 28]

for ch in channels:
    devices[f'ch{ch:02}'] = device(
        'nicos_ess.estia.devices.multiline.MultilineChannel',
        description=f'Value of channel {ch}',
        readpv=f'{etalon_prefix}:Ch{ch}DataLength-R',
        latest_valid_pv=f'{etalon_prefix}:Ch{ch}DataLenValid-R',
        gain_pv=f'{etalon_prefix}:Ch{ch}Gain-R',
        unit='mm',
    )
