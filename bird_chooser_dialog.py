# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BirdChooserDialog
                                 A QGIS plugin
 Show bird observations
                             -------------------
        begin                : 2015-11-05
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Jerome
        email                : jerome@guelat.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import psycopg2
from PyQt4 import QtGui, uic

from qgis.core import QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry, QgsMarkerSymbolV2, QgsMessageLog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bird_chooser_dialog_base.ui'))


class BirdChooserDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(BirdChooserDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        # Connecter les slots
        self._connectSlots()
        #self.conn = psycopg2.connect(database = "jguelat", user = "jguelat", password = "")
        self.conn = psycopg2.connect(service = "local_jguelat")

    def _connectSlots(self):
        self.tableCombo.activated.connect(self.getSpecies)
        # Quand la fenetre est fermee (d'une maniere ou d'une autre)
        self.finished.connect(self.closeConnection)
        self.addLayerButton.clicked.connect(self.addLayer)

    def getSpecies(self):
        self.speciesCombo.clear()
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT species_id from " + self.tableCombo.currentText() + " ORDER BY species_id")
        rows = cur.fetchall()

        self.speciesCombo.addItems([str(elem[0]) for elem in rows])

        self.addLayerButton.setEnabled(True)

        cur.close()

    def addLayer(self):
        uri = QgsDataSourceURI()
        # set host name, port, database name, username and password
        #uri.setConnection("localhost", "5432", "jguelat", "jguelat", "")
        uri.setConnection("local_jguelat", "", "", "")
        # set database schema, table name, geometry column and optionally subset (WHERE clause)
        uri.setDataSource("public", self.tableCombo.currentText(), "geom", "species_id = " + self.speciesCombo.currentText())
        #vlayer = self.iface.addVectorLayer(uri.uri(), "Species " + self.speciesCombo.currentText(), "postgres")
        vlayer = QgsVectorLayer(uri.uri(), "Species " + self.speciesCombo.currentText(), "postgres")
        props = vlayer.rendererV2().symbol().symbolLayer(0).properties()
        props['size'] = '3'
        props['color'] = 'blue'
        vlayer.rendererV2().setSymbol(QgsMarkerSymbolV2.createSimple(props))
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        QgsMessageLog.logMessage("Tout est OK", 'BirdChooser', QgsMessageLog.INFO)

    def closeConnection(self):
        self.conn.close()
