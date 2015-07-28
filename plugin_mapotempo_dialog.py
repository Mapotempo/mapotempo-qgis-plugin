# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginMapotempoDialog
                                 A QGIS plugin
 Plugin for Mapotempo API
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

import os

from PyQt4 import QtCore, QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'plugin_mapotempo_dialog_base.ui'))

FORM_CLASS_WIDGET, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'widget_base.ui'))

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class PluginMapotempoDialogBase(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(PluginMapotempoDialogBase, self).__init__(parent)
        self.setupUi(self)

        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(70, 30, 311, 27))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.lineEdit_2 = QtGui.QLineEdit(self)
        self.lineEdit_2.setGeometry(QtCore.QRect(70, 80, 311, 27))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(20, 30, 66, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(20, 80, 66, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.pushButton = QtGui.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(280, 110, 98, 27))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, PluginMapotempoDialogBase):
        PluginMapotempoDialogBase.setWindowTitle(
            _translate("PluginMapotempoDialogBase", "Parameters", None))
        self.pushButton.setText(
            _translate("PluginMapotempoDialogBase", "Save", None))
        self.label.setText(_translate("PluginMapotempoDialogBase", "Key", None))
        self.label_2.setText(
            _translate("PluginMapotempoDialogBase", "Host", None))

class DockWidget(QtGui.QDockWidget, FORM_CLASS_WIDGET):

    def __init__(self, parent=None):
        """Constructor."""
        super(DockWidget, self).__init__(parent)

        self.vehicleTab = {}

        self.setObjectName(_fromUtf8("DockWidget"))
        self.resize(383, 887)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(self.resolve('icons/connection.png')),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.pushButton.setIcon(icon2)
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_4 = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(self.resolve('icons/parameter.png')),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.pushButton_4.setIcon(icon3)
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.pushButton_2 = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(self.resolve('icons/refresh.png')),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.verticalLayout.addWidget(self.pushButton_2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_5 = QtGui.QLabel(self.dockWidgetContents)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_2.addWidget(self.label_5)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.comboBox = QtGui.QComboBox(self.dockWidgetContents)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.verticalLayout.addWidget(self.comboBox)
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.listWidget = QtGui.QListWidget(self.dockWidgetContents)
        self.listWidget.setMaximumSize(QtCore.QSize(16777215, 100))
        self.listWidget.setDragEnabled(True)
        self.listWidget.setDragDropOverwriteMode(True)
        self.listWidget.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout.addWidget(self.listWidget)
        self.treeView = QCustomTreeView()
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.treeView.setDragEnabled(True)
        self.treeView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.model = QtGui.QStandardItemModel()

        self.verticalLayout.addWidget(self.treeView)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.setWidget(self.dockWidgetContents)

        self.retranslateUi(self)

    def addVehicles(self, data, color, infoVehicle, activeTab):
        self.addItems(self.model, data.items(), activeTab, infoVehicle, color)
        self.model.setHeaderData(
            0,
            QtCore.Qt.Horizontal,
            _translate("PluginMapotempo", "routes", None))
        self.treeView.setModel(self.model)

    def addItems(self, parent, elements, activeTab, infoVehicle, color, bool=False):
        for text, children in elements:
            if bool:
                item = QtGui.QStandardItem(text)
                client =  text.split(' - ')
                if len(client) == 2:
                    item.setData(client[1])
                else:
                    item.setData(client[0])
                parent.appendRow(item)
                item.setCheckable(True)
                item.setCheckState(QtCore.Qt.Checked)
                if text in activeTab:
                    item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item = QtGui.QStandardItem(text + infoVehicle[text])
                item.setData(text)
                parent.appendRow(item)
                colorV = color[text]
                icon = QtGui.QIcon()
                pixmap = QtGui.QPixmap(20, 20)
                pixmap.fill(QtGui.QColor(str(colorV)))
                icon.addPixmap(
                    pixmap,
                    QtGui.QIcon.Normal,
                    QtGui.QIcon.Off)
                item.setIcon(icon)
            if children:
                self.addItems(
                    item,
                    children,
                    activeTab,
                    infoVehicle,
                    color=None,
                    bool=True)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "Mapotempo", None))
        self.pushButton_2.setText(_translate("DockWidget", "Refresh", None))
        self.label_5.setText(_translate("DockWidget", "", None))
        self.pushButton.setText(_translate("DockWidget", "Connection", None))
        self.pushButton_4.setText(_translate("DockWidget", "Parameter", None))
        self.label.setText(_translate("DockWidget", "Unplanned", None))

    def resolve(self, name, basepath=None):
        if not basepath:
            basepath = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(basepath, name)

class QCustomTreeView (QtGui.QTreeView):
    def __init__(self, parent = None):
        super(QCustomTreeView, self).__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.resize(360,240)

    def dragEnterEvent (self, eventQDragEnterEvent):
        sourceQCustomTreeView = eventQDragEnterEvent.source()
        if isinstance(sourceQCustomTreeView, QCustomTreeView):
            if self != sourceQCustomTreeView:
                sourceQCustomTreeView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
                eventQDragEnterEvent.accept()
            else:
                sourceQCustomTreeView.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
                QtGui.QTreeView.dragEnterEvent(self, eventQDragEnterEvent)
        else:
            QtGui.QTreeView.dragEnterEvent(self, eventQDragEnterEvent)

    def dropEvent (self, eventQDropEvent):
        sourceQCustomTreeView = eventQDropEvent.source()
        if isinstance(sourceQCustomTreeView, QCustomTreeView):
            if self != sourceQCustomTreeView:
                sourceQCustomTreeView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
                sourceQTreeViewItem = sourceQCustomTreeView.currentItem()
                isFound = False
                for column in range(0, self.columnCount()):
                    sourceQString = sourceQTreeViewItem.text(column)
                    listsFoundQTreeViewItem = self.findItems(sourceQString, QtCore.Qt.MatchExactly, column)
                    if listsFoundQTreeViewItem:
                        isFound = True
                        break
                if not isFound:
                    (sourceQTreeViewItem.parent() or sourceQCustomTreeView.invisibleRootItem()).removeChild(sourceQTreeViewItem)
                    self.invisibleRootItem().addChild(sourceQTreeViewItem)
            else:
                sourceQCustomTreeView.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
                QtGui.QTreeView.dropEvent(self, eventQDropEvent)
        else:
            QtGui.QTreeView.dropEvent(self, eventQDropEvent)