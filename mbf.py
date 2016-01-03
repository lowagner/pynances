# money money money, Must Be Funny, in a rich man's world....
import time, os, sys
import config

class Dough:
    ''' some amount of money, with units. '''
    def __init__( self, amount, units=config.DEFAULTcurrency ):
        self.dough = {} # a dictionary with money amounts.  key = units, value = amount
        checkunits = units.upper()
        if checkunits == "EUROS":
            checkunits = "EURO"
        self.dough[checkunits] = amount

    def copy( self ): 
        ''' make a deep copy of oneself '''
        newself = Dough(0)
        # in case the default currency is not in "self" which we want to copy...
        if config.DEFAULTcurrency not in self.dough.keys():
            # remove the default currency
            del newself.dough[config.DEFAULTcurrency]
       
        # then add in all the other currencies in self
        for currency in self.dough.keys():
            newself.dough[currency] = self.dough[currency]

        return newself 
    
    def clean( self, units=config.DEFAULTcurrency ):
        ''' cut out any entries that are zero, unless they all are; then keep 0 in the units currency. '''
        currencies = self.dough.keys()
        for currency in currencies:
            if abs(int(self.dough[currency])-self.dough[currency]) < 1E-3:
                # if the dough is an integer, get rid of the floatness
                self.dough[currency] = int(self.dough[currency])
            else:
                # general getting rid of extra decimal points
                self.dough[currency] = float( format("%.2f")%(self.dough[currency]) ) 
                #int(100 * self.dough[currency]) *1.0/ 100 
        if len(currencies) > 1:
            for currency in currencies:
                if abs(self.dough[currency]) < 2E-3:
                    del self.dough[currency]
            
            if len( self.dough ) == 0:
                checkunits = units.upper()
                if checkunits == "EUROS":
                    checkunits = "EURO"
                self.dough[checkunits] = 0

        return self.copy()
    
    def __eq__( self, other ): # ==
        ''' check if doughs are equal '''
        if isinstance( other, Dough ):
            other.clean()
        elif other == 0:
            other = Dough(0)
        else:
            raise Exception("Comparing dough to non-dough")
        self.clean()

        equal = True

        if len(other.dough) != len(self.dough):
            # nonequal lengths, obviously not equal
            equal = False
        else:
            # equal lengths
            if set(self.dough.keys()) != set(other.dough.keys()):
                # not equal sets of keys (currencies), they are probably not equal
                if len(self.dough) == 1:
                    # if they have equal lengths, but not equal keys, they could
                    # both be equal to zero.  but if they aren't equal to zero,...
                    if ( abs( self.dough[ self.dough.keys()[0] ]) > 1E-3 
                        or
                         abs( other.dough[ other.dough.keys()[0] ]) > 1E-3):
                         # they aren't both zero, so they are not equal!
                         equal = False
                else:
                    equal = False
            else:
                # both sets of keys (currencies) are equal
                for key in self.dough.keys():
                    if abs( self.dough[key] - other.dough[key] ) > 1E-3:
                        equal = False
                        break
                    
        return equal
    
    def __ne__( self, other ): # !=
        return not ( self == other )

    def __imul__( self, other ): # +=
        ''' *= a dough by a scalar '''
        for currency, amount in self.dough.iteritems():
            self.dough[currency] *= other 
        return self 

    def __mul__( self, other ):
        ''' multiply self by other '''
        # first we make a copy of the self into "theresult"
        theresult = self.copy()
        # then we add the other dough
        theresult *= other
        return theresult 
    
    def __neg__( self ):
        ''' negate a copy of one's self '''
        theresult = self.copy()
        for currency in self.dough:
            theresult.dough[currency] = -self.dough[currency]
        return theresult

    def __iadd__( self, other ): # +=
        ''' += a dough '''
        try:
            for currency, amount in other.dough.iteritems():
                if currency in self.dough:
                    self.dough[currency] += amount
                elif abs(other.dough[currency]) > 1E-3:
                    self.dough[currency] = amount
        except AttributeError:
            raise Exception("Attempting to add non-dough to a dough class")
        return self 

    def __add__( self, other ):
        ''' add two doughs '''
        # first we make a copy of the self into "thesum"
        thesum = self.copy()
        # then we add the other dough
        thesum += other
        return thesum
    
    def __isub__( self, other ): # +=
        ''' -= a dough '''
        try:
            for currency, amount in other.dough.iteritems():
                if currency in self.dough:
                    self.dough[currency] -= amount
                else:
                    self.dough[currency] = -amount
        except AttributeError:
            raise Exception("Attempting to add non-dough to a dough class")
        return self 

    def __sub__( self, other ):
        ''' add two doughs '''
        # first we make a copy of the self into "thedifference"
        thedifference = self.copy()
        # then we add the other dough
        thedifference -= other
        return thedifference

    def __str__( self ):
        ''' print function '''
        string = "" 
        numcurrenciesleft = len(self.dough)
        for currency, amount in self.dough.iteritems():
            numcurrenciesleft -= 1
            if isinstance(amount, int):
                string += str(amount) + " " + currency
            else:
                string += format("%.2f")%(amount) + " " + currency
            if numcurrenciesleft:
                string += " + "
            
        return string 


class DoughFromString( Dough ):
    ''' another way to get to the dough class, different initialization '''
    def __init__( self, doughstring ):
        doughsplit = doughstring.split()
        self.dough = {}
        if len(doughsplit) == 1:
            self.dough[config.DEFAULTcurrency] = float( doughsplit[0] )
            if abs(self.dough[config.DEFAULTcurrency] - int(self.dough[config.DEFAULTcurrency]) ) < 1E-3:
                self.dough[config.DEFAULTcurrency] = int(self.dough[config.DEFAULTcurrency])
        else:
            i = 0
            while i < len(doughsplit):
                try:
                    checkunits = doughsplit[i+1].upper()
                    if checkunits == "EUROS":
                        checkunits = "EURO"
                except IndexError:
                    checkunits = config.DEFAULTcurrency
                self.dough[checkunits] = float( doughsplit[i] )
                if abs(self.dough[checkunits] - int(self.dough[checkunits]) ) < 1E-3:
                    self.dough[checkunits] = int(self.dough[checkunits])
                i += 3 # skip the + sign

class Entry:
    def __init__( self, info ):
        self.name = ""
        namemode = True
        self.averaged = False
        i = 0
        while i < len(info):
            if info[i].upper() == "PAID" or info[i].upper() == "FROM":
                self.account = info[i+1].upper() # capitalize the account
                i += 2 
                namemode = False
            elif info[i].upper() == "AVERAGE":
                self.averaged = True
                self.outmonths = info[i+1]
                self.account = info[i+2].upper()
                i += 3 
                namemode = False
            elif info[i].upper() == "WEEK":
                self.week = info[i+1]
                i += 2 
                namemode = False
            else:
                if namemode:
                    self.name += info[i] + " "
                    i += 1
                else:
                    self.dough = DoughFromString( " ".join( info[i:] ) )
                    self.dough.clean()
                    break
        if len(self.name) > 1: 
            self.name = self.name[:-1]
        else:
            self.name = "unknown"

    def budget( self ):
        return self.dough.copy()
        
    def actual( self, month ):
        if self.averaged:
            if config.MONTHS[int(month)-1] in self.outmonths:
                return (self.dough.copy() * (12.0 / len(self.outmonths)))
            else:
                return Dough(0) 
        else:
            return self.budget()

class Category:
    def __init__( self, rootdir, name ):
        self.name = name
        self.filename = os.path.join( rootdir, name )
        self.allowedmetaflags = [ "account", # true or false flags
                                  "income",
                                  "budgetenough",
                                  "nocarryover" ]
        self.allowedmetavalues = [ "startingbalance", # meta-information with a value
                                   "budget",
                                   "endingbalance" ]

        self.metavalues = {} # is a dictionary
        self.metaflags = {}
        self.accounts = {}
        for key in self.allowedmetaflags:
            self.metaflags[key] = False # set them all false
        self.parse()

#### CATEGORY CLASS
    def parse( self ):
        print " Parsing ", self.filename
        try:
            with open(self.filename) as f:
                content = f.readlines()
        except:
            raise Exception("Error parsing file " + self.filename)
        
        self.entries = []

        for line in content:
            split = line.split() # strip leading/trailing white space and split
            if len(split) == 0:
                pass
            elif split[0][0] == "#":
                ## commented line begins with a #
                pass
            elif split[0] in self.allowedmetaflags:
                # if the file is a metaflag
                self.metaflags[ split[0] ] = True
            elif split[0] in self.allowedmetavalues:
                # then split[0] is a metavalue, and the rest is the value in EUROS
                datastring = " ".join( split[1:] )
                self.metavalues[split[0]] = DoughFromString( datastring )
                self.metavalues[split[0]].clean()
            else:
                self.entries.append( Entry(split) ) 

        if self.metaflags["income"] and self.metaflags["budgetenough"]:
            print "WARNING:  should not include \"income\" and \"budgetenough\" in file " +self.filename
#        if self.metaflags["budgetenough"] and "startingbalance" in self.metavalues:
#            print "WARNING:  should not specify \"startingbalance\" and \"budgetenough\" in file "+self.filename
            
#### CATEGORY CLASS
    def total( self, accounts, month ):
        if self.metaflags["income"]:
            # we will parse an income file 
            totalinbudget = Dough(0)
            totalinactual = Dough(0)

            for e in self.entries:
                # if the income is averaged over many months...
                actuale = e.actual( month )
                totalinactual += actuale
                totalinbudget += e.budget()

                if e.account in accounts:
                    accounts[e.account] += actuale
                else:
                    accounts[e.account] = actuale

            self.metavalues["changeactual"] = totalinactual.clean()
            self.metavalues["changebudget"] = totalinbudget.clean()
            # experimental
            self.metavalues["endingbalance"] = (totalinactual-totalinbudget).clean()

            return [ totalinactual, totalinbudget  ]

#### CATEGORY CLASS, TOTAL METHOD
        elif self.metaflags["account"]:
            # an account, like a credit card
            balance = Dough(0)
    
            if "startingbalance" in self.metavalues:
                balance = self.metavalues["startingbalance"].copy()

            for e in self.entries:
                actuale = e.actual( month )
                balance += actuale
         
                # even though this account is getting money in,
                # the account which we used to get the money in must be debited!
                if e.account in accounts:
                    accounts[e.account] -= actuale
                else:
                    accounts[e.account] = -actuale
            
            self.metavalues["endingbalance"] = balance.clean()
           
            # accounts are zero-sum games.
            return [ Dough(0), Dough(0) ]

#### CATEGORY CLASS, TOTAL METHOD
        else:
            # regular file of things to buy in a certain category
            balance = Dough(0)
            totaloutbudget = Dough(0)
            totaloutactual = Dough(0)

            if "startingbalance" in self.metavalues:
                balance = self.metavalues["startingbalance"].copy()

            if "budget" in self.metavalues:
                balance += self.metavalues["budget"]

            for e in self.entries:
                actuale = e.actual( month )
                totaloutactual += actuale
                totaloutbudget += e.budget()
                balance -= actuale
                if e.account in accounts:
                    accounts[e.account] -= actuale
                else:
                    accounts[e.account] = -actuale
           
            if self.metaflags["budgetenough"]:
                balance += totaloutbudget

            self.metavalues["endingbalance"] = balance.clean()
            self.metavalues["changeactual"] = -totaloutactual.clean()
            self.metavalues["changebudget"] = -totaloutbudget.clean()
            
            return [ -totaloutactual, -totaloutbudget ]

#### CATEGORY CLASS
    def write( self ): 
        pass
        
#### END CATEGORY CLASS

class Month:
    def __init__( self, YYYY, mm ):
        self.rootdir = os.path.join( YYYY, mm )
        self.year = int(YYYY)
        self.month = int(mm)
        self.names = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December" ]
        self.name = self.names[self.month-1] + " " + str(YYYY)

        self.reset()

    def reset( self ):
        self.categorynames = [ ]
        for f in os.listdir( self.rootdir ):
            if not f.startswith('.'):
                self.categorynames.append(f)
#        self.incomefiles = [ "income", "reimburse" ]
#        for income in self.incomefiles:
#            if income in self.categorynames:
#                self.categorynames.remove(income)
        if "totals" in self.categorynames:
            self.categorynames.remove("totals")

        self.categories = {}
        for catname in self.categorynames:
            self.categories[catname] = Category( self.rootdir, catname )
        

    def grandtotal( self, printme=False ): 
        # the following dictionary will hold all the information about how the account
        # balances will change from this month to the next
        self.accounts = {}
        for account in config.ACCOUNTS:
            self.accounts[account] = Dough(0)

        self.totaldeltabudget = Dough(0)
        self.totaldeltaactual = Dough(0)
        # first go through everything and get all accounts up to date
        for catname in self.categories:
            cat = self.categories[catname]
            actual, budget = cat.total( self.accounts, #adds entries to the accounts
                                        self.month ) # for the given month...
            self.totaldeltabudget += budget
            self.totaldeltaactual += actual
        
        # need to repeat the process, everything global should be ok
        self.monthlyexpectedincome = Dough(0)
        self.monthlyexpectedoutpour = Dough(0)
        self.accumulatedantisavings = Dough(0)

        self.totalactualincome = Dough(0)
        self.totalactualspendings = Dough(0)
        for catname in self.categories:
            cat = self.categories[catname]
            if cat.metaflags["income"]:
                # income category
                if catname not in config.BUSINESScategories:
                    # don't put business stuff in expected income
                    self.monthlyexpectedincome += cat.metavalues["changebudget"]
                # but do put everything in actual income
                self.totalactualincome += cat.metavalues["changeactual"]

            elif not cat.metaflags["account"]:
                # not an account, some other category
                
                # first see what we're budgeting in each category
                if catname not in config.BUSINESScategories:
                    # if it's not business related, we can budget for it
                    try:
                        catbudget = cat.metavalues["budget"]
                        #budgetenough = False
                    except KeyError:
                        # assume budget enough
                        #budgetenough = True
                        catbudget = -cat.metavalues["changebudget"]
                    
                    self.monthlyexpectedoutpour += catbudget

                # see what the actual changes are in each category
                try:
                    catchange = -cat.metavalues["changeactual"]
                except KeyError:
                    catchange = Dough(0)
                
                self.totalactualspendings += catchange

                # now see if there's anything hidden that we can spend this month
#                if budgetenough:
#                    catbalance = Dough(0)
#                else:
                try:
                    catbalance = cat.metavalues["endingbalance"]
                except KeyError:
                    catbalance = Dough(0)
                
                self.accumulatedantisavings += catbalance



        if printme:
            print "TOTALS"
            print "grand total actual change = ", self.totaldeltaactual
            print "grand total averaged/budgeted change = ", self.totaldeltabudget 
            print
            print " monthly expected income = ", self.monthlyexpectedincome
            print " monthly expected outpour = ", self.monthlyexpectedoutpour
            print " accumulated anti savings = ", self.accumulatedantisavings
            print 
            print " total actual income = ", self.totalactualincome 
            print " total actual spending = ", self.totalactualspendings
            print " Delta = ", (self.totalactualincome - self.totalactualspendings)
            print 
            print "ACCOUNTS"


        for account in config.ACCOUNTS:
            # use the config to put it in a certain order
            self.categories[account].metavalues["endingbalance"] += self.accounts[account]
            endmonth =  self.categories[account].metavalues["endingbalance"].clean()

            if printme:
                print "money change in ", account, ": ", self.accounts[account].clean()
                print "   end of month account balance: ", endmonth


    def generatenextmonth( self, deletedir=False ):
        nextmonth = self.month + 1
        nextyear = self.year
        if nextmonth > 12:
            nextmonth = 1
            nextyear += 1

        self.nextyear = str(nextyear)
        self.nextmonth = format("%02d")%(nextmonth)
        self.nextyearmonth = self.nextyear + os.sep + self.nextmonth
        
        directory = os.path.join( self.nextyear, self.nextmonth )
        if os.path.exists( directory ):
            if deletedir:
                for afile in os.listdir( directory ):
                    path = os.path.join(directory, afile)
                    try:
                        if os.path.isfile( path ):
                            os.unlink( path )
                    except Exception, e:
                        print e
            else:
                return 1
        else:
            # the directory does not exist, create it
            os.makedirs( directory )
            
        for catname in self.categories:
            cat = self.categories[catname]
            filedir = os.path.join( directory, catname )
            if catname == "bills" or catname == "income" or catname == "giving":
                # copy over bills and income verbatim.  you can change them yourself,
                # but those should be fairly consistent ;)
                with open(os.path.join(self.rootdir,catname)) as f:
                    content = f.readlines()

                # the only thing that might be different is the starting balance. 
                newcontent = []
                fixedstartingbalance = False
                for c in content:
                    split = c.split()
                    if len(split) and split[0].lower() == "startingbalance":
                        newcontent.append("startingbalance "+str(cat.metavalues["endingbalance"])+"\n")
                        fixedstartingbalance = True
                    else:
                        newcontent.append(c)

                with open(filedir, 'w') as f:
                    if not fixedstartingbalance and cat.metavalues["endingbalance"] != 0:
                        f.write("startingbalance "+str(cat.metavalues["endingbalance"])+"\n")
                    for c in newcontent:
                        f.write(c)

            elif catname in self.accounts:
                # an account just has a starting balance
                with open(filedir, 'w') as f:
                    f.write("account\n")
                    f.write("startingbalance "+str(cat.metavalues["endingbalance"])+"\n")
            elif cat.metaflags["income"]:
                with open(filedir, 'w') as f:
                    f.write("income\n")
            else:
                # regular category
                with open(filedir, 'w') as f:
                    if cat.metaflags["nocarryover"]:
                        # unless we don't carry over
                        f.write("nocarryover\n")
                    elif cat.metavalues["endingbalance"] != 0:
                        f.write("startingbalance "+str(cat.metavalues["endingbalance"])+"\n")

                    try:
                        # check if we have a budget, keep it the same for next month
                        catbudgetline = "budget "+str(cat.metavalues["budget"])+"\n"
                        # but if we have a budget, we also have a starting balance...
                    except KeyError:
                        catbudgetline = "budgetenough\n"
                    
                    f.write(catbudgetline)
                    
        return 0
            


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # only one argument supplied to sys, i.e. this program
        currentyear = time.strftime("%Y")   # 2014, etc.
        currentmonth = time.strftime("%m")  # 01 = jan, ..., 12 = dec
        if os.path.exists( os.path.join( currentyear, currentmonth ) ):
            month = Month( currentyear, currentmonth )
        else:
            raise Exception(" Current month is unavailable in pynances.  Try YYYY"+os.sep+"mm" )
    else:
        if os.path.exists( sys.argv[1] ):
            args = sys.argv[1].split( os.sep )
            YYYY, mm = args[0], args[1]
            month = Month( YYYY, mm )
        else:
            sys.exit(" Month "+sys.argv[1]+" is unavailable in pynances.  Try YYYY"+os.sep+"mm" )

    month.grandtotal( True )


