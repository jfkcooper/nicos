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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""IMPAC Pyrometer IGAR 12-LO"""

from nicos.core import Override, Param, Readable, intrange, status
from nicos.devices.tango import PyTangoDevice


class TemperatureSensor(PyTangoDevice, Readable):
    """The temperature readout device of the IMPAC pyrometer."""

    parameters = {
        'address': Param('Device address',
                         type=intrange(0, 97), default=0, settable=False,),
    }

    parameter_overrides = {
        'comtries': Override(default=5),
    }

    def doInit(self, mode):
        pass

    def doRead(self, maxage=0):
        # return current temperature
        what = '%02dms' % self.address
        temp = float(self._dev.Communicate(what))
        if temp > 77769:
            temp = -0
        else:
            temp /= 10.0
        return temp

    def doStatus(self, maxage=0):
        return status.OK, 'idle'
