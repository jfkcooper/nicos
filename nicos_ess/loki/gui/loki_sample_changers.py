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
from nicos.guisupport.qt import QDialog, QTableWidget, QItemDelegate,\
    QLineEdit, QTableWidgetItem, Qt
from nicos_ess.loki.gui.loki_panel import LokiPanelBase
from nicos_ess.utilities.validators import DoubleValidator


class TableDelegate(QItemDelegate):
    # There is no direct validation call for `QTableWidget`. One straightforward
    # method is the use of delegations. Here, our delegate is a `QLineEdit`.
    def createEditor(self, parent, option, index):
        delegated_table = QLineEdit(parent)
        self.validate(delegated_table)
        return delegated_table

    @staticmethod
    def validate(delegated_table):
        _validator_values = {  # in units of mm
            'bottom': 0.0,
            'top': 1000.0,
            'decimal': 5,
        }
        validator = DoubleValidator(**_validator_values)
        delegated_table.setValidator(validator)


class ThermoCellHolderPositions(QDialog):

    def __init__(self, parent, client):
        QDialog.__init__(self, parent)
        self.client = client
        loadUi(self, findResource('nicos_ess/loki/gui/'
                                  'ui_files/sample_changers/'
                                  'thermo_cell_holder_positions.ui'))
        self.initialise_markups()
        for table in self._get_all_tables():
            table.setItemDelegate(TableDelegate())

        self._disable_all_positions_but_first()

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

    def _disable_all_positions_but_first(self):
        for table in self._get_all_tables():
            self._disable(table)

    def _disable(self, table):
        # Whenever an item is set to a `QTableWidget`, that widget takes the
        # ownership and the item cannot be set to another widget. Thus, we
        # create an instance of an item for each cell.
        for i in range(1, self.firstRowFirstTable.rowCount()):
            for j in range(self.firstRowFirstTable.columnCount()):
                table.setItem(i, j, self._configure_item())

    @staticmethod
    def _configure_item():
        item = QTableWidgetItem(str(0.0))
        item.setFlags(Qt.ItemIsEnabled)
        item.setBackground(Qt.lightGray)
        return item


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
