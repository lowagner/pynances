#!/usr/bin/env python
__version__ = "0.1a"

import sys
import platform
 
import PySide
from PySide.QtGui import (QApplication, QMainWindow, QMessageBox, QIcon, QFileDialog, QStatusBar, QResizeEvent, QPalette)

from mainwindow import Ui_MainWindow as Ui


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # Store Ui() as class variable self.ui
        self.ui = Ui()
        self.ui.setupUi(self)
        self.setWindowTitle('Qif') 
        self.ui.accountsWidget.setStatusTip("Accounts")
        self.ui.accountsWidget.setFrameShape(PySide.QtGui.QFrame.Box)

        self.ui.totalsAccounts.setStatusTip("Account Totals")
        self.ui.totalsAccounts.setFrameShape(PySide.QtGui.QFrame.Box)

        self.ui.categoriesWidget.setStatusTip("Spending/Saving Categories")
        self.ui.categoriesWidget.setFrameShape(PySide.QtGui.QFrame.Box)

        self.ui.totalsCategories.setStatusTip("Category Totals")
        self.ui.totalsCategories.setFrameShape(PySide.QtGui.QFrame.Box)

        self.ui.textEdit.setStatusTip("File Editor")
        self.ui.textEdit.setFrameShape(PySide.QtGui.QFrame.Box)
        
        wincol = self.palette().color(QPalette.Window); 
        self.ui.lineEdit.setStyleSheet("background-color: %s;"%wincol.name())

    def requestDirectory(self):
        getdir = QFileDialog.getExistingDirectory(self, "Set Working Directory", ".",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    def about(self):
        '''Popup a box with about message.'''
        QMessageBox.about(self, "About Qif, PySide, and Platform",
                """<b> qif.py version %s </b> 
                <p>Copyright &copy; 2016 by Lucas Wagner, MIT License.</p> 
                <p>Python %s -  PySide version %s - Qt version %s on %s""" %
                (__version__, platform.python_version(), PySide.__version__,
                 PySide.QtCore.__version__, platform.system()))                        
    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        h = event.size().height()
        w = event.size().width()
        if sys.platform == "darwin":
            if w < h or w < 600:
                # not very wide.
                self.ui.accountsWidget.resize(w/2-4, h/2-28)
                self.ui.accountsWidget.move(2,2)
                self.ui.totalsAccounts.resize(w/2-4,80)
                self.ui.totalsAccounts.move(2,h/2-22)
                self.ui.categoriesWidget.resize(w/2-4, h/2-28)
                self.ui.categoriesWidget.move(w/2+2, 2)
                self.ui.totalsCategories.resize(w/2-4,80)
                self.ui.totalsCategories.move(w/2+2,h/2-22)

                self.ui.textEdit.resize(w-4, h/2-104)
                self.ui.textEdit.move(2, h/2+62)
            else:
                # wide screen
                self.ui.accountsWidget.resize(w/4-4, h-128)
                self.ui.accountsWidget.move(2,2)
                self.ui.totalsAccounts.resize(w/4-4,80)
                self.ui.totalsAccounts.move(2,h-122)
                self.ui.categoriesWidget.resize(w/4-4, h-128)
                self.ui.categoriesWidget.move(w/4+2, 2)
                self.ui.totalsCategories.resize(w/4-4,80)
                self.ui.totalsCategories.move(w/4+2,h-122)

                self.ui.textEdit.resize(w/2-4, h-44)
                self.ui.textEdit.move(w/2+2, 2)
        else: # linux and windows
            if w < h or w < 600:
                # not very wide.
                self.ui.accountsWidget.resize(w/2-4, h/2-46)
                self.ui.accountsWidget.move(2,0)
                self.ui.totalsAccounts.resize(w/2-4,80)
                self.ui.totalsAccounts.move(2,h/2-42)
                self.ui.categoriesWidget.resize(w/2-4, h/2-46)
                self.ui.categoriesWidget.move(w/2+2, 0)
                self.ui.totalsCategories.resize(w/2-4,80)
                self.ui.totalsCategories.move(w/2+2,h/2-42)

                self.ui.textEdit.resize(w-4, h/2-129)
                self.ui.textEdit.move(2, h/2+42)
                
                self.ui.lineEdit.resize(w-4, 32)
                self.ui.lineEdit.move(2, h-86)
            else:
                # wide screen
                self.ui.accountsWidget.resize(w/4-4, h-172)
                self.ui.accountsWidget.move(2,0)
                self.ui.totalsAccounts.resize(w/4-4,80)
                self.ui.totalsAccounts.move(2,h-168)
                self.ui.categoriesWidget.resize(w/4-4, h-172)
                self.ui.categoriesWidget.move(w/4+2, 0)
                self.ui.totalsCategories.resize(w/4-4,80)
                self.ui.totalsCategories.move(w/4+2,h-168)

                self.ui.textEdit.resize(w/2-4, h-88)
                self.ui.textEdit.move(w/2+2, 0)
                
                self.ui.lineEdit.resize(w-4, 32)
                self.ui.lineEdit.move(2, h-86)
        #self.ui.statusBar.showMessage("Resized...")
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    sys.exit(app.exec_())
    
