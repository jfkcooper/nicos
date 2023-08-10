# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
from collections import namedtuple

import numpy as np

from nicos.core import Attach, CommunicationError, Override, Param, Readable, \
    limits, pvname, status, Waitable
from nicos.devices.epics import SEVERITY_TO_STATUS

from nicos_ess.devices.epics.base import EpicsReadableEss
from nicos_ess.devices.epics.extensions import HasDisablePv


class PilotLaser(HasDisablePv, EpicsReadableEss):
    parameters = {
        'uncertainty_fix':
            Param('Fixed contribution to uncertainty',
                  type=float,
                  settable=False,
                  volatile=True),
        'uncertainty_variable':
            Param('Uncertainty that depends on L', type=float, settable=False),
        'pvprefix':
            Param('Name of the record PV.',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  userparam=False),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    _record_fields = {
            'uncertainty_fix': 'LaserUncertFix-R',
            'uncertainty_variable': 'LaserUncertLDep-R',
            'connected': 'IsConnected-R',
        }

    def _get_pv_parameters(self):
        return HasDisablePv._get_pv_parameters(self) | set(
            self._record_fields.keys())

    def _get_pv_name(self, pvparam):
        record_prefix = getattr(self, 'pvprefix')
        field = self._record_fields.get(pvparam)
        if field is not None:
            return ':'.join((record_prefix, field))
        pvname = HasDisablePv._get_pv_name(self, pvparam)
        if pvname:
            return pvname
        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        general_epics_status, _ = self._get_mapped_epics_status()

        if general_epics_status == status.ERROR:
            return status.ERROR, 'Unknown problem in record'

        if not self._get_pv('connected'):
            return status.WARN, 'Disconnected'

        return status.OK, ''

    def doReadUncertainty_Fix(self):
        return self._get_pv('uncertainty_fix')

    def doReadUncertainty_Variable(self):
        return self._get_pv('uncertainty_variable')

    def doRead(self, maxage=0):
        if self._get_pv('connected'):
            return 'Ready'
        return 'Not Ready'


STAT_TO_STATUS = {
    0: '', # NO_ALARM
    1: 'READ_ALARM',
    2: 'WRITE_ALARM',
    3: 'HIHI_ALARM',
    4: 'HIGH_ALARM',
    5: 'LOLO_ALARM',
    6: 'LOW_ALARM',
    7: 'STATE_ALARM',
    8: 'COS_ALARM',
    9: 'COMM_ALARM',
    10:'TIMEOUT_ALARM',
    11:'HW_LIMIT_ALARM',
    12:'CALC_ALARM',
    13:'SCAN_ALARM',
    14:'LINK_ALARM',
    15:'SOFT_ALARM',
    16:'BAD_SUB_ALARM',
    17:'UDF_ALARM',
    18:'DISABLE_ALARM',
    19:'SIMM_ALARM',
    20:'READ_ACCESS_ALARM',
    21:'WRITE_ACCESS_ALARM',
}

class MultilineChannel(EpicsReadableEss):

    parameters = {
        'channel':
            Param('Channel number.',
                  type=int,
                  settable=False,
                  userparam=False,
                  internal=True),
        'i_limits':
            Param('Minimum intensity as raw value.',
                  type=limits,
                  settable=False,
                  internal=True),
        'gain':
            Param('Gain for the channel.',
                  type=float,
                  settable=False),
        'gain_pv':
            Param('PV for the gain.',
                  type=pvname,
                  settable=False,
                  mandatory=True,
                  userparam=False),
        'latest_valid':
            Param('Latest data of a valid measurement.',
                  type=float,
                  settable=False),
        'latest_valid_pv':
            Param('PV of latest data of a valid measurement.',
                  type=pvname,
                  settable=False,
                  mandatory=True,
                  userparam=False),
    }

    def _get_pv_parameters(self):
        return {'readpv', 'gain_pv'}

    def doPreinit(self, mode):
        self._raw = np.zeros(16)
        self._raw = list(map(float, self._raw.tolist()))
        EpicsReadableEss.doPreinit(self, mode)

    def _readRaw(self):
        raw = self._get_pv('readpv')
        raw = list(map(float, raw.tolist()))
        if len(raw) > 0:
            self._raw = raw
        else:
            raise CommunicationError(f'Can\'t read {self.readpv}')

    def doRead(self, maxage=0):
        self._readRaw()
        return self._raw[1]

    def doStatus(self, maxage=0):
        self._readRaw()
        epics_status = self._get_pvctrl('readpv', 'status', update=True)
        epics_severity = self._get_pvctrl('readpv', 'severity')
        readpv_status = SEVERITY_TO_STATUS.get(epics_severity, status.UNKNOWN)
        readpv_message=STAT_TO_STATUS.get(epics_status, 'Unkown status code %i'%epics_status)

        if int(self._raw[7]):
            return max(readpv_status, status.ERROR), 'Analysis error '+readpv_message
        elif int(self._raw[8]):
            return max(readpv_status, status.ERROR), 'Beam interruption '+readpv_message
        elif int(self._raw[9]):
            return max(readpv_status, status.ERROR), 'Temperature error '+readpv_message
        elif int(self._raw[10]):
            return max(readpv_status, status.ERROR), 'Movement tolerance error '+readpv_message
        elif int(self._raw[11]):
            return max(readpv_status, status.ERROR), 'Intensity error '+readpv_message
        elif int(self._raw[12]):
            return max(readpv_status, status.ERROR), 'USB connection error '+readpv_message
        elif int(self._raw[13]):
            return max(readpv_status, status.ERROR), 'Error setting the laser speed '+readpv_message
        elif int(self._raw[14]):
            return max(readpv_status, status.ERROR), 'Error laser temperature '+readpv_message
        elif int(self._raw[15]):
            return max(readpv_status, status.ERROR), 'DAQ error '+readpv_message
        else:
            highest_status = status.OK
            mapped_massages = []
            for name in self._pvs:
                epics_status = self._get_pvctrl(name, 'status', update=True)
                epics_severity = self._get_pvctrl(name, 'severity')

                mapped_status = SEVERITY_TO_STATUS.get(epics_severity, status.UNKNOWN)
                mapped_massages.append(
                        (mapped_status,
                        STAT_TO_STATUS.get(epics_status, 'Unkown status code %s'%epics_status),
                        name)
                        )

                highest_status = max(highest_status, mapped_status)
            if highest_status>status.OK:
                epics_message='PV error status: '+'|'.join([self._get_pv_name(mm[2])+':'+mm[1]
                                                            for mm in mapped_massages if mm[0]==highest_status])
            else:
                epics_message=''
            return (highest_status, epics_message)

    def doReadChannel(self):
        return self._raw[0]

    def doReadI_Limits(self):
        return self._raw[2], self._raw[3]

    def doReadGain(self):
        return self._get_pv('gain_pv')

    def doReadLatest_Valid(self):
        raw = self._get_pv('latest_valid_pv')
        return float(raw[1]) if raw else 0

    def doPoll(self, n, maxage=0):
        self.pollParams(volatile_only=False,
                        param_list=['i_limits', 'gain'])


EnvironmentalParameters = namedtuple('EnvironmentalParameters',
                                     ['temperature', 'pressure', 'humidity'])


class MultilineController(EpicsReadableEss, Waitable):

    parameters = {
        'pvprefix':
            Param('Name of the record PV.',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  userparam=False),
        'front_end_splitter':
            Param('Turn front end splitter on/off.',
                  type=str,
                  settable=True,
                  internal=True),
        'fes_option':
            Param('Turn the shutter on or off when not measuring.',
                  type=str,
                  settable=True,
                  internal=True),
        'single_measurement':
            Param('Start of a single measurement.',
                  type=str,
                  settable=True,
                  internal=True),
        'alignment_process':
            Param('Start/stop the process to align the '
                  'channels.',
                  type=str,
                  settable=True,
                  internal=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    attached_devices = {
        'pilot_laser': Attach('Pilot laser', PilotLaser),
        'humidity': Attach('Environmental humidity', Readable),
        'pressure': Attach('Environmental pressure', Readable),
        'temperature': Attach('Environmental temperature', Readable),
    }

    _record_fields = {
            # 'front_end_splitter': 'FrontEndSplitter-S',
            'fes_option': 'FESOption-S',
            'single_measurement': 'SingleMeasurement-S',
            # 'alignment_process': 'AlignmentProcess-S',
            'server_error': 'ServerErr-R',
            'num_channels': 'NumChannels-R',
            'is_grouped': 'IsGrouped-R'
        }

    _cache_relations = {
        'single_measurement': 'single_measurement',
    }


    def _get_pv_parameters(self):
        parameters = set(self._record_fields.keys())
        return parameters | {'readpv'}

    def _get_pv_name(self, pvparam):
        record_prefix = getattr(self, 'pvprefix')
        field = self._record_fields.get(pvparam)
        if field is not None:
            return ':'.join((record_prefix, field))
        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        epics_status = self._get_pvctrl('readpv', 'status', update=True)
        epics_severity = self._get_pvctrl('readpv', 'severity')
        readpv_status = SEVERITY_TO_STATUS.get(epics_severity, status.UNKNOWN)
        readpv_message=STAT_TO_STATUS.get(epics_status, 'Unkown status code %s'%epics_status)

        if self._get_pv('server_error'):
            return max(readpv_status, status.ERROR), 'Server error '+readpv_message
        mess_status = self.doReadSingle_Measurement()
        if mess_status in ['START', 'RUNNING']:
            return status.BUSY, 'Measuring'
        else:
            highest_status = status.OK
            mapped_massages = []
            for name in self._pvs:
                epics_status = self._get_pvctrl(name, 'status', update=True)
                epics_severity = self._get_pvctrl(name, 'severity')

                mapped_status = SEVERITY_TO_STATUS.get(epics_severity, status.UNKNOWN)
                mapped_massages.append(
                        (mapped_status,
                        STAT_TO_STATUS.get(epics_status, 'Unkown status code %s'%epics_status),
                        name)
                        )

                highest_status = max(highest_status, mapped_status)
            if highest_status>status.OK:
                epics_message='PV error status: '+'|'.join([self._get_pv_name(mm[2])+':'+mm[1]
                                                            for mm in mapped_massages if mm[0]==highest_status])
            else:
                epics_message=''
            return (highest_status, epics_message)

    def measure(self):
        self.doWriteSingle_Measurement(1)

    def doReadFront_End_Splitter(self):
        return self._get_pv('front_end_splitter', as_string=True)

    def doWriteFront_End_Splitter(self, value):
        self._put_pv('front_end_splitter', value, wait=True)

    def doReadFes_Option(self):
        return self._get_pv('fes_option', as_string=True)

    def doWriteFes_Option(self, value):
        self._put_pv('fes_option', value, wait=True)

    def doReadSingle_Measurement(self):
        return self._get_pv('single_measurement', as_string=True)

    def doWriteSingle_Measurement(self, value):
        self._put_pv('single_measurement', value, wait=True)

    def doReadAlignment_Process(self):
        return self._get_pv('alignment_process', as_string=True)

    def doWriteAlignment_Process(self, value):
        self._put_pv('alignment_process', value, wait=True)

    def doReadIs_Grouped(self):
        return self._get_pv('is_grouped', as_string=True)

    def doReadNum_Channels(self):
        return self._get_pv('num_channels')

    # def doPoll(self, n, maxage=0):
    #     self._pollParam('front_end_splitter')
    #     self._pollParam('fes_option')
    #     self._pollParam('single_measurement')
    #     self._pollParam('alignment_process')
    #     self._pollParam('num_channels')
    #     self._pollParam('is_grouped')

    @property
    def pilot(self):
        return self._attached_pilot_laser

    @property
    def env(self):
        return EnvironmentalParameters(
            self._attached_temperature.read(),
            self._attached_pressure.read(),
            self._attached_humidity.read(),
        )
