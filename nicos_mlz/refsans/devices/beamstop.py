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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************

"""Read devices for the beam stop (externally driven)."""

from nicos.core import Readable, status
from nicos.core.params import Attach


class BeamStopDevice(Readable):
    attached_devices = {
        'att': Attach('VSD device', Readable),
    }

    def doRead(self, maxage=0):
        return self._attached_att.read(maxage)

    def doStatus(self, maxage=0):
        if self._attached_att.read(maxage) < 0.01:
            return status.ERROR, 'VSD disconected'
        return status.OK, ''


class BeamStopCenter(Readable):
    attached_devices = {
        'att': Attach('VSD device', Readable),
    }

    def doRead(self, maxage=0):
        val = self._attached_att.read(maxage)
        if val < 4:
            return 'None'
        elif val > 7:
            return 'On'
        return 'Off'

    def doStatus(self, maxage=0):
        if self.doRead(maxage) == 'None':
            return status.ERROR, 'VSD disconected'
        return status.OK, ''
