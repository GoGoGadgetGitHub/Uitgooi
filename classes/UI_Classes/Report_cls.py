from UI import Ui_Report
from PyQt6.QtWidgets import QDialog, QTableWidgetItem


class Report(QDialog, Ui_Report):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Report")
        self.par = parent
        self.packagesOrdered = parent.packagesOrdered
        self.PackcagesCopied = parent.packagesCopied
        self.errors = parent.errors
        self.setup_table()
        self.show_errors()
        
        self.btnDone.clicked.connect(self.done_click)

    def done_click(self):
        self.par.reset()
        self.hide()

    def setup_table(self):
        self.tblOrders.setRowCount(len(self.packagesOrdered))
        self.tblOrders.setColumnCount(3)
        self.tblOrders.setHorizontalHeaderLabels(["Package", "Ordered", "Copied"])
        for i, package in enumerate(self.packagesOrdered):
            self.tblOrders.setItem(i, 0, QTableWidgetItem(package))
            self.tblOrders.setItem(i, 1, QTableWidgetItem(str(self.packagesOrdered[package])))
            self.tblOrders.setItem(i, 2, QTableWidgetItem(str(self.PackcagesCopied[package])))
        self.tblOrders.resizeColumnsToContents()
    
    def show_errors(self):
        self.edtErrors.setText("\n".join(self.errors))