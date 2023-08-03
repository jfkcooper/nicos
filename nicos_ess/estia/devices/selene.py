#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Artur Glavic <artur.glavic@psi.ch
#
# *****************************************************************************


"""
This module implements the selene guides system. Guides can be properly
shaped using a number of screws on the back. A robot position and drives the
screwdriver.
"""

from __future__ import absolute_import, division, print_function

import numpy as np

from nicos.core import Attach, Param, status, Value, oneof, dictof, tupleof
from nicos.core.device import Override, Moveable
from nicos.devices.generic import LockedDevice
from nicos_ess.devices.epics.pva.motor import EpicsMotor
from nicos.devices.epics.pva.epics_devices import EpicsMappedReadable
import yaml

from nicos_ess.estia.devices.multiline import MultilineController, MultilineChannel


class SeleneRobot(Moveable):
    parameters = {
        'adjuster_backslash': Param('Backslash for rotation', mandatory=False,
                                    userparam=True, default=10.0, unit='deg'),
        'adjuster_play':      Param('Typical play within screw', mandatory=False,
                                    userparam=True, default=5.0, unit='deg', ),
        'cart_backslash':     Param('Backslash for rotation', mandatory=False,
                                    userparam=True, default=0.2, unit='mm', ),
        'delta12':            Param('Distance between driver 1 and 2', mandatory=True,
                                    userparam=True, unit='mm', ),
        'engaged':            Param('Screwdriver engaged position', type=float,
                                    mandatory=True, userparam=False, unit='mm', ),
        'retracted':          Param('Screwdriver retracted position', type=float,
                                    mandatory=True, userparam=False, unit='mm', ),
        'position_data':      Param('YAML file that contins the positioning data', type=str,
                                    mandatory=True, userparam=False, unit='mm', ),
        'rotation':      Param('Rotation angle of selected driver0', type=float,
                                    mandatory=False, userparam=True, unit='deg', ),
        'driver':      Param('Selected screw driver (1/2)', type=oneof(0, 1, 2), default=1,
                                    settable=True, internal=True, unit=''),
        'positions':      Param('Internal screw position tracking',
                                    type=dictof(int, dictof(int, tupleof(float, float))),
                                    settable=True, internal=True, unit=''),
        'rotations':      Param('Internal screw position tracking',
                                    type=dictof(int, dictof(int, float)),
                                    settable=True, internal=True, unit=''),
        'current_position':      Param('Internal screw position tracking',
                                    type=tupleof(int, int),
                                    settable=True, internal=True, unit=''),
        }

    attached_devices = {
        'move_x':     Attach('Device for rotation', EpicsMotor),
        'move_z':     Attach('Device for approache', EpicsMotor),
        'adjust1':    Attach('Device for rotation', EpicsMotor),
        'approach1':  Attach('Device for approache', EpicsMotor),
        'hex_state1': Attach('Device reporting the hex status', EpicsMappedReadable),
        'adjust2':    Attach('Device for rotation', EpicsMotor),
        'approach2':  Attach('Device for approache', EpicsMotor),
        'hex_state2': Attach('Device reporting the hex status', EpicsMappedReadable),
        }


    def doInit(self, mode):
        self._xpos_zero1 = 0.
        self._xpos_zero2 = 0.
        self._item_zpos = {}
        self._confirmed = {}
        items1 = 0
        items2 = 0
        for item, ditem in self.positions.items():
            data = np.array(list(ditem.values()), dtype=float)
            if item<4:
                items2 += 1
                self._xpos_zero2 += (data[:, 0]%480).mean()
            else:
                items1 += 1
                self._xpos_zero1 += (data[:, 0]%480).mean()

            self._item_zpos[item] = data[:, 1].mean()

            self._confirmed[item] = {}
            for group in ditem.keys():
                self._confirmed[item][group] = False
        self._xpos_zero1 /= items1
        self._xpos_zero2 /= items2

    def _get_driver(self, xpos):
        # Return which driver is best suited for a certain x-position of the cart
        if abs(xpos%480-self._xpos_zero1)>abs(xpos%480-self._xpos_zero2):
            return 2
        else:
            return 1

    def _select_driver(self, driver=None):
        # use x-position to find the right screw driver to use
        xpos = self._attached_move_x.read()

        if driver is None:
            driver = self._get_driver(xpos)

        if driver in [1,2]:
            self.log.debug("Configuring driver %i"%driver)
            self.driver = driver
        else:
            self.log.warning("Not valid for choose of driver %s"%driver)
            self.driver = 0

    @property
    def _adjust(self):
        if self.driver==1:
            return self._attached_adjust1
        elif self.driver==2:
            return self._attached_adjust2
        else:
            raise ValueError('No valid screw driver selected')

    @property
    def _approach(self):
        if self.driver==1:
            return self._attached_approach1
        elif self.driver==2:
            return self._attached_approach2
        else:
            raise ValueError('No valid screw driver selected')

    @property
    def _hex_state(self):
        if self.driver==1:
            return self._attached_hex_state1
        elif self.driver==2:
            return self._attached_hex_state2
        else:
            raise ValueError('No valid screw driver selected')

    def _engage(self):
        self.log.debug("Engaing driver")
        self._select_driver()
        self._adjust.wait() # make sure the driver is not rotating while moving stage
        self._approach.maw(self.engaged)

    def _disengage(self):
        self.log.debug("Retracting driver")
        self._adjust.wait() # make sure the driver is not rotating while moving stage
        self._attached_approach1.move(self.retracted)
        self._attached_approach2.maw(self.retracted)
        self._attached_approach1.wait()

    def engage(self):
        """
        User version to engage a screw if already positioned.
        Has some additional checkes and usability improvements.
        """
        self.doRead()
        if self.current_position==(-1, -1):
            self.log.error('Robot position does not fit any configuration, aborting')
            return
        xpos = self._attached_move_x.read()
        zpos = self._attached_move_z.read()
        xref, zref = self.positions[self.current_position[0]][self.current_position[1]]
        if abs(xpos-xref)>0.5 or abs(zpos-zref)>0.5:
            self.log.error('Robot position too far from configuration value, aborting')
            return
        if self._hex_state() in ["HexScrewInTransition", "HexScrewFullyOut"]:
            self._engage()
        if self._hex_state()!="HexScrewInserted":
            # issue with insertion
            self.log.warning("Screw driver not inserted correctly, trying to rotate")
            angle = self.rotations[self.current_position[0]][self.current_position[1]]
            self._adjust.maw(angle-60)
            self._adjust.maw(angle+self.adjuster_play/2.)
            self._adjust.maw(angle)
            if self._hex_state()!="HexScrewInserted":
                self.log.error("Screw driver still not inserted correctly, aborting")
                self._disengage()
                return
        self.log.info('Driver in position')

    def disengage(self):
        """
        User version to disengage a screw driver.
        Makes sure it is not accidentally retracted without storing rotation position.
        """
        if self._hex_state()!="HexScrewInserted":
            self.log.info('Not engaged')
            return
        if abs(self.rotations[self.current_position[0]][self.current_position[1]]-self._adjust())>(self.adjuster_play/2.):
            self.log.error('Rotation position does not fit the stored value, did you use adjust for last movement?')
            return
        self._disengage()
        self.log.info('Driver retracted')

    def doRead(self, maxage=0):
        xpos = self._attached_move_x.read()
        zpos = self._attached_move_z.read()
        for item, ditem in self.positions.items():
            for group, dgroup in ditem.items():
                if abs(dgroup[0]-xpos)<5.0 and abs(dgroup[1]-zpos)<5.0:
                    self.current_position = (item, group)
                    return (item, group)
        self.current_position = (-1, -1)
        return (-1, -1)

    def valueInfo(self):
        return (Value('Item', unit=''),
                Value('Group', unit=''))

    def doStart(self, position):
        if len(position)==2:
            item, group = position
            driver = None
        elif len(position)==3 and position[2] in [1, 2]:
            item, group, driver = position
        else:
            raise ValueError("Position should be tuple (item, group) or (item, group, driver)")

        x, z = self.positions[position[0]][position[1]]
        nominal_driver = self._get_driver(x)
        if driver:
            if nominal_driver!=driver:
                # the user selected a driver that is not configured for this position
                self.log.debug('Manual overwrite of driver, changing expected x position')
                if nominal_driver==1:
                    x += self.delta12
                else:
                    x -= self.delta12
        else:
            driver = nominal_driver
        self.driver=driver
        self.log.debug("Selected driver = %s, moving to (%i,%i) at location (%.2f, %.2f)"%(
            driver, position[0], position[1], x, z))

        self._disengage()
        self._attached_move_x.move(x)
        self._attached_move_z.move(z)
        rot = self.rotations[position[0]].get(position[1], 0.)
        if driver==2:
            # move driver to last rotation
            self._attached_adjust2.move(rot)
        else:
            # move driver to last rotation
            self._attached_adjust1.move(rot)

    # TODO: Implement an intelligent doStop to prevent any hardware issues and loss of rotation info

    def doTime(self, old_value, target):
        # estimate the approximate movement time from horizontal difference
        out = 30.
        diff = abs(old_value[1]-target[1])*480.
        tdiff = diff / self._attached_move_x.speed
        return out+tdiff

    def doReadRotation(self):
        try:
            return self._adjust()
        except AttributeError:
            return 0.

    def doWriteRotation(self, value):
        self.adjust(value)

    def doPoll(self, n, maxage=0):
        self._pollParam('rotation')

    def doStatus(self, maxage=0):
        sout = status.OK
        motor_messages = []
        for motor in [self._attached_move_x, self._attached_move_z,
                      self._attached_approach1, self._attached_approach2,
                      self._attached_adjust1, self._attached_adjust2]:
            sout = max(sout, motor.status()[0])
            if motor.status()[0] not in [status.OK, status.BUSY] and motor.status()[1].strip()!='':
                motor_messages.append(motor.status()[1])

        smessage = ""
        if sout==status.OK:
            if self._hex_state()=="HexScrewInserted":
                smessage += "ready  "
            elif self._hex_state()=="HexScrewFullyOut":
                smessage += "out     "
            elif self._hex_state()=="HexScrewMissed":
                return (status.ERROR, "screw missed")
            elif self._hex_state()=="HexScrewCollided":
                return (status.WARN, "driver collided")
        elif sout==status.BUSY:
            smessage += "driving "
        else:
            smessage += "        "

        if self.driver in [1,2]:
            smessage += "D%i: %.1f°"%(self.driver, self._adjust())
        if len(motor_messages)>0:
            smessage += ' - '+";".join(motor_messages)
        return (sout, smessage)

    def _move_x(self, x, retry=2):
        for i in range(retry+1):
            try:
                self.log.debug('Moving x to position-backlash, %.2f'%(x-self.cart_backslash))
                self._attached_move_x.maw(x-self.cart_backslash)
                self.log.debug('Moving x to requested position, %.2f'%x)
                self._attached_move_x.maw(x)
            except Exception as e:
                if i==retry:
                    self.log.error("Error in x-positioning: %s, giving up"%e)
                else:
                    self.log.warning("Error in x-positioning: %s, retry"%e)
            else:
                return

    def _move_z(self, z, retry=2):
        for i in range(retry+1):
            try:
                self.log.debug('Moving z to position-backlash, %.2f'%(z-self.cart_backslash))
                self._attached_move_z.maw(z-self.cart_backslash)
                self.log.debug('Moving z to requested position, %.2f'%z)
                self._attached_move_z.maw(z)
            except Exception as e:
                if i==retry:
                    self.log.error("Error in z-positioning: %s, giving up"%e)
                else:
                    self.log.warning("Error in z-positioning: %s, retry"%e)
            else:
                return

    def _move_xz(self, x, z, retry=2):
        for i in range(retry+1):
            try:
                self.log.debug(
                    'Moving x,z to position-backlash, %.2f, %.2f'%(x-self.cart_backslash, z-self.cart_backslash))
                self._attached_move_x.move(x-self.cart_backslash)
                self._attached_move_z.maw(z-self.cart_backslash)
                self._attached_move_x.wait()
                self.log.debug('Moving x,z to requested position, %.2f, %.2f'%(x, z))
                self._attached_move_x.move(x)
                self._attached_move_z.maw(z)
                self._attached_move_x.wait()
            except Exception as e:
                if i==retry:
                    self.log.error("Error in xz-positioning: %s, giving up"%e)
                else:
                    self.log.warning("Error in xz-positioning: %s, retry"%e)
            else:
                return

    def _move_angle(self, phi, retry=2):
        for i in range(retry+1):
            try:
                self._adjust.maw(phi)
            except Exception as e:
                if i==retry:
                    self.log.error("Error in adjuster-positioning: %s, giving up"%e)
                else:
                    self.log.warning("Error in adjuster-positioning: %s, retry"%e)
            else:
                return

    def search_screw(self, step_size=0.2, r_max=5, auto_refine=True, auto_update=False):
        """
        Starting at an approximate position, search for a screw in
        concentric circles with increasing radius.
        Assumes angle of the screw is unknown.
        """
        self._select_driver()

        if self.current_position!=(-1, -1):
            angle = self.rotations[self.current_position[0]][self.current_position[1]]
        else:
            angle = 0.

        self._approach.maw(self.retracted)
        self._adjust.move(angle)

        x_start = self._attached_move_x()
        z_start = self._attached_move_z()

        self.log.info("Searching for screw near %.2f, %.2f"%(x_start, z_start))

        found_screw = False

        for i_r in range(r_max+1):
            if found_screw:
                break
            r = step_size*i_r
            self.log.info("    search radius = %.2f"%r)
            for i_phi in range(7*i_r+1):
                # to keep approximate step size around circle, use 4*i_r angular steps
                phi = 2.*np.pi/max(1, 7*i_r)*i_phi
                xpos = r*np.cos(phi)+x_start
                zpos = r*np.sin(phi)+z_start
                self._move_xz(xpos, zpos)

                self._approach.maw(self.engaged)

                self._move_angle(angle+60)
                if self._hex_state()=="HexScrewInserted":
                    self._move_angle(angle-self.adjuster_backslash)
                    self._move_angle(angle+self.adjuster_play/2.)
                    self._move_angle(angle)
                    found_screw = True
                    break

                self._adjust.move(angle)
                self._approach.maw(self.retracted)

        if found_screw and auto_refine:
            self.log.info("    Screw found at (%.2f, %.2f), trying to refine position"%(xpos, zpos))
            self.refine(auto_update=auto_update)
            return True
        else:
            return found_screw

    def refine(self, srange=2.0, sstep=20, auto_update=False):
        """
        If robot could find the screw, use to refine the more exact
        position of the screw center.
        """
        self._select_driver()

        pos_out = []
        vert_out = []

        x_start = self._attached_move_x()
        z_start = self._attached_move_z()

        self.log.info("Refining screw location around %.2f, %.2f"%(x_start, z_start))

        self._approach.maw(self.retracted)

        for i in range(sstep):
            self._move_x(x_start+srange*(i-sstep/2)/(sstep-1))
            self._approach.maw(self.engaged)
            pos_out.append([self._attached_move_x(), self._hex_state()=="HexScrewInserted"])
            self._approach.maw(self.retracted)

        pos_out = np.array(pos_out)
        x_insertions = pos_out[pos_out[:, 1]==1, 0]
        self.log.info('  Insertions in x-scan: %s'%(x_insertions))
        if len(x_insertions)==0:
            raise ValueError("Scan never inserted into screw")
        self._move_x(x_insertions.mean())

        for j in range(sstep):
            self._move_z(z_start+srange*(j-sstep/2)/(sstep-1))
            self._approach.maw(self.engaged)
            vert_out.append([self._attached_move_z(), self._hex_state()=="HexScrewInserted"])
            self._approach.maw(self.retracted)

        vert_out = np.array(vert_out)
        self.log.info('  Insertions in z-scan: %s'%(vert_out[vert_out[:, 1]==1, 0]))

        # calculate new center
        cen_pos = pos_out[pos_out[:, 1]==1, 0].mean()
        cen_vert = vert_out[vert_out[:, 1]==1, 0].mean()

        self._move_xz(cen_pos, cen_vert)

        if auto_update:
            self.update_position()

        return pos_out, vert_out

    def update_position(self):
        # Change the stored location for the current screw
        self.doRead()
        if self.current_position!=(-1, -1):
            # dict parameter is immutable, create a copy and modify that
            pos = dict([(k, dict(v)) for k,v in self.positions.items()])
            pos[self.current_position[0]][self.current_position[1]] = (
                self._attached_move_x(),
                self._attached_move_z(),
                )
            self.positions = pos
            self.log.info("Updated stored position for screw (%i, %02i) to (%.2f, %.2f)"%(
                self.current_position[0],
                self.current_position[1],
                self.positions[self.current_position[0]][self.current_position[1]][0],
                self.positions[self.current_position[0]][self.current_position[1]][1],
                ))

    def adjust(self, angle):
        self.doRead()
        if self.current_position==(-1, -1):
            return
        if self._hex_state() in ["HexScrewInTransition", "HexScrewFullyOut"]:
            self._engage()
        if self._hex_state()!="HexScrewInserted":
            # issue with insertion
            self.log.warning("Screw driver not inserted correctly, aborting")
            return False
        self.log.debug(
            'Adjusting to position-play/2-backlash, %.2f'%(angle-self.adjuster_play/2.-self.adjuster_backslash))
        self._move_angle(angle-self.adjuster_play/2.-self.adjuster_backslash)
        # always overshoot with the expected play
        self.log.debug('Adjusting to position+play/2, %.2f'%(angle+self.adjuster_play/2.))
        self._move_angle(angle+self.adjuster_play/2.)
        # move back to desired angle for extractoin
        self.log.debug('Releasing screw, %.2f'%(angle))
        self._move_angle(angle)
        self.log.debug('Storing rotation for position (%i, %02i)'%self.current_position)

        rotations = dict([(k, dict(v)) for k,v in self.rotations.items()])

        rotations[self.current_position[0]][self.current_position[1]] = angle
        self.rotations = rotations

    def save_data(self, fname=None):
        if fname is None:
            fname=self.position_data
        data = {
            'positions': dict([(k, dict(v)) for k,v in self.positions.items()]),
            'rotations': dict([(k, dict(v)) for k,v in self.rotations.items()]),
            }
        yaml.dump(data, open(fname, 'w'), indent=2, sort_keys=True)

    def load_data(self, fname=None):
        if fname is None:
            fname = self.position_data
        data = yaml.load(open(fname, 'r'), yaml.FullLoader)
        self.positions = data['positions']
        self.rotations = data['rotations']

    def confirm_all(self):
        self.log.info("Confirming screws...")
        for group in range(1, 16):
            for item in self.positions.keys():
                if self._confirmed[item][group]:
                    continue
                self.log.info("  position (%i, %02i)"%(item, group))
                self.doStart((item, group))
                self._attached_move_x.wait()
                self._attached_move_z.wait()
                self._attached_adjust1.wait()
                self._attached_adjust2.wait()
                self._engage()
                if self._hex_state()=="HexScrewInserted":
                    self.log.info("        confirmed")
                    self._confirmed[item][group] = True
                else:
                    self.log.info("        "+self._hex_state())

    def reference_screw(self, nrot0=15):
        """
        Use the lower hard stop of the adjuster to reference the screw
        absolute rotation position.
        Will drive adjuster negative until the motor stops following
        then it moves nrot0 rotations forward and defines this as new zero.
        """
        self.doRead()
        if self.current_position==(-1, -1):
            return
        if self._hex_state() in ["HexScrewInTransition", "HexScrewFullyOut"]:
            self._engage()
        if self._hex_state()!="HexScrewInserted":
            # issue with insertion
            self.log.warning("Screw driver not inserted correctly, aborting")
            return False
        self.log.info('Moving screw to lower limit')
        try:
            self._adjust.maw(-15000)
        except Exception as e:
            pass
        lpos = self._adjust()
        self.log.info('   screw stopped moving at %.1f°'%lpos)
        lpos_partial = (lpos+180)%360-180 # partial rotation of this position
        dest = self._rotations[self.current_position[0]][self.current_position[1]]
        temp_dest = lpos-lpos_partial+nrot0*360+dest
        self.log.debug('    moving to calculated position %.1f'%temp_dest)
        for i in range(5):
            self._adjust.reset()
            try:
                self._move_angle(temp_dest-self.adjuster_play/2.-self.adjuster_backslash)
            except Exception as e:
                continue
            else:
                break
        self._move_angle(temp_dest+self.adjuster_play/2.)
        self._move_angle(temp_dest)
        self.log.debug('    move driver back to nominal position %.1f'%dest)
        self._disengage()
        self._move_angle(dest)
        return True


class SeleneMetrology(Moveable):
    parameters = {
        'cart_center': Param('Cart position of ellipse center', mandatory=False,
                                userparam=True, default=3500.0, unit='mm'),
        'eta_v': Param('Nominal reflection angle from interferometer head to retroreflector', mandatory=False,
                             userparam=True, default=14.81, unit='deg'),
        'delta_v': Param('Nominal distance between XZ plane and retroreflector', mandatory=False,
                     userparam=True, default=120.0, unit='mm'),
        'eta_h1': Param('Nominal reflection angle from interferometer head to retroreflector', mandatory=False,
                       userparam=True, default=16.39, unit='deg'),
        'delta_h1': Param('Nominal distance between XZ plane and retroreflector', mandatory=False,
                         userparam=True, default=70.0, unit='mm'),
        'zret_h1': Param('Nominal distance between XY plane and retroreflector', mandatory=False,
                         userparam=True, default=70.0, unit='mm'),
        'zcol_h1': Param('Nominal distance between XY plane and collimator', mandatory=False,
                         userparam=True, default=70.0, unit='mm'),
        'eta_h2': Param('Nominal reflection angle from interferometer head to retroreflector', mandatory=False,
                       userparam=True, default=15.47, unit='deg'),
        'delta_h2': Param('Nominal distance between XZ plane and retroreflector', mandatory=False,
                         userparam=True, default=80.0, unit='mm'),
        'zret_h2': Param('Nominal distance between XY plane and retroreflector', mandatory=False,
                         userparam=True, default=70.0, unit='mm'),
        'zcol_h2': Param('Nominal distance between XY plane and collimator', mandatory=False,
                         userparam=True, default=70.0, unit='mm'),
        'delta_x': Param('Nominal x-distance of retroreflector and cart center', mandatory=False,
                         userparam=True, default=-15.0, unit='mm'),
        'if_offset_u_h1': Param('Deviation of laser path length as determined at center',
                           internal=True, default=0.0, unit='mm'),
        'if_offset_u_h2': Param('Deviation of laser path length as determined at center',
                                 internal=True, default=0.0, unit='mm'),
        'if_offset_u_v1': Param('Deviation of laser path length as determined at center',
                                 internal=True, default=0.0, unit='mm'),
        'if_offset_u_v2': Param('Deviation of laser path length as determined at center',
                                 internal=True, default=0.0, unit='mm'),
        'if_offset_d_h1': Param('Deviation of laser path length as determined at center',
                                 internal=True, default=0.0, unit='mm'),
        'if_offset_d_h2': Param('Deviation of laser path length as determined at center',
                                 internal=True, default=0.0, unit='mm'),
        'if_offset_d_v1': Param('Deviation of laser path length as determined at center',
                                 internal=True, default=0.0, unit='mm'),
        'if_offset_d_v2': Param('Deviation of laser path length as determined at center',
                                 internal=True, default=0.0, unit='mm'),
    }

    attached_devices = {
        'm_cart': Attach('Metrology cart', LockedDevice),
        'interferometer': Attach('Attached interferometer', MultilineController),
        'ch_u_h1': Attach('Interferometer channel for horizontal mirror up-stream', MultilineChannel),
        'ch_u_h2': Attach('Interferometer channel for horizontal mirror up-stream', MultilineChannel),
        'ch_u_v1': Attach('Interferometer channel for vertical mirror up-stream', MultilineChannel),
        'ch_u_v2': Attach('Interferometer channel for vertical mirror up-stream', MultilineChannel),
        'ch_d_h1': Attach('Interferometer channel for horizontal mirror down-stream', MultilineChannel),
        'ch_d_h2': Attach('Interferometer channel for horizontal mirror down-stream', MultilineChannel),
        'ch_d_v1': Attach('Interferometer channel for vertical mirror down-stream', MultilineChannel),
        'ch_d_v2': Attach('Interferometer channel for vertical mirror down-stream', MultilineChannel),
    }

    _sb = 157. # selene distance center-ellipse
    _sc = 6000. # selene distance center-focus

    _mw = 480. # mirror width
    _sx = 42.5 # distance of screw from edge of mirror

    def doInit(self, dummy=None):
        pass

    def doRead(self, maxage=0):
        """
        Position is the location on mirror and mirror number counting from up-stream.
        Location on mirror is -1: up-stream screw, 0: center, 1: down-stream screw.
        """
        pos = self._attached_m_cart()-self.cart_center
        mirror = (pos+self._mw/2)//self._mw + 8 # mirrors are 480 wide and 8 is the central one
        rpos = (pos+self._mw/2)%self._mw-self._mw/2 # relative position on mirror
        if abs(rpos)<30:
            return (0, mirror)
        elif abs(rpos-self._sx)<30:
            if rpos<0:
                return (-1, mirror)
            else:
                return (1, mirror)
        else:
            return (rpos, mirror)


    def valueInfo(self):
        return (Value('Relative Position', unit=''),
                Value('Mirror', unit=''))

    def doStart(self, position):
        if len(position)==2 and position[0] in [-1, 0, 1] and position[1] in range(1,15):
            rel_pos, mirror = position
        else:
            raise ValueError("Position should be tuple (rel. location, mirror) w/ rel. location in [-1,0,1]")
        calc_pos = 480*(mirror-8) + rel_pos*(480-self._sx)
        self._attached_m_cart.move(self.cart_center+self._cart_for_x(calc_pos))

    def _ellipse(self, xpos):
        # return selene ellipse height at distance from center
        return self._sb*np.sqrt(self._sc**2-xpos**2)

    def _ellipse_angle(self, xpos):
        # return the inclanation of the ellipse at defined position
        raise NotImplementedError("TODO")

    def _cart_for_x(self, xpos):
        """
        Calculate the cart position necessary to measure at a certain x-positin on the ellipse.
        This has to take into account the location of the correct interferometer heads
        and the change in reflection spot location due to ellipse surface changing distance to cart.
        """
        if abs(xpos)<100.:
            # if around center of guide, don't perform any correction
            return xpos
        # In the optimal configuration the retro reflector receives the beam with
        # half of the nominal angle plus 2x the surface inclination.
        alpha = self.eta_v*np.pi/180. + self._ellipse_angle(abs(xpos))/2.
        # distance of that reflection is the nominal distance at center minus ellipse height
        h = self.delta_v  + self._sb - self._ellipse(xpos)
        div = self.delta_x + np.tan(alpha)*h
        direction=np.sign(xpos) # select if up-stream or down-stream collimators are used
        return xpos+direction*div

    def _x_for_cart(self, xpos):
        """
        Calculate the approximate position the laser hits the mirror
        for a given cart position
        """
        delta=100.
        xout = xpos
        while delta>1.:
            dpos = self._cart_for_x(xout)-xpos
            xout -= dpos
            delta = abs(dpos)
        return xout

    def _nominal_path_lengths(self, pos_motor=None):
        """
        Calculate the individual laser path lengths that would be excepted
        if the mirrors are perfectly aligned.
        """
        if pos_motor is None:
            pos_motor = self._attached_m_cart()-self.cart_center
        xpos = self._x_for_cart(pos_motor)
        # length of laser is distance reflector-mirror + collimator-mirror
        # vertical mirrors
        dalpha = self._ellipse_angle(abs(xpos))/2.
        h = self.delta_v + self._sb - self._ellipse(xpos)
        v_l1 = h/np.cos(self.eta_v*np.pi/180.+dalpha) # reflector angle gets larger
        v_l2 = h/np.cos(self.eta_v*np.pi/180.-dalpha) # collimator angle gets smaller

        # for diagnoal paths, 3d has to be considered and two reflections
        # horizontal w/ short path
        h1_ret = np.array([self.delta_x, -self.delta_h1, self.zret_h1])
        h1_col = np.array([self.delta_x+2*(self.delta_h1+self._sb)*np.tan(self.eta_h1),
                           -self.delta_h1, self.zcol_h1])
        # both beams should come under ~45°, so y/z-positions are equal to z/y-distance
        h1_p1 = np.array([0., self.zret_h1-h, h])
        h1_p2 = np.array([0., h, self.zcol_h1-h])
        h1_l1 = np.sqrt(((h1_col-h1_p1)**2).sum())
        h1_l2 = np.sqrt(((h1_p1-h1_p2)**2).sum())
        h1_l3 = np.sqrt(((h1_p2-h1_ret)**2).sum())

        # horizontal w/ long path
        h2_ret = np.array([self.delta_x, -self.delta_h2, self.zret_h2])
        h2_col = np.array([self.delta_x+2*(self.delta_h2+self._sb)*np.tan(self.eta_h2),
                           -self.delta_h2, self.zcol_h2])
        # both beams should come under ~45°, so y/z-positions are equal to z/y-distance
        h2_p1 = np.array([0., self.zret_h2-h, h])
        h2_p2 = np.array([0., h, self.zcol_h2-h])
        h2_l1 = np.sqrt(((h2_col-h2_p1)**2).sum())
        h2_l2 = np.sqrt(((h2_p1-h2_p2)**2).sum())
        h2_l3 = np.sqrt(((h2_p2-h2_ret)**2).sum())

        return (v_l1+v_l2, h1_l1+h1_l2+h1_l3, h2_l1+h2_l2+h2_l3)

    def calibrate(self):
        """
        Use measurement at center position to calibrate the
        interferometer channel lengths measured.
        """
        self.log.info("Performing calibration")
        self._attached_interferometer.measure()
        self._attached_interferometer.wait()
        v, h1, h2 = self._nominal_path_lengths(0.)
        for chv in [self._attached_ch_u_v1, self._attached_ch_u_v2,
                    self._attached_ch_d_v1, self._attached_ch_d_v2]:
            if chv.status()[0]==status.OK:
                vm = chv()
            else:
                self.warning("Channel %s not measured correctly" % chv._name)

#
# class SeleneGuide(BaseSequencer):
#     parameters = {
#         'major_axis': Param('Major semi-axis of the ellipse', type=float,
#                             unit='mm',
#                             settable=False, mandatory=True,
#                             userparam=False,
#                             category='general'),
#         'minor_axis': Param('Minor semi-axis of the ellipse', type=float,
#                             unit='mm',
#                             settable=False, mandatory=True,
#                             userparam=False,
#                             category='general'),
#         'segment_length': Param('Length of one mirror segment', type=float,
#                                 unit='mm',
#                                 settable=False, mandatory=True,
#                                 userparam=False,
#                                 category='general'),
#         'screws_semidistance': Param('Semidistance between screws along '
#                                      'x-axis', mandatory=True,
#                                      userparam=False, unit='mm', ),
#         'adjuster_rows': Param('Position of the screws along X-axis',
#                                type=list, settable=True,
#                                mandatory=True,
#                                userparam=False, unit='mm', ),
#         'adjuster_columns': Param('Position of the screws along Z-axis',
#                                   type=list, settable=True,
#                                   mandatory=True,
#                                   userparam=False, unit='mm', ),
#         'segments': Param('Number of segments that compose the guide',
#                           type=int, mandatory=True, userparam=False, ),
#         'vertical_ratio': Param('', mandatory=True,
#                                 userparam=False, unit='mm/deg', ),
#         'horizontal_ratio': Param('', mandatory=True,
#                                   userparam=False, unit='mm/deg', ),
#         'adjuster_angles': Param('Current rotation angles', type=list,
#                                  mandatory=True,
#                                  userparam=True, settable=True, unit='deg', ),
#         'adjuster_positions': Param('Screws position', type=list,
#                                     mandatory=True, settable=True,
#                                     userparam=False, unit='mm', ),
#         # 'driver_dx': Param('', mandatory=True,
#         #                    userparam=False, unit='mm', ),
#     }
#
#     parameter_overrides = {
#         'precision': Override(userparam=False, default=0.01),
#         'lowlevel': Override(default=False),
#     }
#
#     attached_devices = {
#         'rx': Attach('Adjustment X-axis motor', EpicsMotor),
#         'rz': Attach('Adjustment Z-axis motor', EpicsMotor),
#         'screwdriver': Attach('Adjustment screwdriver', Screwdriver),
#         #  'interferometer': Attach('Interferometer', MirrorDistance),
#         #  'm_cart': Attach('Metrology cart', LockedDevice),
#         'measurement': Attach('Guide measurement system',
#                               SeleneMeasurementHandler)
#     }
#
#     _offset_values = []
#     _actions = []
#
#     def _generateSequence(self, _):  # pylint: disable=W0221
#         print('_generateSequence')
#         return self._actions
#
#     def doInit(self, dummy=None):
#         segment_len = self.segment_length
#         distance = self.screws_semidistance
#         # self._adjuster_columns = [
#         #     [-distance + (i - 7) * segment_len,
#         #      distance + (i - 7) * segment_len]
#         #     for i in range(self.segments)]
#
#         # FIX
#         # self.adjuster_columns = [[60.0, 455.1, 100],
#         # 				    [455.1, 100, 100] ]
#         # self.adjuster_rows = [[157.0, 123.5, 187.5],
#         #                                  [212.7, 187.5, 222.5]]
#
#         if not self.adjuster_angles:
#             self.log.warning('Initialize empty \'adjuster_angles\'')
#             self.adjuster_angles = [[[0] * 3] * 2] * \
#                                               self.segments
#         if not self.adjuster_positions:
#             self.log.warning('Initialize empty \'adjuster_positions\'')
#             self.adjuster_positions = [[[0] * 3] * 2] * self.segments
#
#     def _compute_adjustement_sequence(self):
#         self._adjust_guide()
#
#     def doStart(self, target=None):
#         #        self.adjust_guide()
#         BaseSequencer.doStart(self, target)
#
#     def doRead(self, maxage=0):
#         return self._find_screw_indices()
#
#     # def doStatus(self, maxage=0):
#     #     return None
#
#     # def doStatus(self, maxage=0):
#     #     return None
#
#     # def _position_for(self, segment, step):
#     #     x_m = self.adjuster_columns[segment][step]
#     #     self._actions.append(SeqDev(self._attached_rx, x_m))
#
#     # def _measure_current_position(self, segment, step):
#     #     x_m = self.adjuster_columns[segment][step]
#     #     self._actions.append(
#     #         SeqCall(self._attached_measurement.measure, x_m))
#
#     def _get_offsets(self, step, index):
#         offset_values = self._attached_measurement.doRead()
#         self.log.warning(offset_values)
#         delta_pos = 10
#         if (step == 0 and index == 2) or (step == 1 and index > 0):
#             # delta_pos = interpolate()
#             delta_rot = delta_pos / self.horizontal_ratio
#         else:
#             # delta_pos = interpolate()
#             delta_rot = delta_pos / self.vertical_ratio
#         return delta_pos, delta_rot
#
#     def _adjust(self, rot_from, rot_to):
#         # if self._attached_rx.read() > 0:
#         #     drive = self._attached_r1t
#         # else:
#         #     drive = self._attached_r2t
#         drive = self._attached_screwdriver
#
#         drive.doStart([rot_from, rot_to, ])
#         self._attached_screwdriver.wait()
#
#     def _mock_adjust_guide_segment(self, segment, step, index):
#         self._mock_position_for(segment, step)
#         _offset_values = self._attached_measurement.read()
#
#     def _adjust_guide(self):
#         for segment in range(self.segments):
#             for step in range(2):
#                 # append to SeqCall list
#                 # self._position_for(segment, step)
#                 self._actions.append(SeqCall(self.move_to_position, segment,
#                                              step))
#
#                 # FIXME: Doesn't this require the index too?
#                 self._measure_current_position(self, segment, step)
#                 # This must be sequential too!
#                 _offset_values = self._attached_measurement.read()
#                 for index in range(3):
#                     self._actions.append(
#                         SeqCall(self.move_to_position, segment,
#                                 step, index))
#
#                     rot_from = self._adjuster_angles[segment][
#                         step][index]
#                     # pos_from = self._adjuster_positions[segment][
#                     #     step][index]
#                     delta_rot, delta_pos = self._get_offsets(step, index)
#                     self.log.info('({},{},{}) -> delta_rot: {'
#                                   '}\tdelta_pos: {}'.format(segment,
#                                                             step,
#                                                             index,
#                                                             delta_rot,
#                                                             delta_pos))
#                     # self._adjust(rot_from, rot_from + delta_rot)
#                     # FIXME: check success
#                     success = True
#                     if success:
#                         self.adjuster_angles[segment][step][
#                             index] += \
#                             delta_rot
#                         self.adjuster_positions[segment][step][
#                             index] += \
#                             delta_pos
#
#     # Determine the screw indices correspondig to the current position. If
#     # the current position in more than 'tolerance' cm far from any screw,
#     # returns None (i.e. assumes that we are not at any screw)
#     def _find_x_index(self, tolerance=.5):
#         x_pos = self._attached_rx()
#         for segment, segment_values in enumerate(self.adjuster_columns):
#             if abs(segment_values[0] - x_pos) < tolerance:
#                 return segment, 0
#             if abs(segment_values[1] - x_pos) < tolerance:
#                 return segment, 1
#         return None, None
#
#     def _find_z_index(self, tolerance=.5):
#         z_pos = self._attached_rz()
#         for step, step_values in enumerate(self.adjuster_rows):
#             if abs(step_values[0] - z_pos) < tolerance:
#                 return step, 0
#             if abs(step_values[1] - z_pos) < tolerance:
#                 return step, 1
#         return None, None
#
#     def _find_screw_indices(self, tolerance=.5):
#         segment, x_index = self._find_x_index(tolerance)
#         step, z_index = self._find_z_index(tolerance)
#         # TODO: needs review
#         if z_index is None or x_index is None: #or x_index != z_index:
#             self.log.info('Screwdriver not in a screw position')
#             return None, None, None
#         return segment, step, 0
#
#     def _update_adjuster_angle(self):
#         segment, column, row = self._find_screw_indices()
#         if None in [segment, column, row]:
#             self.log.info('Not in a screw position, no angle to update')
#             return
#         current = self.adjuster_angles
#         angle = self._attached_screwdriver._attached_angle()
#         updated = [[list(curcol) for curcol in curseg] for curseg in current]
#         updated[segment][column][row]=angle
#         self._setROParam('adjuster_angles', updated)
#
#     def update_screw_position(self):
#         segment, column, row = self._find_screw_indices(tolerance=5.0)
#         if None in [segment, column, row]:
#             self.log.info('Not in a screw position, no positon to update')
#             return
#         cx = self._attached_rx.read()
#         cz = self._attached_rz.read()
#         cols = [list(curseg) for curseg in self.adjuster_columns]
#         rows = [list(curstep) for curstep in self.adjuster_rows]
#         self.log.info('Updating column,row from %.2f,%.2f to %.2f,%.2f'%
#                       (cols[segment][row], rows[column][row], cx, cz))
#         cols[segment][row]=cx
#         rows[column][row]=cz
#         self._setROParam('adjuster_columns', cols)
#         self._setROParam('adjuster_rows', rows)
#
#     def disengage(self):
#         if self._attached_screwdriver._is_engaged():
#             self._update_adjuster_angle()
#             self._attached_screwdriver._disengage()
#
#     def engage(self):
#         segment, step, index = self._find_screw_indices()
#         if not segment in [segment, step, index]:
#             angle = self.adjuster_angles[segment][step][index]
#             if self._attached_screwdriver._attached_angle() != angle:
#                 self.log.info('Current screwdriver rotation doesn\'t match '
#                               'screw angle, correcting rotation')
#                 self._attached_screwdriver.rotate_to(angle)
#         self._attached_screwdriver._engage()
#
#     def move_to_position(self, segment, step, index=0):
#         if self._attached_screwdriver._is_engaged():
#             self.disengage()
#         self._attached_rx.move(self.adjuster_columns[segment][step])
#         self._attached_rz.move(self.adjuster_rows[step][index])
#         self._attached_screwdriver._attached_angle.move(
#             self.adjuster_angles[segment][step][index])
#         self._attached_rx.wait()
#         self._attached_rz.wait()
#         self._attached_screwdriver._attached_angle.wait()
#
#     # TESTING
#     # FIXME: Doesn't this require the index (i.e. z position) too?
#     def measure_position(self, segment, step, index=None):
#         x_m = self.adjuster_columns[segment][step]
#         self._attached_measurement._position_to_measure(x_m)
#         self._attached_measurement.measure(x_m)
#         self._attached_measurement.wait()
