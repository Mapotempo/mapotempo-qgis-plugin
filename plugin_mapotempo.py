# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginMapotempo
                                 A QGIS plugin
 test
                              -------------------
        begin                : 2015-06-19
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Darius Matboo
        email                : dariusmatboo@mapotempo.com
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
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QAction, QIcon

try:
    from PyQt4.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = str

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

import resources_rc

from plugin_mapotempo_dialog import PluginMapotempoDialogBase, Widget

from plugin_mapotempo_handle import PluginMapotempoHandle
from plugin_mapotempo_layer import PluginMapotempoLayer
from translate import Translate

class PluginMapotempo:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        self.iface = iface
        self.translate = Translate()
        self.running = False
        # Declare instance attributes
        self.actions = []
        self.menu = self.translate.tr(u'&Plugin Mapotempo')
        self.toolbar = self.iface.addToolBar(u'PluginMapotempo')
        self.toolbar.setObjectName(u'PluginMapotempo')

        self.dlg = PluginMapotempoDialogBase()

        self.dock = Widget()

        #instance
        self.layer_inst = PluginMapotempoLayer(
            self.dlg, self.dock, self.iface, self.translate)
        self.handle = PluginMapotempoHandle(
            self.layer_inst, self.dlg, self.dock, self.translate)
        self.layer_inst.setHandler(self.handle)

        self.dlg.pushButton.clicked.connect(self.handle.handleButtonSave)

        self.dock.pushButton.clicked.connect(self.handle.handleButtonConnect)
        self.dock.pushButton_2.clicked.connect(self.layer_inst.refresh)
        self.dock.pushButton_4.clicked.connect(self.handle.HandleParam)
        self.dock.comboBox.activated.connect(self.handle.HandleSelect)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/mapotempo-qgis-plugin/icons/icon.png'
        self.add_action(
            icon_path,
            text=self.translate.tr(u'Plugin Mapotempo'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.translate.tr(u'&Plugin Mapotempo'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
