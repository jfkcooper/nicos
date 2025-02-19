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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
"""
This defines some commands for interfacing directly with EPICS from NICOS
This is for us, for debugging
"""
import epics

from nicos import session
from nicos.commands import helparglist, hiddenusercommand, usercommand
from nicos.commands.device import disable, enable

from nicos_sinq.devices.epics.motor import EpicsMotor as SinqEpicsMotor


@hiddenusercommand
@helparglist('PV-name,optionaL as_string')
def caget(PV, as_string=True):
    return epics.caget(PV, as_string)


@hiddenusercommand
@helparglist('PV-name,value')
def caput(PV, value):
    return epics.caput(PV, value)


@hiddenusercommand
@helparglist('PV-name')
def cainfo(PV):
    return epics.cainfo(PV)


def _enableSetupMotors(function, *setupnames):
    for setupname in setupnames:
        if setupname not in session.loaded_setups:
            session.log.warning('%r is not a loaded setup, ignoring',
                                setupname)
            continue
        for devname in session.getSetupInfo()[setupname]['devices']:
            device = session.getDevice(devname)
            if isinstance(device, SinqEpicsMotor):
                function(device)


@usercommand
@helparglist('setup, ...')
def DisableSetupMotors(*setupnames):
    """Disable all the motors (that are capable of that) in the setups.

    Example:

    >>> DisableSetupMotors('epics_motors')
    """
    _enableSetupMotors(disable, *setupnames)


@usercommand
@helparglist('setup, ...')
def EnableSetupMotors(*setupnames):
    """Enable all the motors (that are capable of that) in the setups.

    Example:

    >>> EnableSetupMotors('epics_motors')
    """
    _enableSetupMotors(enable, *setupnames)
