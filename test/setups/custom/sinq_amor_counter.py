description = 'Neutron counter box and channels in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:counter'

devices = dict(
    timepreset = device('nicos_sinq.devices.epics.extensions.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = pvprefix + '.TP',
        presetpv = pvprefix + '.TP',
    ),
    elapsedtime = device('nicos_sinq.devices.epics.extensions.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = pvprefix + '.T',
    ),
    countpreset = device('nicos_sinq.devices.epics.extensions.EpicsCounterActiveChannel',
        description = 'Used to set and view count preset',
        type = 'counter',
        readpv = pvprefix + '.PR2',
        presetpv = pvprefix + '.PR2',
    ),
    c1 = device('nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        description = 'First scalar counter channel',
        type = 'counter',
        readpv = pvprefix + '.S2',
    ),
    c2 = device('nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        description = 'Second scalar counter channel',
        type = 'counter',
        readpv = pvprefix + '.S3',
    ),
    c3 = device('nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        description = 'Third scalar counter channel',
        type = 'counter',
        readpv = pvprefix + '.S4',
    ),
    c4 = device('nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        description = 'Fourth scalar counter channel',
        type = 'counter',
        readpv = pvprefix + '.S5',
    ),
    c5 = device('nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        description = 'Fifth scalar counter channel',
        type = 'counter',
        readpv = pvprefix + '.S6',
    ),
    c6 = device('nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        description = 'Sixth scalar counter channel',
        type = 'counter',
        readpv = pvprefix + '.S7',
    ),
    c7 = device('nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        description = 'Seventh scalar counter channel',
        type = 'counter',
        readpv = pvprefix + '.S8',
    ),
    c8 = device('nicos_sinq.devices.epics.extensions.EpicsCounterPassiveChannel',
        description = 'Eighth scalar counter channel',
        type = 'counter',
        readpv = pvprefix + '.S9',
    ),
    psd_tof = device('nicos_sinq.devices.epics.scaler_record.EpicsScalerRecord',
        description = 'EL737 counter box that counts neutrons and starts streaming events',
        startpv = pvprefix + '.CNT',
        pausepv = pvprefix + ':Pause',
        statuspv = pvprefix + ':Status',
        errormsgpv = pvprefix + ':MsgTxt',
        timers = ['timepreset', 'elapsedtime'],
        counters = [
            'countpreset', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8'
        ],
    ),
    cter1 = device('nicos_sinq.devices.epics.extensions.EpicsAsynController',
        description = 'Controller of the counter box',
        commandpv = 'SQ:AMOR:cter1.AOUT',
        replypv = 'SQ:AMOR:cter1.AINP',
    ),
)
