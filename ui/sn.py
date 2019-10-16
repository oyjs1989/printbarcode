# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sn.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SN(object):
    def setupUi(self, SN):
        SN.setObjectName("SN")
        SN.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(SN)
        self.centralwidget.setObjectName("centralwidget")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(320, 140, 160, 40))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(230, 220, 356, 44))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        SN.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(SN)
        self.statusbar.setObjectName("statusbar")
        SN.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(SN)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menuBar.setObjectName("menuBar")
        self.menuLogin = QtWidgets.QMenu(self.menuBar)
        self.menuLogin.setObjectName("menuLogin")
        self.menu_print_method = QtWidgets.QMenu(self.menuBar)
        self.menu_print_method.setObjectName("menu_print_method")
        SN.setMenuBar(self.menuBar)
        self.actionLogin = QtWidgets.QAction(SN)
        self.actionLogin.setObjectName("actionLogin")
        self.menuLogin.addAction(self.actionLogin)
        self.menuBar.addAction(self.menuLogin.menuAction())
        self.menuBar.addAction(self.menu_print_method.menuAction())

        self.retranslateUi(SN)
        QtCore.QMetaObject.connectSlotsByName(SN)

    def retranslateUi(self, SN):
        _translate = QtCore.QCoreApplication.translate
        SN.setWindowTitle(_translate("SN", "Odoo"))
        self.label_2.setText(_translate("SN", "打印"))
        self.label.setText(_translate("SN", "输入："))
        self.menuLogin.setTitle(_translate("SN", "用户"))
        self.menu_print_method.setTitle(_translate("SN", "选择打印方法"))
        self.actionLogin.setText(_translate("SN", "登录"))

