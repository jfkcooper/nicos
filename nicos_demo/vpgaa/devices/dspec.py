# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""Classes to simulate the DSpec detector."""

from nicos.core import ArrayDesc, Override, Param, intrange, status, tupleof
from nicos.devices.generic.detector import GatedDetector
from nicos.devices.generic.virtual import VirtualImage


class Spectrum(VirtualImage):

    parameters = {
        'preselection': Param('Preset value for this channel', type=float,
                              settable=True),
    }

    parameter_overrides = {
        'size': Override(type=tupleof(intrange(1, 1), intrange(1, 16384)),
                         default=(1, 16384)),
        'iscontroller': Override(settable=True),
    }

    # set to True to get a simplified doEstimateTime
    is_timer = False

    def doInit(self, mode):
        self.arraydesc = ArrayDesc(self.name, self.size[::-2], '<u4')

    def doEstimateTime(self, elapsed):
        if not self.iscontroller or self.doStatus()[0] != status.BUSY:
            return None
        if self.is_timer:
            return self.preselection - elapsed
        else:
            counted = float(self.doRead()[0])
            # only estimated if we have more than 3% or at least 100 counts
            if counted > 100 or counted > 0.03 * self.preselection:
                if 0 <= counted <= self.preselection:
                    return (self.preselection - counted) * elapsed / counted

    def doReadArray(self, _quality):
        if self._buf is not None:
            return self._buf[0]
        return self._buf


class DSPec(GatedDetector):

    parameters = {
        'prefix': Param('prefix for filesaving',
                        type=str, settable=False, mandatory=True,
                        category='general'),
        'ecalslope': Param('Energy Calibration Slope',
                           type=int, mandatory=False, settable=True,
                           prefercache=True, default=0, category='general'),
        'ecalintercept': Param('Energy Calibration Slope',
                               type=int, mandatory=False, settable=True,
                               prefercache=True, default=0,
                               category='general'),
    }

    parameter_overrides = {
        'enablevalues':  Override(settable=True, category='general'),
    }

    def _presetiter(self):
        for k in ('info', 'Filename'):
            yield k, None, 'other'
        for dev in self._attached_timers:
            if dev.name == 'truetim':
                yield 'TrueTime', dev, 'time'
            elif dev.name == 'livetim':
                yield 'LiveTime', dev, 'time'
            elif dev.name == 'clocktim':
                yield 'ClockTime', dev, 'time'
        for dev in self._attached_images:
            yield 'counts', dev, 'counts'

    def presetInfo(self):
        pinfo = {'info', 'Filename'}
        for dev in self._attached_timers:
            if dev.name == 'truetim':
                pinfo = pinfo.union({'TrueTime'})
            elif dev.name == 'livetim':
                pinfo = pinfo.union({'LiveTime'})
            elif dev.name == 'clocktim':
                pinfo = pinfo.union({'ClockTime'})
        if self._attached_images:
            pinfo = pinfo.union({'counts'})
        return pinfo
