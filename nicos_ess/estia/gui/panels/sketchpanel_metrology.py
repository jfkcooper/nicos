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
A sketch display of the metrology cart to vizualize the components.
'''

from nicos.clients.gui.panels import Panel
from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, UNKNOWN, \
    WARN
from nicos.guisupport.qt import QGraphicsView, QGraphicsScene, QGraphicsItem, \
    QGraphicsItemGroup, QVBoxLayout, QGraphicsEllipseItem, QGraphicsRectItem, \
    QColor, QGraphicsSimpleTextItem, Qt, QFont, QTimer, QPixmap, QPen, QPolygonF, QPointF
from nicos.protocols.cache import cache_load, OP_TELL, cache_dump
from nicos.utils import findResource
import numpy as np

STATUS_COLORS = {
    OK: QColor(0, 150, 0),
    WARN: QColor(100, 100, 0),
    BUSY: QColor(50, 50, 0),
    NOTREACHED: QColor(100, 0, 100),
    DISABLED: QColor(0, 0, 0),
    ERROR: QColor(150, 0, 0),
    UNKNOWN: QColor(0, 0, 0),
}


from .graphics_helpers import InteractiveGroup, TransmittingGroup

class MetrologySketchPanel(Panel):
    _devinfo = {}

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self._view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self._view.setScene(self.scene)
        vbox.addWidget(self._view)

        self.channels = list(options.get('channels'))
        self.positions = list(options.get('positions'))
        self.cart_position = str(options.get('cart_position', 'mpos'))
        self.offsetx = float(options.get('offsetx', 0))
        self.selene = int(options.get('selene', 1))

        self.title = options.get('title', 'Metrology Selene %i'%self.selene)
        if self.selene==2:
            self.scene.setBackgroundBrush(QColor(230,200,200))
            self.title='(view inverted) '+self.title

        self.collimators = {}
        self.build_background()
        self.build_mirrors()
        self.build_cart()

        self._currentSelection = None

        client.cache.connect(self.on_client_cache)
        client.connected.connect(self.on_client_connected)

        QTimer.singleShot(1000, self.resizeEvent)

    def build_background(self):
        s = self.scene
        stone = QGraphicsRectItem(0, -475, 7250, 950)
        s.addItem(stone)
        stone.setZValue(-12.)
        stone.setBrush(QColor(50, 50, 50))

        indent = s.addRect(0, -250, 7250, 500)
        indent.setZValue(-11.)
        indent.setBrush(QColor(255, 255, 255, 50))

        refsurf = s.addRect(0, -280, 7250, 30)
        refsurf.setZValue(-11.)
        refsurf.setBrush(QColor(50, 50, 150, 100))
        refsurf = s.addRect(0, 220, 7250, 30)
        refsurf.setZValue(-11.)
        refsurf.setBrush(QColor(50, 50, 150, 100))

        rail = s.addRect(0, -320, 7250, 30)
        rail.setZValue(-10.)
        rail.setBrush(QColor(250, 250, 250))
        rail = s.addRect(0, 290, 7250, 30)
        rail.setZValue(-10.)
        rail.setBrush(QColor(250, 250, 250))

        logo = s.addPixmap(QPixmap(findResource('nicos_ess/estia/gui/estia_logo.png')))
        logo.setScale(0.333)
        logo.setZValue(-10.)
        logo.setPos(3625-logo.pixmap().width()//6, -logo.pixmap().height()//6)

        toppos, toptxt = self.build_collimator_horizontal(self.positions[0], False)
        s.addItem(toppos)
        toppos.setPos(7210, -220)
        botpos, bottxt = self.build_collimator_horizontal(self.positions[1], True)
        s.addItem(botpos)
        botpos.setPos(7210, 220)
        self.collimators[self.positions[0]] = (toppos, toptxt)
        self.collimators[self.positions[1]] = (botpos, bottxt)

        topline = s.addLine(500, -220, 7210, -220)
        topline.setZValue(-5.0)
        topline.setPen(QPen(QColor(255, 50, 50, 150), 5))

        botline = s.addLine(500, 220, 7210, 220)
        botline.setZValue(-5.0)
        botline.setPen(QPen(QColor(255, 50, 50, 150), 5))

        self.collimator_lines = [topline, botline]

        self._selectionText = QGraphicsSimpleTextItem(self.title)
        self._selectionText.setFont(QFont('sans', 54))
        s.addItem(self._selectionText)
        self._selectionText.setPos(7250/2-self._selectionText.boundingRect().width()/2, -580)

    def build_mirrors(self):
        s = self.scene
        # draw polygon shapes for each of the Selene mirrors, colors can later indicate adjustment state
        self.mirrors_H={}
        self.mirrors_V={}
        if self.selene!=2:
            zpre=1
        else:
            zpre=-1
        for group in range(15):
            center_x=265+group*480
            xellipse=(group-8)*480
            x_start=int(center_x-240)
            x_end=int(center_x+240)
            z_start=int(158*np.sqrt(6000**2-(xellipse-240)**2)/6000)
            z_end=int(158*np.sqrt(6000**2-(xellipse+240)**2)/6000)
            qt_polygon = QPolygonF()
            for px,py in [(x_start,zpre*z_start), (x_end,zpre*z_end),
                          (x_end, zpre*(z_end+40)), (x_start, zpre*(z_start+40)),
                          (x_start, zpre*z_start)]:

                qt_polygon.append(QPointF(px, py))
            self.mirrors_H[group]=s.addPolygon(qt_polygon, brush=QColor(255, 255, 255, 220))

            for px,py in [(x_start,zpre*z_start), (x_end,zpre*z_end),
                          (x_end, zpre*20), (x_start, zpre*20),
                          (x_start, zpre*z_start)]:
                qt_polygon.append(QPointF(px, py))
            self.mirrors_V[group]=s.addPolygon(qt_polygon, brush=QColor(255, 255, 255, 200))

            if self.selene==2:
                text = s.addText('E02-06-%02i-VU'%(group+1))
                textH = s.addText('E02-06-%02i-HU'%(group+1))
            else:
                text=s.addText('E02-02-%02i-VD'%(group+1))
                textH = s.addText('E02-02-%02i-HD'%(group+1))
            text.setFont(QFont('sans', 30))
            text.setPos(center_x-text.boundingRect().width()/2, zpre*80-15)
            text.setDefaultTextColor(QColor(160,160,160))
            textH.setFont(QFont('sans', 30))
            textH.setPos(center_x-text.boundingRect().width()/2,
                         zpre*(max(z_start, z_end)+10)-text.boundingRect().height()/2)
            textH.setDefaultTextColor(QColor(160,160,160))


    def build_cart(self):
        s = self.scene

        self.cart = TransmittingGroup()
        c = self.cart
        c.setZValue(10.)
        s.addItem(c)

        for CHi, pos, diagonal in self.channels:
            if diagonal:
                group, value = self.build_collimator_diagonal(CHi, pos[0]<0)
            else:
                group, value = self.build_collimator(CHi, pos[0]<0)
            group.setParentItem(c)
            group.setPos(pos[0], -pos[1])
            self.collimators[CHi] = (group, value)

        frame = QGraphicsRectItem(-135, -300, 270, 600)
        frame.setZValue(-1.0)
        frame.setBrush(QColor(128, 128, 128, 128))
        frame.setParentItem(c)
        c.setPos(350., 0.)

    def build_collimator(self, label, text_left=True):
        group = InteractiveGroup(label)
        outer = QGraphicsEllipseItem(-6, -6, 12, 12)
        outer.setBrush(STATUS_COLORS[UNKNOWN])
        group.addToGroup(outer)
        inner = QGraphicsEllipseItem(-3, -3, 6, 6)
        inner.setBrush(STATUS_COLORS[UNKNOWN])
        group.addToGroup(inner)
        text = QGraphicsSimpleTextItem(' '*14)
        font = QFont('sans', 24)
        font.setStyleHint(QFont.Monospace)
        text.setFont(font)
        group.addToGroup(text)
        title = QGraphicsSimpleTextItem(label)
        title.setFont(QFont('sans', 26, QFont.Bold))
        # background box for text
        if text_left:
            title.setPos(-title.boundingRect().width() - 20, -title.boundingRect().height() / 2)
            text.setPos(-text.boundingRect().width() - title.boundingRect().width() - 30,
                        -title.boundingRect().height() / 2)
        else:
            title.setPos(20,-title.boundingRect().height()/2)
            text.setPos(title.boundingRect().width()+35,-title.boundingRect().height()/2)
        group.addToGroup(title)
        return group, text

    def build_collimator_diagonal(self, label, text_left=True, point_down=True):
        group = InteractiveGroup(label)
        outer = QGraphicsRectItem(-6, -6, 12, 24)
        outer.setBrush(STATUS_COLORS[UNKNOWN])
        group.addToGroup(outer)
        if point_down:
            inner = QGraphicsRectItem(-3, -21-14, 6, 14)
        else:
            inner = QGraphicsRectItem(-3, 21, 6, 14)
        inner.setBrush(STATUS_COLORS[UNKNOWN])
        group.addToGroup(inner)
        text = QGraphicsSimpleTextItem(' '*14)
        font = QFont('sans', 24)
        font.setStyleHint(QFont.Monospace)
        text.setFont(font)
        group.addToGroup(text)
        title = QGraphicsSimpleTextItem(label)
        title.setFont(QFont('sans', 26, QFont.Bold))
        if text_left:
            title.setPos(-title.boundingRect().width() - 20, -title.boundingRect().height() / 2)
            text.setPos(-text.boundingRect().width() - title.boundingRect().width() - 30,
                        -title.boundingRect().height() / 2)
        else:
            title.setPos(20,-title.boundingRect().height()/2)
            text.setPos(title.boundingRect().width()+35,-title.boundingRect().height()/2)
        group.addToGroup(title)
        return group, text

    def build_collimator_horizontal(self, label, text_above=True):
        group = InteractiveGroup(label)
        outer = QGraphicsRectItem(-6, -6, 24, 12)
        outer.setBrush(STATUS_COLORS[UNKNOWN])
        group.addToGroup(outer)
        inner = QGraphicsRectItem(12, -3, 14, 6)
        inner.setBrush(STATUS_COLORS[UNKNOWN])
        group.addToGroup(inner)
        text = QGraphicsSimpleTextItem('0')
        text.setFont(QFont('sans', 24))
        group.addToGroup(text)
        title = QGraphicsSimpleTextItem(label)
        title.setFont(QFont('sans', 26, QFont.Bold))
        if text_above:
            title.setPos(-100, -80)
            text.setPos(-100, -48)
        else:
            title.setPos(-100, 20)
            text.setPos(-100,  62)
        group.addToGroup(title)
        return group, text

    def on_client_cache(self, data):
        (time, key, op, value) = data
        if '/' not in key:
            return
        ldevname, subkey = key.rsplit('/', 1)

        if ldevname in self.collimators:
            if subkey == 'status':
                value = cache_load(value)
                for item in self.collimators[ldevname][0].childItems():
                    if hasattr(item, 'setBrush'):
                        item.setBrush(STATUS_COLORS[value[0]])
                if ldevname == self._currentSelection:
                    self._selectionText.setBrush(STATUS_COLORS[value[0]])
            if subkey == 'value':
                value = cache_load(value)
                text = self.collimators[ldevname][1]
                if text.x()<0:
                    text.setText('%12.3f'%value)
                else:
                    text.setText('%.3f' % value)
                if ldevname == self._currentSelection:
                    self._selectionText.setText(
                        '%s: %.4f' % (self._currentSelection, value))
        elif ldevname == self.cart_position and subkey == 'value':
            value = cache_load(value) + self.offsetx
            #if self.selene==2:
                # selene 2 is oriented in opposite direction wrt beam
            #    value = 7250-value
            self.cart.setPos(value + 150, 0)
            self.collimator_lines[0].setLine(value+300, -220, 7210, -220)
            self.collimator_lines[1].setLine(value+300, 220, 7210, 220)

    def on_client_connected(self):
        state = self.client.ask('getstatus')
        if not state:
            return
        devlist = [ci[0] for ci in self.channels] + self.positions + ['mpos']

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

    def childSelected(self, name):
        self._currentSelection = name
        self.on_client_connected()

    def childActivated(self, name):
        print("Event from ", name)
