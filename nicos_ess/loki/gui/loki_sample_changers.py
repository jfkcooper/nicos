#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   AÜC Hardal <umit.hardal@ess.eu>
#
# *****************************************************************************

"""LoKI Sample Changers dialog."""
import itertools

from nicos.clients.gui.utils import loadUi
from nicos.utils import findResource
from nicos.guisupport.qt import QDialog, QTableWidget
from nicos_ess.loki.gui.loki_panel import LokiPanelBase


class ThermoCellHolderPositions(QDialog):

    def __init__(self, parent, client):
        QDialog.__init__(self, parent)
        self.client = client
        loadUi(self, findResource('nicos_ess/loki/gui/'
                                  'ui_files/sample_changers/'
                                  'thermo_cell_holder_positions.ui'))
        self.initialise_markups()

    def initialise_markups(self):
        self.setWindowTitle('Cartridge Settings')
        self.setStyleSheet("background-color: whitesmoke;")
        for table in self._get_all_tables():
            table.setStyleSheet("background-color: white;")

    def _get_all_tables(self):
        _tables = itertools.chain(
                self.topRowGroup.findChildren(QTableWidget),
                self.bottomRowGroup.findChildren(QTableWidget)
            )
        return _tables


class ThermoCellHolderSettings(LokiPanelBase):
    def __init__(self, client, frame, parent, options):
        super().__init__(parent, client, options)
        self.client = client
        self.frame = frame
        loadUi(self.frame, findResource('nicos_ess/loki/gui/'
                                        'ui_files/sample_changers/'
                                        'thermo_cell_holder_settings.ui'))
        self.frame.cartridgeSettings.clicked.connect(
            self._active_holder_position_settings)

    def _active_holder_position_settings(self):
        dlg = ThermoCellHolderPositions(self, self.client)
        if not dlg.exec_():
            return

