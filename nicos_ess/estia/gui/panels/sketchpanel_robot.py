#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2019 by the NICOS contributors (see AUTHORS)
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
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************
'''
A sketch display of the Selene adjustment robot to vizualize state of the instrument.
'''

from nicos.clients.gui.panels import Panel
from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, UNKNOWN, \
    WARN
from nicos.guisupport.qt import QGraphicsView, QGraphicsScene, QGraphicsItem, \
    QGraphicsItemGroup, QVBoxLayout, QGraphicsEllipseItem, QGraphicsRectItem, \
    QColor, QGraphicsSimpleTextItem, Qt, QFont, QTimer, QPixmap, QPen, \
    pyqtSlot
from nicos.protocols.cache import cache_load, OP_TELL, cache_dump
from nicos.utils import findResource

STATUS_COLORS = {
    OK: QColor(0, 255, 0),
    WARN: QColor(200, 200, 0),
    BUSY: QColor(100, 100, 0),
    NOTREACHED: QColor(128, 0, 128),
    DISABLED: QColor(50, 50, 50),
    ERROR: QColor(255, 0, 0),
    UNKNOWN: QColor(128, 128, 128),
}

from .graphics_helpers import InteractiveEllipse, InteractiveGroup, TransmittingGroup

class RobotSketchPanel(Panel):
    _devinfo = {}

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self._view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self._view.setScene(self.scene)
        vbox.addWidget(self._view)

        self.posx = options.get('posx')
        self.posz = options.get('posz')
        self.approach1 = options.get('approach1')
        self.rotation1 = options.get('rotation1')
        self.approach2 = options.get('approach2')
        self.rotation2 = options.get('rotation2')
        self.selene = int(options.get('selene', 1))

        self.robot = options.get('robot', None)

        self.offsetx = float(options.get('offsetx'))
        self.offsetz = float(options.get('offsetz'))

        self.screw_group = options.get('screw_group')

        self.title = options.get('title', 'Robot Selene %i'%self.selene)
        if self.selene==1:
            self.scene.setBackgroundBrush(QColor(230,200,200))
            self.title='(view inverted) '+self.title

        self.build_background()
        self.build_cart()

        self._currentSelection = None

        client.cache.connect(self.on_client_cache)
        client.connected.connect(self.on_client_connected)

        QTimer.singleShot(5000, self.resizeEvent)

    def build_background(self):
        s = self.scene
        rack = QGraphicsRectItem(-7250, 0, 7250, 820)
        s.addItem(rack)
        rack.setZValue(-13.)
        rack.setBrush(QColor(200, 200, 200))

        stage = s.addRect(-7250, -50, 7250, 100)
        stage.setZValue(-11.)
        stage.setBrush(QColor(50, 50, 50))

        for group in range(15):
            for sx, sy, active,item in self.screw_group:
                si=InteractiveEllipse('screw', -sx-480*group, 720-sy, 30, 30)
                si.screw_group=15-group
                si.screw_item=item+1
                s.addItem(si)
                si.setZValue(-10.)
                if active:
                    si.setBrush(QColor(100, 25, 25))
                else:
                    si.setBrush(QColor(75, 75, 75))
                si.setFlag(QGraphicsItem.ItemIsSelectable, True)

            group_label = QGraphicsSimpleTextItem('%01i'%(si.screw_group))
            group_label.setFont(QFont('sans', 52))
            s.addItem(group_label)
            group_label.setPos(-(260+480*group), 375)

            cutout = QGraphicsRectItem(-(380+480*group), 220, 300, 540)
            s.addItem(cutout)
            cutout.setZValue(-12.)
            cutout.setBrush(QColor(150, 150, 150))

        self._selectionText = QGraphicsSimpleTextItem(self.title)
        self._selectionText.setFont(QFont('sans', 54))
        s.addItem(self._selectionText)
        self._selectionText.setPos(-7250/2-self._selectionText.boundingRect().width()/2, -200)

    def build_cart(self):
        s = self.scene

        self.vstage = TransmittingGroup()
        v = self.vstage
        v.setZValue(10.)
        s.addItem(v)


        vstage = QGraphicsRectItem(-100, 0, 200, 820)
        vstage.setZValue(-1.0)
        vstage.setBrush(QColor(128, 128, 128, 128))
        v.addToGroup(vstage)

        self.hstage = InteractiveGroup("driver")
        h = self.hstage
        h.setZValue(12.)
        v.addToGroup(h)

        hstage=QGraphicsRectItem(-160, -60, 320, 120)
        hstage.setZValue(-1.0)
        hstage.setBrush(QColor(128, 128, 128, 128))
        h.addToGroup(hstage)

        self.driver2=QGraphicsEllipseItem(-204, -25, 50, 50)
        self.driver2.setZValue(1.0)
        self.driver2.setBrush(QColor(128, 128, 128, 128))
        h.addToGroup(self.driver2)
        self.driver1=QGraphicsEllipseItem(154, -25, 50, 50)
        self.driver1.setZValue(1.0)
        self.driver1.setBrush(QColor(128, 128, 128, 128))
        h.addToGroup(self.driver1)

        rot_center1 = InteractiveGroup("rot1")
        self.rotind1=QGraphicsRectItem(-5, -55, 10, 60)
        self.rotind1.setZValue(2.0)
        self.rotind1.setBrush(QColor(150, 0, 0))
        rot_center1.addToGroup(self.rotind1)
        h.addToGroup(rot_center1)

        rot_center2 = InteractiveGroup("rot2")
        self.rotind2=QGraphicsRectItem(-5, -55, 10, 60)
        self.rotind2.setZValue(2.0)
        self.rotind2.setBrush(QColor(150, 0, 0))
        rot_center2.addToGroup(self.rotind2)
        h.addToGroup(rot_center2)


        v.setPos(-3500, 0)
        h.setPos(0, -150)
        rot_center1.setPos(179, 0)
        rot_center2.setPos(-179, 0)

    def on_client_cache(self, data):
        (time, key, op, value) = data
        if '/' not in key:
            return
        ldevname, subkey = key.rsplit('/', 1)

        if ldevname == self.posx and subkey == 'value':
            value = cache_load(value)
            if self.selene==2:
                value = -value
            else:
                value = value-7250
            self.vstage.setPos(value+self.offsetx, 0)
        elif ldevname==self.posz and subkey=='value':
            value=cache_load(value)
            self.hstage.setPos(0, 800-value-self.offsetz)
        elif ldevname==self.rotation1 and subkey=='value':
            value=cache_load(value)
            self.rotind1.setRotation(-value)
        elif ldevname==self.rotation2 and subkey=='value':
            value = cache_load(value)
            self.rotind2.setRotation(-value)
        elif ldevname == self.approach1 and subkey == 'status':
            status_id, text = cache_load(value)
            if status_id==BUSY:
                self.driver1.setBrush(QColor(200, 200, 64, 200))
                self.rotind1.setBrush(QColor(200, 200, 0))
            elif text.strip() in ['HexScrewFullyOut', 'InterlockBwd']:
                self.driver1.setBrush(QColor(64, 64, 128, 200))
                self.rotind1.setBrush(QColor(150, 0, 0))
            elif text.strip()=='HexScrewInserted':
                self.driver1.setBrush(QColor(64, 255, 64, 200))
                self.rotind1.setBrush(QColor(0, 255, 0))
            else:
                self.driver1.setBrush(QColor(255, 64, 64, 200))
                self.rotind1.setBrush(QColor(255, 0, 0))
        elif ldevname==self.approach2 and subkey=='status':
            status_id, text = cache_load(value)
            if status_id==BUSY:
                self.driver2.setBrush(QColor(200, 200, 64, 200))
                self.rotind2.setBrush(QColor(200, 200, 0))
            elif text.strip() in ['HexScrewFullyOut', 'InterlockBwd']:
                self.driver2.setBrush(QColor(64, 64, 128, 200))
                self.rotind2.setBrush(QColor(150, 0, 0))
            elif text.strip()=='HexScrewInserted':
                self.driver2.setBrush(QColor(64, 255, 64, 200))
                self.rotind2.setBrush(QColor(0, 255, 0))
            else:
                self.driver2.setBrush(QColor(255, 64, 64, 200))
                self.rotind2.setBrush(QColor(255, 0, 0))

    def on_client_connected(self):
        state = self.client.ask('getstatus')
        if not state:
            return
        devlist = [self.posx, self.posz, self.approach1, self.rotation1, self.approach2, self.rotation2]

        for devname in devlist:
            self._create_device_item(devname)

    def _create_device_item(self, devname):
        ldevname = devname.lower()
        # get all cache keys pertaining to the device
        params = self.client.getDeviceParams(devname)
        if not params:
            return

        # let the cache handler process all properties
        for key, value in params.items():
            self.on_client_cache((0, ldevname + '/' + key, OP_TELL,
                                  cache_dump(value)))

    def resizeEvent(self, value=None):
        self._view.fitInView(self.scene.sceneRect(), mode=Qt.KeepAspectRatio)

    def childSelected(self, name, item=None):
        self._currentSelection = name
        #print("Selection from ", name, " at ", item.pos().x(), item.pos().y())
        if hasattr(item, 'screw_group'):
            #print(f"  group: {item.screw_group} item: {item.screw_item}")
            self._selectionText.setText(self.title+f' (item={item.screw_item}, group={item.screw_group})')
            self._selectionText.setPos(-7250/2-self._selectionText.boundingRect().width()/2, -200)

    def childActivated(self, name, item):
        pass
        #print("Activatoin from ", name, " at ", item.pos().x(), item.pos().y())
        if hasattr(item, 'screw_group') and self.robot and item.screw_item>0:
            # print(f"  group: {item.screw_group} item: {item.screw_item}")
            # move to activated screw location
            self.client.tell('queue',
                             f'Moving to Screw ({item.screw_item},{item.screw_group})',
                             f'maw({self.robot}, ({item.screw_item},{item.screw_group}))\n{self.robot}.engage()')
