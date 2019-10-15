# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_main(object):
    def setupUi(self, main):
        main.setObjectName("main")
        main.resize(811, 579)
        self.centralwidget = QtWidgets.QWidget(main)
        self.centralwidget.setObjectName("centralwidget")
        self.Lable = QtWidgets.QLabel(self.centralwidget)
        self.Lable.setGeometry(QtCore.QRect(320, 140, 160, 40))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.Lable.setFont(font)
        self.Lable.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.Lable.setAlignment(QtCore.Qt.AlignCenter)
        self.Lable.setObjectName("Lable")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(150, 260, 511, 80))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_11 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 1)
        font = QtGui.QFont()
        font.setPointSize(20)
        main.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(main)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 811, 23))
        self.menuBar.setObjectName("menuBar")
        self.menuLogin = QtWidgets.QMenu(self.menuBar)
        self.menuLogin.setObjectName("menuLogin")
        self.menuERP = QtWidgets.QMenu(self.menuBar)
        self.menuERP.setObjectName("menuERP")
        self.print_method = QtWidgets.QMenu(self.menuERP)
        self.print_method.setObjectName("print_method")
        self.print_model = QtWidgets.QMenu(self.menuERP)
        self.print_model.setObjectName("print_model")
        main.setMenuBar(self.menuBar)
        self.statusBar = QtWidgets.QStatusBar(main)
        self.statusBar.setEnabled(True)
        self.statusBar.setObjectName("statusBar")
        main.setStatusBar(self.statusBar)
        self.actionLogin = QtWidgets.QAction(main)
        self.actionLogin.setObjectName("actionLogin")
        self.actionselectbartenderpath = QtWidgets.QAction(main)
        self.actionselectbartenderpath.setObjectName("actionselectbartenderpath")
        self.menuLogin.addAction(self.actionLogin)
        self.menuERP.addAction(self.print_method.menuAction())
        self.menuERP.addAction(self.print_model.menuAction())
        self.menuERP.addAction(self.actionselectbartenderpath)
        self.menuBar.addAction(self.menuLogin.menuAction())
        self.menuBar.addAction(self.menuERP.menuAction())

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)

    def retranslateUi(self, main):
        _translate = QtCore.QCoreApplication.translate
        main.setWindowTitle(_translate("main", "Odoo"))
        self.Lable.setText(_translate("main", "扫描打印"))
        self.label_11.setText(_translate("main", "请输入："))
        self.menuLogin.setTitle(_translate("main", "用户"))
        self.menuERP.setTitle(_translate("main", "扫描配置"))
        self.print_method.setTitle(_translate("main", "打印方法"))
        self.print_model.setTitle(_translate("main", "打印模型"))
        self.actionLogin.setText(_translate("main", "登录"))
        self.actionselectbartenderpath.setText(_translate("main", "打印软件路径"))

