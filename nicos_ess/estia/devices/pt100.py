#  -*- coding: utf-8 -*-
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
from nicos.core import Param, pvname, status
from nicos.devices.epics import SEVERITY_TO_STATUS

from nicos_ess.devices.epics.base import EpicsReadableEss

error_bits = {
    'underrange': 0x1,
    'overrange': 0x2,
    'limit1 overshot': 0x4,
    'limit1 undershot': 0x8,
    'limit2 overshot': 0x10,
    'limit2 undershot': 0x20,
    'error': 0x40,
}


def get_pt100_status_message(value):
    """
    Maps the content of the status PV to the internal status of the device
    """

    # The sign bit is used as a flag for the internal status of the device.
    # In case its value is 1 we need to enforce 'value' to be unsigned.
    #
    # Error map
    # |   15   |   14  |  ... |   6   | 5 | 4 | 3 | 2 |     1     |     0      |
    # | Toggle | State | None | Error |  Lim2 |  Lim1 | Overrange | Underrange |

    if value < 0:
        value = (value + 0x100000000) | 0xFF
    if value & error_bits['error']:
        value ^= error_bits['error']
        for text, error in error_bits.items():
            if value == error:
                return status.ERROR, text
        return status.ERROR, 'error'
    return status.OK, ''

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

class EpicsPT100Temperature(EpicsReadableEss):
    """
    Device that reads one of the PT100 sensors.
    """

    parameters = {
        'statuspv':
            Param('PV name for status code', type=pvname, mandatory=False),
    }

    def _get_pv_parameters(self):
        if self.statuspv:
            return EpicsReadableEss._get_pv_parameters(self) | {'statuspv'}
        return EpicsReadableEss._get_pv_parameters(self)

    def doStatus(self, maxage=0):
        # Return the status and the affected pvs in case the status is not OK
        epics_status = self._get_pvctrl('readpv', 'status', update=True)
        epics_severity = self._get_pvctrl('readpv', 'severity')
        mapped_status = SEVERITY_TO_STATUS.get(epics_severity, status.UNKNOWN)
        status_message = STAT_TO_STATUS.get(epics_status, 'Unknown status flag %i'%epics_status)
        return mapped_status, status_message
