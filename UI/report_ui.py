# Form implementation generated from reading ui file '/home/saai/Documents/lern/ABF/ABF Verwerkign/Brenda/UI/QtDes/report.ui'
#
# Created by: PyQt6 UI code generator 6.8.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Report(object):
    def setupUi(self, Report):
        Report.setObjectName("Report")
        Report.resize(513, 364)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Report)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(parent=Report)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tblOrders = QtWidgets.QTableWidget(parent=self.groupBox_2)
        self.tblOrders.setObjectName("tblOrders")
        self.tblOrders.setColumnCount(0)
        self.tblOrders.setRowCount(0)
        self.verticalLayout.addWidget(self.tblOrders)
        self.btnDone = QtWidgets.QPushButton(parent=self.groupBox_2)
        self.btnDone.setObjectName("btnDone")
        self.verticalLayout.addWidget(self.btnDone)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(parent=Report)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.edtErrors = QtWidgets.QTextBrowser(parent=self.groupBox)
        self.edtErrors.setObjectName("edtErrors")
        self.horizontalLayout_2.addWidget(self.edtErrors)
        self.horizontalLayout.addWidget(self.groupBox)

        self.retranslateUi(Report)
        QtCore.QMetaObject.connectSlotsByName(Report)

    def retranslateUi(self, Report):
        _translate = QtCore.QCoreApplication.translate
        Report.setWindowTitle(_translate("Report", "Dialog"))
        self.groupBox_2.setTitle(_translate("Report", "Orders"))
        self.btnDone.setText(_translate("Report", "Done!"))
        self.groupBox.setTitle(_translate("Report", "Errors"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Report = QtWidgets.QDialog()
    ui = Ui_Report()
    ui.setupUi(Report)
    Report.show()
    sys.exit(app.exec())
