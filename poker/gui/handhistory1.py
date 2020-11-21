# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'handhistory1.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Handhistory1(object):
    def setupUi(self, Handhistory1):
        Handhistory1.setObjectName("Handhistory1")
        Handhistory1.resize(569, 244)
        self.tableWidget = QtWidgets.QTableWidget(Handhistory1)
        self.tableWidget.setGeometry(QtCore.QRect(30, 40, 461, 181))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 0, item)

        self.retranslateUi(Handhistory1)
        QtCore.QMetaObject.connectSlotsByName(Handhistory1)

    def retranslateUi(self, Handhistory1):
        _translate = QtCore.QCoreApplication.translate
        Handhistory1.setWindowTitle(_translate("Handhistory1", "Form"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("Handhistory1", "player1"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("Handhistory1", "player2"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("Handhistory1", "player3"))
        item = self.tableWidget.verticalHeaderItem(3)
        item.setText(_translate("Handhistory1", "player4"))
        item = self.tableWidget.verticalHeaderItem(4)
        item.setText(_translate("Handhistory1", "player5"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Handhistory1", "prefolp"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Handhistory1", "flop"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Handhistory1", "turn"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Handhistory1", "river"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setSortingEnabled(__sortingEnabled)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Handhistory1 = QtWidgets.QWidget()
    ui = Ui_Handhistory1()
    ui.setupUi(Handhistory1)
    Handhistory1.show()
    sys.exit(app.exec_())

