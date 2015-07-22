# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginMapotempoDialog
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
            _translate("PluginMapotempoDialogBase", "Plugin Mapotempo", None))
        self.pushButton.setText(
            _translate("PluginMapotempoDialogBase", "Save", None))
        self.label.setText(_translate("PluginMapotempoDialogBase", "Key", None))
        self.label_2.setText(
            _translate("PluginMapotempoDialogBase", "Host", None))

class Widget(QtGui.QDockWidget, FORM_CLASS_WIDGET):

    def __init__(self, parent=None):
        """Constructor."""
        super(Widget, self).__init__(parent)

        self.vehicleTab = {}
        self.label_4 = QtGui.QLabel(self)
        self.label_4.setGeometry(QtCore.QRect(0, 50, 151, 17))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(0, 70, 241, 27))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(0, 160, 241, 101))
        self.listWidget.setDragEnabled(True)
        self.listWidget.setDragDropOverwriteMode(True)
        self.listWidget.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, 140, 171, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.widget = QtGui.QWidget(self)
        self.widget.setGeometry(QtCore.QRect(0, 20, 241, 29))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton = QtGui.QPushButton(self.widget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(self.resolve('icons/connection.png')),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.pushButton.setIcon(icon2)
        self.pushButton_4 = QtGui.QPushButton(self.widget)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.horizontalLayout.addWidget(self.pushButton_4)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(self.resolve('icons/parameter.png')),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.pushButton_4.setIcon(icon3)
        self.widget1 = QtGui.QWidget(self)
        self.widget1.setGeometry(QtCore.QRect(0, 100, 241, 29))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget1)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.pushButton_2 = QtGui.QPushButton(self.widget1)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(self.resolve('icons/refresh.png')),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.label_5 = QtGui.QLabel(self.widget1)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_2.addWidget(self.label_5)
        self.treeView = QtGui.QTreeView(self)
        self.model = QtGui.QStandardItemModel()

        self.treeView.setGeometry(QtCore.QRect(0, 271, 241, 581))
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.treeView.setHeaderHidden(True)
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(0, 160, 201, 101))
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.listWidget.setDragEnabled(True)
        self.listWidget.setDragDropOverwriteMode(True)
        self.listWidget.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, 140, 171, 17))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(self)

    def addVehicles(self, data, color):
        self.addItems(self.model, data.items(), color)
        self.treeView.setModel(self.model)

    def addItems(self, parent, elements, color, bool=False):

        for text, children in elements:
            item = QtGui.QStandardItem(text)
            parent.appendRow(item)
            if bool:
                item.setCheckable(True)
                item.setCheckState(QtCore.Qt.Checked)
            else:
                colorV = color[text]
                icon = QtGui.QIcon()
                pixmap = QtGui.QPixmap(20, 20)
                pixmap.fill(QtGui.QColor(str(colorV)))
                path = QtGui.QPainterPath()
                # painter = QtGui.QPainter()
                # path.addEllipse(20, 20, 0, 0)
                # painter.setClipPath(path)
                # painter.drawPixmap(20, 20, 0, 0, pixmap)
                # icon.paint(painter, 0, 10 ,10 ,10)
                icon.addPixmap(
                    pixmap,
                    QtGui.QIcon.Normal,
                    QtGui.QIcon.Off)
                item.setIcon(icon)
            if children:
                self.addItems(item, children, color=None, bool=True)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "Mapotempo", None))
        self.pushButton_2.setText(_translate("DockWidget", "Refresh", None))
        self.label_4.setText(_translate("DockWidget", "Planning choice", None))
        self.label_5.setText(_translate("DockWidget", "", None))
        self.pushButton.setText(_translate("DockWidget", "Connection", None))
        self.pushButton_4.setText(_translate("DockWidget", "Parameter", None))
        self.label.setText(_translate("DockWidget", "Unplanned", None))

    def resolve(self, name, basepath=None):
        if not basepath:
            basepath = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(basepath, name)

# class Vehicle(QtGui.QWidget):
#     def __init__( self, name, parent=None):
#         super(Vehicle, self).__init__(parent)
#
#         # self.pushButton = QtGui.QPushButton('I am in Test widget')
#         self.widget = QtGui.QWidget()
#         self.widget.setGeometry(QtCore.QRect(30, 50, 241, 151))
#         self.widget.setObjectName(_fromUtf8("widget"))
#         self.verticalLayout = QtGui.QVBoxLayout(self.widget)
#         self.verticalLayout.setMargin(0)
#         self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
#         self.label = QtGui.QLabel(self.widget)
#         self.label.setObjectName(_fromUtf8("label"))
#         self.verticalLayout.addWidget(self.label)
#         self.listWidget = QtGui.QListWidget(self.widget)
#         self.listWidget.setDragEnabled(True)
#         self.listWidget.setDragDropOverwriteMode(True)
#         self.listWidget.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
#         self.listWidget.setObjectName(_fromUtf8("listWidget"))
#         self.verticalLayout.addWidget(self.listWidget)
#         self.label.setText(_translate("Form", name, None))
#
#         layout = QtGui.QHBoxLayout()
#         layout.addWidget(self.widget)
#         self.setLayout(layout)
