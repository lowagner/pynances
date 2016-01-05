import curses
import curses.textpad
from mbf import *
# http://docs.python.org/2/library/curses.html   

class MainScreen:
    def __init__( self, screen, month ):
        self.filedir = ""
        self.whichwin = "cat"
        self.screen = screen
        self.month = month

        self.loadscreens()

    def loadscreens( self ):
        self.screen.erase()

        curses.mousemask(1)

        curses.start_color() 
        
        curses.noecho()

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE) 
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE) 
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_WHITE) 

        self.screen.bkgd(curses.color_pair(1)) 
        self.screen.box()
        screenheight, screenwidth =  self.screen.getmaxyx()
        screenheight -= 1
        self.cmdheight = screenheight - 1
        acctwinwidth = 42
        self.screen.addstr(1,acctwinwidth+2-len(self.month.name)/2, " "+self.month.name+" ", curses.A_REVERSE)
        self.screen.refresh() 

        self.winheight = screenheight-3
        self.acctwin = curses.newwin( self.winheight,
                                 acctwinwidth,
                                 2,
                                 2
                               )

        self.acctwinstartline = 2
        self.printtoacctwin()

        catwinx = 2 + acctwinwidth + 1
        catwinwidth = min(70, screenwidth - catwinx - 2)
        self.catwin = curses.newwin( self.winheight,
                                catwinwidth,
                                2,
                                catwinx
                               )
            
        self.catwinstartline = 2  #start at line 2 and go for it
        self.printtocatwin( ) 

        editx = catwinx + 1 + catwinwidth
        if editx > screenwidth - 30:
            self.editpad = False
        else:
            editwidth = screenwidth - editx - 2 
            self.editwin =  curses.newwin( self.winheight,
                                           editwidth,
                                           2,
                                           editx
                                         )
            self.editpad = curses.newwin( screenheight-9,
                                           editwidth-4,
                                           4,
                                           editx+2
                                         )

            self.editwin.clear()
            self.editwin.box()
            self.editwin.bkgd(curses.color_pair(3)) 
            self.editwin.addstr(0,2,"Edit")
            self.editwin.refresh()

            self.editpad.clear()
            self.editpad.bkgd(curses.color_pair(3)) 
            self.editpad.refresh()
            self.editor = curses.textpad.Textbox( self.editpad )
        

        self.resetblinker()

    def switchwhichwin( self , towin=0 ):
        if towin:
            if towin == "cat":
                if self.editpad:
                    if self.filedir == "":
                        self.editwin.addstr(0,2,"Edit")
                    else:
                        self.editwin.addstr(0,2,"Edit "+self.filedir )
                self.acctwin.addstr(0,2,"Accounts" )
                self.catwin.addstr(0,2,"Categories", curses.A_UNDERLINE)
                self.whichwin = "cat"
            elif towin == "acct":
                if self.editpad:
                    if self.filedir == "":
                        self.editwin.addstr(0,2,"Edit")
                    else:
                        self.editwin.addstr(0,2,"Edit "+self.filedir )
                self.catwin.addstr(0,2,"Categories") # erase special text effect on Categories
                self.acctwin.addstr(0,2,"Accounts", curses.A_UNDERLINE)
                self.whichwin = "acct"
            elif self.editpad: # towin == "edit"
                if self.filedir == "":
                    self.editwin.addstr(0,2,"Edit", curses.A_UNDERLINE )
                else:
                    self.editwin.addstr(0,2,"Edit "+self.filedir, curses.A_UNDERLINE )
                self.catwin.addstr(0,2,"Categories") # erase special text effect on Categories
                self.acctwin.addstr(0,2,"Accounts")
                self.editwin.addstr(self.winheight-3,2,"C-g", curses.A_BOLD)
                self.editwin.addstr(self.winheight-3,5,": get out") 
                self.editwin.addstr(self.winheight-3,18,"C-o / C-k", curses.A_BOLD)
                self.editwin.addstr(self.winheight-3,27,": insert/kill line")
                self.editwin.addstr(self.winheight-2,2,"C-a", curses.A_BOLD)
                self.editwin.addstr(self.winheight-2,5,": start left")
                self.editwin.addstr(self.winheight-2,19,"C-n / C-p", curses.A_BOLD)
                self.editwin.addstr(self.winheight-2,28,": next/prev line")
                self.whichwin = "edit"

            self.acctwin.refresh()
            self.catwin.refresh()
            if self.editpad:
                self.editwin.refresh()
        else:
            # if no window was given, then switch between categories and accounts
            if self.whichwin == "cat":
                self.switchwhichwin("acct")
            elif self.whichwin == "acct":
                self.switchwhichwin("cat")
        
    def printtoacctwin( self ):
        line = self.acctwinstartline
        acctwinheight, acctwinwidth =  self.acctwin.getmaxyx()
        self.acctwin.clear()
        self.acctwin.bkgd(curses.color_pair(3)) 
        self.acctwin.box()

        if self.whichwin == "acct":
            self.acctwin.addstr(0,2,"Accounts", curses.A_UNDERLINE)
        else:
            self.acctwin.addstr(0,2,"Accounts")

        starttotaldough = Dough(0)
        endtotaldough = Dough(0)
        accounts = self.month.accountlist.keys()
        accounts.sort()
        for account in accounts:
            accountname = self.month.accountlist[account]
            if line > 0 and line < acctwinheight - 1:
                self.acctwin.addstr(line,2,accountname+" ("+account+")", curses.A_BOLD)
            line += 1
            try:
                sbalance = self.month.categories[account.upper()].metavalues["startingbalance"]
            except KeyError:
                sbalance = Dough(0)
            starttotaldough += sbalance
            if line > 0 and line < acctwinheight - 1:
                self.acctwin.addstr(line,3,"start "+str(sbalance))
            line += 1

            ebalance = self.month.categories[account.upper()].metavalues["endingbalance"]
            if line > 0 and line < acctwinheight - 1:
                self.acctwin.addstr(line,5,"end "+str(ebalance))
            line += 1

            endtotaldough += ebalance
        
        line += 1
        if line > 0 and line < acctwinheight - 1:
            self.acctwin.addstr(line,2,"Totals", curses.A_BOLD)
        line += 1
        if line > 0 and line < acctwinheight - 1:
            self.acctwin.addstr(line,3,"start "+str(starttotaldough.clean()))
        line += 1
        if line > 0 and line < acctwinheight - 1:
            self.acctwin.addstr(line,5,"end "+str(endtotaldough.clean()))
        line += 1
        if line > 0 and line < acctwinheight - 1:
            self.acctwin.addstr(line,3,"delta "+str(endtotaldough-starttotaldough))
        line += 1

        self.acctwin.refresh()

    def printcat( self, cat, line ):
        catwinheight, catwinwidth =  self.catwin.getmaxyx()
        # if not an account, it's a category we can analyze more
        if cat.metaflags["business"]:
            if line > 0 and line < catwinheight - 1:
                self.catwin.addstr(line,2,"Business "+str(cat.name), curses.A_BOLD)
        else:
            if line > 0 and line < catwinheight - 1:
                self.catwin.addstr(line,2,str(cat.name), curses.A_BOLD)

        if cat.metaflags["income"]:
            catincome = cat.metavalues["changebudget"]
            line += 1
            if line > 0 and line < catwinheight - 1:
                self.catwin.addstr(line,5,"got "+str(catincome)) 
        else:
            try:
                catbudget = cat.metavalues["budget"].clean()
                budgetenough = False
            except KeyError:
                # assume budget enough
                budgetenough = True
                catbudget = -cat.metavalues["changebudget"].clean()
          
            rightadjustx = 32
            if not cat.metaflags["business"]:
                if line > 0 and line < catwinheight - 1:
                    self.catwin.addstr(line,rightadjustx,("budget "+str(catbudget)).rjust(catwinwidth-rightadjustx-2))
            line += 1

            try:
                catchange = -cat.metavalues["changeactual"]
            except KeyError:
                catchange = Dough(0)
            
            if line > 0 and line < catwinheight - 1:
                self.catwin.addstr(line,5,"spent "+str(catchange))
            
            if budgetenough:
                catbalance = Dough(0)
            else:
                try:
                    catbalance = cat.metavalues["endingbalance"]
                except KeyError:
                    catbalance = Dough(0)
            
            if catbalance != Dough(0):
                if line > 0 and line < catwinheight - 1:
                    self.catwin.addstr(line,rightadjustx,("left "+str(catbalance)).rjust(catwinwidth-rightadjustx-2))

        line += 1
        return line

    def printtocatwin( self ):
        catwinheight, catwinwidth =  self.catwin.getmaxyx()
        line = self.catwinstartline
        self.catwin.clear()
        self.catwin.bkgd(curses.color_pair(3)) 
        self.catwin.box()
        self.catwin.addstr(0,2,"Categories")

        if self.whichwin == "cat":
            self.catwin.addstr(0,2,"Categories", curses.A_UNDERLINE)
        else:
            self.catwin.addstr(0,2,"Categories")
        
        sortedcategories = (self.month.categories.keys())
        sortedcategories.sort()
        for category in sortedcategories:
            cat = self.month.categories[category]
            if not ( cat.metaflags["account"] or cat.metaflags["business"]):
                line = self.printcat( cat, line )

        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,2, "Monthly expected income", curses.A_BOLD)
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,5, str(self.month.monthlyexpectedincome))
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,2, "Monthly expected outpour", curses.A_BOLD)
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,5, str(self.month.monthlyexpectedoutpour))
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,2, "Accumulated anti-savings", curses.A_BOLD)
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,5, str(self.month.accumulatedantisavings))

        line+= 2
        for category in sortedcategories:
            if category in self.month.categories:
                cat = self.month.categories[category]
                if cat.metaflags["business"] and not cat.metaflags["account"]:
                    line = self.printcat( cat, line )
        line += 1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,2, "Total actual income", curses.A_BOLD)
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,5, str(self.month.totalactualincome))
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,2, "Total actual spendings", curses.A_BOLD)
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,5, str(self.month.totalactualspendings))
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,2, "Delta", curses.A_BOLD)
        line+=1
        if line > 0 and line < catwinheight - 1:
            self.catwin.addstr(line,5, str(self.month.totalactualincome-self.month.totalactualspendings))
        line+=1

        self.catwin.refresh()


    def modifystartline( self, deltaline ):
        if self.whichwin == "acct":
            self.acctwinstartline += deltaline
            self.printtoacctwin()  
        elif self.whichwin == "cat":
            self.catwinstartline += deltaline
            self.printtocatwin() 
        
    def resetblinker( self ):
        self.screen.addstr(self.cmdheight, 1, "")

    def getcmd( self, cmdstring = "cmd:"):
        self.screen.addstr(self.cmdheight, 1, "                                           ")
        self.screen.addstr(self.cmdheight, 1, cmdstring, curses.A_REVERSE)
        self.screen.refresh()
        curses.echo()
        s = self.screen.getstr( self.cmdheight, len(cmdstring)+2, 20 )
        # set back to no echo
        curses.noecho()
        self.screen.addstr(self.cmdheight, 1, "                               ")
        self.resetblinker() 
        self.screen.refresh()
        return s

    def show( self, something ):
        self.screen.addstr(self.cmdheight, 2, str(something) )

    def edit( self, filename="" ):
        if self.editpad:        
            # erase the old edit window
            self.editwin.erase()
            self.editwin.box()
            # get ready the name to put on the top of the edit window 
            if filename != "":
                self.filedir = os.path.join(self.month.rootdir, filename) 
            elif self.filedir == "":
                self.filedir = "scratch"
            # then officially switch
            self.switchwhichwin("edit")
           
            # grab data from the file
            try:
                with open(self.filedir) as f:
                    data = f.readlines()
            except:
                data = [ "" ]

            
            #self.editwin.addstr(0,2,"Edit "+self.filedir, curses.A_UNDERLINE)
            #self.editwin.refresh()
            
            # get the editting pad ready
            self.editpad.erase()
            # add in the data
            i = 0
            while i < len(data):
                self.editpad.addstr(i,0, data[i])
                i += 1    
            # then refresh it
            self.editpad.refresh()
            # make it so the editor doesn't strip newlines... we'll take care of it later
            self.editor.stripspaces = False
            # the unintended side effect is that it puts lots of white space at the end
            # of lines.

            data = self.editor.edit()
            s = "notavalue"
            while not (s[0] == "Y" or s[0] == "N"):
                s = self.getcmd("save file? (y/n):")
                s = s.upper()
            if s[0] == "Y":
                # save data to filedir.  

                # but first we clean it up a bit
                data = data.split('\n')

                # first clear out right spaces
                i = 0
                while i < len(data):
                    data[i] = data[i].rstrip()
                    i += 1
    
                # then clear out all empty lines at the end
                i = len(data) - 1
                while i >= 0:
                    if data[i] == "":
                        del data[i]
                        i -= 1
                    else:
                        break
                
                # then save
                with open(self.filedir, 'w') as f:
                    for line in data:
                        f.write(line+"\n")

                # reset everything
                self.month.reset()
                self.month.grandtotal()
                self.printtoacctwin( ) 
                self.printtocatwin( ) 

                self.show( "file "+self.filedir+" written." )
            else:
                self.show( "not saving." )
            # erase the last lines of the edit window 
            self.editwin.addstr(self.winheight-3,2,"                                           ")
            self.editwin.addstr(self.winheight-2,2,"                                          ")
            # after done editing, switch to category moving
            self.switchwhichwin( "cat" )
            
        else:
            self.show( "widen screen" )


# define a main function
def main( screen, month ): 
    mainscreen = MainScreen( screen, month )
    c = 0
    while c != 27:
        mainscreen.resetblinker()
        c = screen.getch() 
        if c == ord('/') or c == ord(':') or c == ord(';'):
            # for input, use echo (so user can see what is going on )
            s = mainscreen.getcmd()
            if len(s) > 0:
                split = s.split()
                if split[0][0].lower() == "q":
                    c = 27
                elif split[0][0].lower() == "e":
                    if len(split) > 1:
                        mainscreen.edit(split[1])
                    else:
                        mainscreen.edit()
                elif s == "reload":
                    month.reset()
                    month.grandtotal()
                    mainscreen = MainScreen( screen, month )
                elif split[0] == "load":
                    args = split[1].split( os.sep )
                    if len(args) == 1:
                        YYYY = str(month.year)
                        mm = args[0]
                    else:
                        YYYY, mm = args[0], args[1]

                    path = os.path.join( YYYY, mm )
                    if os.path.exists( path ):
                        month = Month( YYYY, mm )
                        month.grandtotal()
                        mainscreen = MainScreen( screen, month )
                    else:
                        mainscreen.show(split[1]+" is unavailable." )
                    
                elif s == "generate":
                    if month.generatenextmonth():
                        while not ( s[0] == "Y" or s[0].lower() == "n" ):
                            s = mainscreen.getcmd("destroy existing "+month.nextyearmonth+"? Y/n")
                        if s[0] == "Y":
                            month.generatenextmonth( True )
                            mainscreen.show(month.nextyearmonth+" generated!")
                    else:
                        mainscreen.show(month.nextyearmonth+" generated!")
                else:
                    mainscreen.show("unknown command: "+s)
        elif c == ord('h') or c == curses.KEY_LEFT:
            pass
        elif c == ord('j') or c == curses.KEY_DOWN:
            mainscreen.modifystartline( -1 )
        elif c == ord('J') or c == 336:
            mainscreen.modifystartline( -5 )
        elif c == ord('k') or c == curses.KEY_UP:
            mainscreen.modifystartline( 1 )
        elif c == ord('K') or c == 337:
            mainscreen.modifystartline( 5 )
        elif c == ord('l') or c == curses.KEY_RIGHT:
            pass
        elif c == ord('\r') or c == ord('\n'): # enter
            pass
        elif c == 9:
            # tab
            mainscreen.switchwhichwin()
        elif c == curses.KEY_MOUSE:
            m = curses.getmouse()
            mainscreen.show( "mouse" )
        elif c == curses.KEY_RESIZE:
            ok = True
            if mainscreen.whichwin == "edit":
                mainscreen.switchwhichwin( "cat" )
                ok = False 
            mainscreen.loadscreens()
            if not ok:
                mainscreen.show("Don't resize when editting.  Changes are lost.")
        else:
            mainscreen.show( c )
            curses.flash() 
            curses.beep() #
    
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    if len(sys.argv) == 1:
        # only one argument supplied to sys, i.e. this program
        currentyear = time.strftime("%Y")   # 2014, etc.
        currentmonth = time.strftime("%m")  # 01 = jan, ..., 12 = dec
        if os.path.exists( os.path.join( currentyear, currentmonth ) ):
            month = Month( currentyear, currentmonth )
        else:
            sys.exit(" Current month is unavailable in pynances.  Try YYYY"+os.sep+"mm" )
    else:
        if os.path.exists( sys.argv[1] ):
            args = sys.argv[1].split( os.sep )
            YYYY, mm = args[0], args[1]
            month = Month( YYYY, mm )
        else:
            sys.exit(" Month "+sys.argv[1]+" is unavailable in pynances.  Try YYYY"+os.sep+"mm" )

    month.grandtotal()

    # call the main function, but wrap it so that the terminal will be ok
    # if the program screws up.
    try: 
        curses.wrapper( main, month ) 
    except KeyboardInterrupt: 
        print "Got KeyboardInterrupt exception. Exiting..." 
        exit() 
