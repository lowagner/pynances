#!/usr/bin/env python
__version__ = "0.1a"

from mbf import *

import sys
import platform
 
import PySide
from PySide.QtGui import (QApplication, QMainWindow, QMessageBox, QIcon, QFileDialog, QStatusBar, QResizeEvent, QPalette)
from PySide import QtCore

from mainwindow import Ui_MainWindow as Ui

class MainWindow(QMainWindow):
    def __init__(self, args, parent=None):
        super(MainWindow, self).__init__(parent)
     
        self.openfile = None
        self.filename = "UNKNOWN FILE"

        # Store Ui() as class variable self.ui
        self.ui = Ui()
        self.ui.setupUi(self)
        self.setWindowTitle('Qif') 

        self.ui.accountsWidget.setStatusTip("Accounts")
        self.ui.accountsWidget.setFrameShape(PySide.QtGui.QFrame.Box)
        self.ui.accountsWidget.installEventFilter(self)
        self.ui.accountsWidget.itemDoubleClicked.connect(self.doubleClickAccount)
        self.ui.accountsWidget.itemClicked.connect(self.singleClickAccount)
        #print self.ui.accountsWidget.__dict__.keys()

        self.ui.totalsAccounts.setStatusTip("Account Totals")
        self.ui.totalsAccounts.setFrameShape(PySide.QtGui.QFrame.Box)
        self.ui.totalsAccounts.installEventFilter(self)

        self.ui.categoriesWidget.setStatusTip("Spending/Saving Categories")
        self.ui.categoriesWidget.setFrameShape(PySide.QtGui.QFrame.Box)
        self.ui.categoriesWidget.installEventFilter(self)
        self.ui.categoriesWidget.itemDoubleClicked.connect(self.doubleClickCategory)
        self.ui.categoriesWidget.itemClicked.connect(self.singleClickCategory)

        self.ui.totalsCategories.setStatusTip("Category Totals")
        self.ui.totalsCategories.setFrameShape(PySide.QtGui.QFrame.Box)
        self.ui.totalsCategories.installEventFilter(self)

        self.ui.textEdit.setStatusTip("File Editor")
        self.ui.textEdit.setFrameShape(PySide.QtGui.QFrame.Box)
        self.ui.textEdit.installEventFilter(self)
        self.ui.textEdit.setAcceptRichText(False)
        
        wincol = self.palette().color(QPalette.Window); 
        self.ui.lineEdit.setStyleSheet("background-color: %s;"%wincol.name())
        self.ui.lineEdit.setStatusTip("Command Line")
        self.ui.lineEdit.installEventFilter(self)

        self.ui.centralWidget.installEventFilter(self)

        self.history = History()
        
        # read in settings to determine whether we should use single click or not.
        #self.ui.actionSingleClickToOpen.setChecked(True)
        self.ui.actionSaveFile.triggered.connect(self.saveOpenFile)

        # read in settings to determine if there's a working directory:
        root = "." # use this as a guess for root directory
        self.rootdir, self.YYYY, self.mm = getrootYYYYmm(args, root)
        self.showAll()

        self.ui.centralWidget.setFocus(QtCore.Qt.OtherFocusReason)

    def requestDirectory(self):
        self.rootdir = QFileDialog.getExistingDirectory(self, 
            "Set Working Directory", ".",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.showAll()

    def about(self):
        '''Popup a box with about message.'''
        QMessageBox.about(self, "About Qif, PySide, and Platform",
                """<b> qif.py version %s </b> 
                <p>Copyright &copy; 2016 by Lucas Wagner, MIT License.</p> 
                <p>Python %s -  PySide version %s - Qt version %s on %s""" %
                (__version__, platform.python_version(), PySide.__version__,
                 PySide.QtCore.__version__, platform.system()))                        

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if widget == self.ui.lineEdit: # command line
                if key == QtCore.Qt.Key_Escape:
                    self.history.clearCommand(self.ui.lineEdit.text())
                    self.ui.lineEdit.setText("")
                    self.ui.centralWidget.setFocus(QtCore.Qt.OtherFocusReason)
                    return True
                elif key == QtCore.Qt.Key_Return:
                    thetext = self.ui.lineEdit.text()
                    self.execute(thetext)
                    self.history.appendCommand(thetext)
                    self.ui.lineEdit.setText("")
                    return True
                elif key == QtCore.Qt.Key_Up:
                    self.ui.lineEdit.setText(
                        self.history.previousCommand(self.ui.lineEdit.text())
                    )
                    return True
                elif key == QtCore.Qt.Key_Down:
                    self.ui.lineEdit.setText(
                        self.history.nextCommand(self.ui.lineEdit.text())
                    )
                    return True
            else:
                if key == QtCore.Qt.Key_Escape:
                    if widget == self.ui.centralWidget:
                        self.ui.lineEdit.setFocus(QtCore.Qt.OtherFocusReason)
                    else:
                        self.ui.centralWidget.setFocus(QtCore.Qt.OtherFocusReason)
                    return True
                elif widget == self.ui.textEdit:
                    # we're in the textEdit
                    if self.openfile:
                        self.alert("Editing %s"%self.filename)
                    # don't return True, we want the key to go through to the textEdit
                elif (key == QtCore.Qt.Key_Slash or 
                    key == QtCore.Qt.Key_Question or 
                    key == QtCore.Qt.Key_Colon or
                    key == QtCore.Qt.Key_Semicolon):
                    self.ui.lineEdit.setFocus(QtCore.Qt.OtherFocusReason)
                    return True
                elif widget == self.ui.centralWidget:
                    if key == QtCore.Qt.Key_S:
                        self.saveOpenFile()
                        return True
                else:
                    if key == QtCore.Qt.Key_Return:
                        if widget == self.ui.categoriesWidget:
                            selitems = widget.selectedItems()
                            if selitems:
                                self.loadCategoryItem(selitems[0])
                        elif widget == self.ui.accountsWidget:
                            selitems = widget.selectedItems()
                            if selitems:
                                self.loadAccountItem(selitems[0])
                        return True
        return False

    def singleClickAccount(self, account):
        if self.ui.actionSingleClickToOpen.isChecked():
            self.loadAccountItem(account)

    def doubleClickAccount(self, account):
        if not self.ui.actionSingleClickToOpen.isChecked():
            self.loadAccountItem(account)
    
    def singleClickCategory(self, category):
        if self.ui.actionSingleClickToOpen.isChecked():
            self.loadCategoryItem(category)

    def doubleClickCategory(self, category):
        if not self.ui.actionSingleClickToOpen.isChecked():
            self.loadCategoryItem(category)

    def loadAccountItem(self, account):
        filename = account.text().split("\n")[0]
        # find first parentheses group:
        filename = filename[filename.find("(")+1:filename.find(")")]
        self.ui.categoriesWidget.clearSelection()
        self.loadFile(filename)

    def loadCategoryItem(self, category):
        filename = category.text().split("\n")[0]
        if "BUSINESS" not in filename:
            self.ui.accountsWidget.clearSelection()
            self.loadFile(filename)

    def alert(self, text):
        self.ui.statusBar.showMessage(text)

    def execute(self, command):
        self.ui.statusBar.showMessage("executing %s"%command)

        if len(command) > 0:
            if command == "q" or command == "quit" or command == "exit":
                self.close()
            else:
                split = command.split()
                if split[0] == "s" or split[0] == "save":
                    self.saveOpenFile()

                elif split[0] == "e" or split[0] == "edit":
                    if len(split) == 1:
                        self.loadFile("scratch")
                    else: 
                        self.loadFile(split[1])
                    return # return to avoid setting focus to the default

                elif split[0] == "load" or split[0] == "open" or split[0] == "o":
                    if len(split) == 1:
                        self.alert("use load YYYY/mm, or open mm")
                    else:
                        root, YYYY, mm = getrootYYYYmm(split, self.rootdir)
                        if root:
                            self.rootdir = root
                            self.YYYY = YYYY
                            self.mm = mm
                            self.showAll()
                        else:
                            self.alert("Invalid directory!")
                
                elif split[0] == "reload":
                    self.showAll()

                elif command == "generate":
                    if self.month.generatenextmonth():
                        self.alert("next month already exists.  type GENERATE to force.")
                    else:
                        self.alert("%s generated!"%self.month.nextyearmonth)
                
                elif command == "GENERATE":
                    self.month.generatenextmonth( True )
                    self.alert("%s re-generated!"%self.month.nextyearmonth)

                else:
                    self.alert('unknown command: '+command)

        self.ui.centralWidget.setFocus(QtCore.Qt.OtherFocusReason) # default focus after running a command

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
                
                self.ui.lineEdit.resize(w-4, 32)
                self.ui.lineEdit.move(2, h-50)
            else:
                # wide screen
                self.ui.accountsWidget.resize(w/4-4, h-138)
                self.ui.accountsWidget.move(2,2)
                self.ui.totalsAccounts.resize(w/4-4,80)
                self.ui.totalsAccounts.move(2,h-132)
                self.ui.categoriesWidget.resize(w/4-4, h-138)
                self.ui.categoriesWidget.move(w/4+2, 2)
                self.ui.totalsCategories.resize(w/4-4,80)
                self.ui.totalsCategories.move(w/4+2,h-132)

                self.ui.textEdit.resize(w/2-4, h-54)
                self.ui.textEdit.move(w/2+2, 2)
                
                self.ui.lineEdit.resize(w-4, 32)
                self.ui.lineEdit.move(2, h-50)
        else: # linux and windows
            if w < h or w < 600:
                # not very wide.
                self.ui.accountsWidget.resize(w/2-4, h/2-46)
                self.ui.accountsWidget.move(2,0)
                self.ui.totalsAccounts.resize(w/2-4,90)
                self.ui.totalsAccounts.move(2,h/2-42)
                self.ui.categoriesWidget.resize(w/2-4, h/2-46)
                self.ui.categoriesWidget.move(w/2+2, 0)
                self.ui.totalsCategories.resize(w/2-4,90)
                self.ui.totalsCategories.move(w/2+2,h/2-42)

                self.ui.textEdit.resize(w-4, h/2-139)
                self.ui.textEdit.move(2, h/2+52)
                
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
   
    def showAll(self):
        self.ui.accountsWidget.clear()
        self.ui.totalsAccounts.clear()
        self.ui.categoriesWidget.clear()
        self.ui.totalsCategories.clear()

        if self.rootdir:
            self.month = Month(self.rootdir, self.YYYY, self.mm)
            self.month.grandtotal()
            self.showAccounts()
            self.showCategories()
        else:
            self.ui.accountsWidget.addItem("Choose a working directory.")

    def showAccounts(self):
        starttotaldough = Dough(0)
        endtotaldough = Dough(0)

        accounts = self.month.accountlist.keys()
        accounts.sort()
        for account in accounts:
            accountname = self.month.accountlist[account]
            itemtext = [ accountname, " (%s):"%account ]
            try:
                sbalance = self.month.categories[account.upper()].metavalues["startingbalance"]
            except KeyError:
                sbalance = Dough(0)
            itemtext.append("\n start ")
            itemtext.append(str(sbalance))
            starttotaldough += sbalance

            ebalance = self.month.categories[account.upper()].metavalues["endingbalance"]
            itemtext.append("\n   end ")
            itemtext.append(str(ebalance))
            endtotaldough += ebalance
            
            self.ui.accountsWidget.addItem("".join(itemtext))

        self.ui.totalsAccounts.addItem("".join(
            ["Totals:",
             "\n start ", str(starttotaldough.clean()), 
             "\n delta ", str(endtotaldough-starttotaldough), 
             "\n   end ", str(endtotaldough.clean())]
        ))

    def showCategory(self, cat):
        # if not an account, it's a category we can analyze more
        if cat.metaflags["business"]:
            itemtext = ["Business ", str(cat.name)]
        else:
            itemtext = [str(cat.name)]

        if cat.metaflags["income"]:
            catactual = cat.metavalues["changeactual"]
            catbudget = cat.metavalues["changebudget"]
            if catactual != catbudget:
                catend = cat.metavalues["endingbalance"]
                if catend != 0:
                    itemtext.append("\n average "+str(catbudget)) 
                    itemtext.append("\n   swing "+str(catend)) 
                else:
                    itemtext.append("\n     got "+str(catactual)) 
                    itemtext.append("\n average "+str(catbudget)) 
            else:
                itemtext.append("\n     got "+str(catactual)) 
        else:
            try:
                catbudget = cat.metavalues["budget"].clean()
                #budgetenough = False
            except KeyError:
                # assume budget enough
                #budgetenough = True
                catbudget = -cat.metavalues["changebudget"].clean()
          
            if not cat.metaflags["business"]:
                itemtext.append("\n budget "+str(catbudget))

            try:
                catchange = -cat.metavalues["changeactual"]
            except KeyError:
                catchange = Dough(0)
           
            if catchange != 0:
                itemtext.append("\n  spent "+str(catchange))
            
            try:
                catbalance = cat.metavalues["endingbalance"]
            except KeyError:
                catbalance = Dough(0)
            
            if catbalance != Dough(0):
                itemtext.append("\n   left "+str(catbalance))

        self.ui.categoriesWidget.addItem("".join(itemtext))

    def showCategories(self):
        sortedcategories = (self.month.categories.keys())
        sortedcategories.sort()
        businesscats = []
        showbusiness = False
        for category in sortedcategories:
            cat = self.month.categories[category]
            # don't print accounts here, or business categories (yet)
            if not cat.metaflags["account"]: 
                if cat.metaflags["business"]:
                    businesscats.append(cat)
                else:
                    self.showCategory(cat)
        
        delta = (self.month.monthlyexpectedincome-self.month.monthlyexpectedoutpour)
        delta.clean()
        self.ui.totalsCategories.addItem(
            "Budgeted income - outpour:\n  %s"%delta
        )
        self.ui.totalsCategories.addItem(
            "Accumulated anti-savings:\n  %s"%self.month.accumulatedantisavings
        )

       
        if businesscats:
            self.ui.categoriesWidget.addItem("BUSINESS CATEGORIES")
            # now print business categories
            for cat in businesscats:
                self.showCategory(cat)
        else:
            self.ui.categoriesWidget.addItem("NO BUSINESS")

    def loadFile(self, filename):
        self.openfile = None
        print "Loading file", filename
        if " " not in filename:
            if filename == "scratch":
                self.openfile = os.path.join(self.rootdir, filename)
            else: 
                self.openfile = os.path.join(self.rootdir, self.YYYY, self.mm, filename)
            self.filename = filename
        else:
            filename = filename.split(" ")
            if len(filename) == 2 and filename[0] == "Business":
                self.filename = filename[1]
                self.openfile = os.path.join(self.rootdir, self.YYYY, self.mm, self.filename)

        lines = unicode("LOAD ERROR")
        if self.openfile:
            self.alert("Editing %s"%self.filename)
            self.ui.textEdit.setStatusTip("Editing %s"%self.filename)
            self.ui.textEdit.setFocus(QtCore.Qt.OtherFocusReason)
            with open(self.openfile, 'r') as f:
                lines = f.read()
        self.ui.textEdit.setText(lines)
   
    def saveOpenFile(self):
        if self.openfile:
            with open(self.openfile, 'w') as f:
                f.write(self.ui.textEdit.toPlainText())
            self.showAll()
            self.alert("%s saved!"%self.filename)
        else:
            self.alert("No file opened, cannot save")
        

if __name__ == '__main__':
    app = QApplication(sys.argv[0])
    main = MainWindow(sys.argv)
    main.show()
    sys.exit(app.exec_())
    
