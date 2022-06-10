description = 'Setup for the ANDOR CCD camera at CAMEA using the CCDWWW server'

counterprefix = 'SQ:CAMEA:counter'
pvprefix = 'SQ:CAMEA:counter'

excludes = ['detector','hm_config']


devices = dict(
    nxsink=device('nicos.nexus.nexussink.NexusSink',
                  description='Sink for NeXus file writer',
                  filenametemplate=['camea%(year)sn%(scancounter)06d.hdf'],
                  templateclass='nicos_sinq.camea.nexus.nexus_templates'
                                '.CameaCCDTemplateProvider',
                  ),
    el737_preset = device('nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = f'{counterprefix}.TP',
        presetpv = f'{counterprefix}.TP',
    ),
    timepreset=device(
        'nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        description='Used to set and view time preset',
        unit='sec',
        readpv=pvprefix + '.TP',
        presetpv=pvprefix + '.TP',
        ),
    elapsedtime=device(
        'nicos_ess.devices.epics.detector.EpicsTimerPassiveChannel',
        description='Used to view elapsed time while counting',
        unit='sec',
        readpv=pvprefix + '.T',
        ),
    monitorpreset=device(
        'nicos_ess.devices.epics.detector.EpicsCounterActiveChannel',
        description='Used to set and view monitor preset',
        type='monitor',
        readpv=pvprefix + '.PR2',
        presetpv=pvprefix + '.PR2',
        ),
    monitor1=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        description='First scalar counter channel',
        type='monitor',
        readpv=pvprefix + '.S2',
        ),
    monitor2=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        description='Second scalar counter channel',
        type='monitor',
        readpv=pvprefix + '.S3',
        ),
    monitor3=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        description='Third scalar counter channel',
        type='monitor',
        visibility=(),
        readpv=pvprefix + '.S4',
        ),
    monitor4=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        description='Fourth scalar counter channel',
        type='monitor',
        visibility=(),
        readpv=pvprefix + '.S5',
        ),
    protoncount=device(
        'nicos_ess.devices.epics.detector.EpicsCounterPassiveChannel',
        description='Fourth scalar counter channel',
        type='monitor',
        readpv=pvprefix + '.S5',
        ),
    ccdwww_connector = device('nicos_sinq.boa.devices.ccdwww.CCDWWWConnector',
        description = 'Connector for CCDWWW',
        baseurl = 'http://mpc2704:8080/ccd',
        base64auth = 'xxx',
        byteorder = 'big',
        comdelay = 1.,
        comtries = 5,
    ),
    ccdwww = device('nicos_sinq.boa.devices.ccdwww.AndorCCD',
        description = 'CCDWWW image channel',
        iscontroller = True,
        connector = 'ccdwww_connector',
        shape = (1024, 1024),
        pollinterval = 30,
        maxage = 30,
    ),
    ccd_cooler = device('nicos_sinq.boa.devices.ccdwww.CCDCooler',
        description = 'CCD sensor cooler',
        connector = 'ccdwww_connector',
        unit = 'state',
        pollinterval = 30,
        maxage = 30,
        fmtstr = '%s'
    ),
    cooler_temperature = device('nicos.devices.generic.paramdev.ReadonlyParamDevice',
        description = 'Actual temperature reading',
        device = 'ccd_cooler',
        parameter = 'temperature',
    ),
    andorccd = device('nicos.devices.generic.detector.Detector',
        description = 'Dummy detector to encapsulate ccdwww',
        monitors = [
            'ccdwww',
        ],
        timers = [
            'ccdwww',
        ],
        images = [
            'ccdwww',
        ],
        visibility = (),
    ),
    el737 = device('nicos_sinq.devices.detector.SinqDetector',
        description = 'EL737 counter box that counts neutrons and '
        'starts streaming events',
        startpv =    f'{counterprefix}.CNT',
        pausepv =    f'{counterprefix}:Pause',
        statuspv =   f'{counterprefix}:Status',
        errormsgpv = f'{counterprefix}:MsgTxt',
        monitorpreset = [
            'monitorpreset',
        ],
        timepreset = ['el737_preset'],
        thresholdpv = f'{counterprefix}:Threshold',
        thresholdcounterpv = f'{counterprefix}:ThresholdCounter',
    ),
    cameacontrol = device('nicos_sinq.boa.devices.ccdcontrol.BoaControlDetector',
        description = 'CAMEA CCD control',
        trigger = 'el737',
        followers = ['andorccd'],
        liveinterval = 5,
        minimum_rate = 0,
        rate_monitor = 'monitor1',
        elapsed_time = 'elapsedtime'
    ),
    cter1 = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        description = 'Direct connection to counter box',
        commandpv = 'SQ:CAMEA:cter1' + '.AOUT',
        replypv = 'SQ:CAMEA:cter1' + '.AINP',
    ),
)

startupcode = '''
SetDetectors(cameacontrol)
'''