#!/usr/bin/env python
__version__ = "0.1a"

from mbf import *

import sys
import platform
 
import PySide
from PySide.QtGui import (QApplication, QMainWindow, QMessageBox, QIcon, QFileDialog, QStatusBar, QResizeEvent, QPalette)
from PySide import QtCore

from mainwindow import Ui_MainWindow as Ui

class History(object):
    def __init__(self):
        self.commands = []
        self.commandpos = 0
    def appendCommand(self, currentcmd):
        if currentcmd:
            if len(self.commands) == 0:
                self.commands.append(currentcmd)
            else:
                if currentcmd != self.commands[-1]:
                    self.commands.append(currentcmd)
    def clearCommand(self, currentcmd):
        if currentcmd:
            if len(self.commands) == 0:
                self.commands.append(currentcmd)
            elif len(self.commands) == 1:
                if currentcmd != self.commands[0]:
                    if self.commandpos > 0:
                        self.commands.append(currentcmd)
                    else:
                        self.commands.insert(0, currentcmd)
            else:
                if self.commandpos >= len(self.commands)-1:
                    if (currentcmd != self.commands[-1] and
                        currentcmd != self.commands[-2]):
                        self.commands.append(currentcmd)
                elif self.commandpos <= 0:
                    self.commandpos = 0
                    if currentcmd != self.commands[0]:
                        self.commands.insert(0, currentcmd)
                else:
                    if (currentcmd != self.commands[self.commandpos] and
                        currentcmd != self.commands[self.commandpos-1] and
                        currentcmd != self.commands[self.commandpos+1]):
                        self.commands.insert(self.commandpos, currentcmd)

        self.commandpos = len(self.commands)
    def previousCommand(self, currentcmd):
        if currentcmd:
            if len(self.commands) == 0:
                self.commands.append(currentcmd)
                self.commandpos = 0
                return currentcmd
            else:   # there are some commands in there
                if self.commandpos >= len(self.commands):
                    self.commandpos = len(self.commands)
                    if currentcmd != self.commands[-1]:
                        self.commands.append(currentcmd)
                elif self.commandpos <= 0:
                    self.commandpos = 0
                    if currentcmd != self.commands[0]:
                        self.commands.insert(0, currentcmd)
                    return currentcmd
                else:
                    if (currentcmd != self.commands[self.commandpos] and
                        currentcmd != self.commands[self.commandpos-1]):
                        self.commands.insert(self.commandpos, currentcmd)
        self.commandpos -= 1
        return self.commands[self.commandpos]
    def nextCommand(self, currentcmd):
        if currentcmd:
            if len(self.commands) == 0:
                self.commands.append(currentcmd)
                self.commandpos = 0
            else:   # there are some commands in there
                if self.commandpos >= len(self.commands)-1:
                    if currentcmd != self.commands[-1]:
                        self.commands.append(currentcmd)
                        self.commandpos += 1
                elif self.commandpos <= 0:
                    self.commandpos = 0
                    if (currentcmd != self.commands[0] and
                        currentcmd != self.commands[1]):
                        self.commands.insert(1, currentcmd)
                        self.commandpos += 1
                else:
                    if (currentcmd != self.commands[self.commandpos] and
                        currentcmd != self.commands[self.commandpos+1]):
                        self.commands.insert(self.commandpos+1, currentcmd)
                        self.commandpos += 1

        self.commandpos += 1
        if self.commandpos >= len(self.commands):
            self.commandpos = len(self.commands)
            return unicode("")
        return self.commands[self.commandpos]

class MainWindow(QMainWindow):
    def __init__(self, args, parent=None):
        super(MainWindow, self).__init__(parent)
       
        self.YYYY = None
        self.mm = None
        if len(args) == 1:
            # only one argument supplied to sys, i.e. this program
            self.YYYY = time.strftime("%Y")   # 2014, etc.
            self.mm = time.strftime("%m")  # 01 = jan, ..., 12 = dec
            if os.path.exists(os.path.join(self.YYYY, self.mm)):
                self.rootdir = "."
        else:
            split = args[1].split(os.sep)
            if len(split) == 1:
                self.YYYY = time.strftime("%Y")   # 2014, etc.
                if os.path.exists(os.path.join(self.YYYY, split[0])):
                    self.rootdir = "."
                    self.mm = split[0]
            elif os.path.exists(args[1]):
                if len(split) == 2:
                    self.rootdir = "."
                    self.YYYY, self.mm = split[0], split[1]
                else:
                    self.rootdir = os.sep.join(split[:-2])
                    self.YYYY, self.mm = split[-2], split[-1]

        if self.YYYY is None or self.mm is None:
            self.YYYY = None
            self.mm = None
            self.rootdir = None

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
        
        wincol = self.palette().color(QPalette.Window); 
        self.ui.lineEdit.setStyleSheet("background-color: %s;"%wincol.name())
        self.ui.lineEdit.setStatusTip("Command Line")
        self.ui.lineEdit.installEventFilter(self)

        self.ui.centralWidget.installEventFilter(self)

        self.history = History()
        
        # read in settings to determine whether we should use single click or not.
        #self.ui.actionSingleClickToOpen.setChecked(True)

        # read in settings to determine if there's a working directory:
        # self.rootdir = ...
       
        self.showAll()
        self.ui.accountsWidget.setTabOrder(self.ui.accountsWidget, self.ui.categoriesWidget)
        self.ui.accountsWidget.setTabOrder(self.ui.categoriesWidget, self.ui.textEdit)

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
#            if key == QtCore.Qt.Key_Tab:
#                if widget == self.ui.accountsWidget:
#                    self.ui.categoriesWidget.setFocus(QtCore.Qt.TabReason)
#                    
#                print "tab"
#                return True
            if widget == self.ui.lineEdit: # command line
                if key == QtCore.Qt.Key_Escape:
                    self.history.clearCommand(self.ui.lineEdit.text())
                    self.ui.lineEdit.setText("")
                    return True
                elif key == QtCore.Qt.Key_Return:
                    thetext = self.ui.lineEdit.text()
                    self.execute(thetext)
                    self.history.appendCommand(thetext)
                    self.ui.lineEdit.setText("")
                    self.ui.centralWidget.setFocus(QtCore.Qt.OtherFocusReason)
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
                    self.ui.lineEdit.setFocus(QtCore.Qt.OtherFocusReason)
                    return True
                elif widget != self.ui.textEdit:
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
                    elif (key == QtCore.Qt.Key_Slash or 
                        key == QtCore.Qt.Key_Question or 
                        key == QtCore.Qt.Key_Colon or
                        key == QtCore.Qt.Key_Semicolon):
                        self.ui.lineEdit.setFocus(QtCore.Qt.OtherFocusReason)
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

    def execute(self, command):
        self.ui.statusBar.showMessage("executing %s"%command)
        print "executing", command

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
   
    def showAll(self):
        self.ui.accountsWidget.clear()
        self.ui.totalsAccounts.clear()
        self.ui.categoriesWidget.clear()
        self.ui.totalsCategories.clear()

        if self.rootdir:
            self.month = Month(self.YYYY, self.mm)
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
            itemtext.append("\n  end ")
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
                    if (cat.metavalues["startingbalance"] != 0 or cat.metavalues["endingbalance"] != 0):
                        businesscats.append(cat)
                else:
                    self.showCategory(cat)
        
        delta = (self.month.monthlyexpectedincome-self.month.monthlyexpectedoutpour)
        delta.clean()
        self.ui.totalsCategories.addItem(
            "Expected income - expected outpour:\n  %s"%delta
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
        if " " in filename:
            lines = unicode("LOAD ERROR")
        else: 
            thefile = os.path.join(self.rootdir, self.YYYY, self.mm, filename)
            lines = unicode("LOAD ERROR")
            with open(thefile, 'r') as f:
                lines = f.read()
        self.ui.textEdit.setText(lines)
        self.ui.textEdit.setStatusTip("Editing %s"%filename)
        self.ui.statusBar.showMessage("Editing %s"%filename)
        
        

if __name__ == '__main__':
    app = QApplication(sys.argv[0])
    main = MainWindow(sys.argv)
    main.show()
    sys.exit(app.exec_())
    
