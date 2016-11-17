# money money money, Must Be Funny, in a rich man's world....
import os, sys
import config
from history import *

def _get_dollars_pennies(amount, currency):
    try:
        precision = config.precision[currency]
    except KeyError:
        precision = config.DEFAULTprecision
    # convert precision from number of decimal places to base 10 number:
    poweroften = 10**precision
   
    # because python rounds to -infinity, we need to check
    # if our amount is less than zero to get correct negative dollars and pennies
    if amount < 0:
        dollars = -(-amount / poweroften) # stuff before the decimal
        pennies = (-amount % poweroften)
    else:
        pennies = amount % poweroften
        dollars = amount / poweroften
    
    return (dollars, pennies, precision)

def _get_dough(string, currency):
    try:
        precision = config.precision[currency]
    except KeyError:
        precision = config.DEFAULTprecision
    # convert precision from number of decimal places to base 10 number:
    precision = 10**precision
  
    return int(round(float(string)*precision))

class Dough(object):
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
        if len(currencies) > 1:
            for currency in currencies:
                if self.dough[currency] == 0:
                    del self.dough[currency]
            
            if len( self.dough ) == 0:
                checkunits = units.upper()
                if checkunits == "EUROS":
                    checkunits = "EURO"
                self.dough[checkunits] = 0

        return self.copy()
    
    def __eq__( self, other ): # ==
        ''' check if doughs are equal '''
        self.clean()
        if isinstance( other, Dough ):
            other.clean()
        elif other == 0:
            for key, val in self.dough.iteritems():
                if val != 0:
                    return False
            return True
        else:
            raise Exception("Comparing dough to non-dough")

        if len(other.dough) != len(self.dough):
            # nonequal lengths, obviously not equal
            return False
        else:
            # equal lengths
            if set(self.dough.keys()) != set(other.dough.keys()):
                # not equal sets of keys (currencies), they are probably not equal
                if len(self.dough) == 1:
                    # if they have equal lengths, but not equal keys, they could
                    # both be equal to zero.  but if they aren't equal to zero,...
                    if (self.dough[ self.dough.keys()[0] ] != 0 or
                        other.dough[ other.dough.keys()[0] ] != 0):
                         # they aren't both zero, so they are not equal!
                         return False
                else:
                    return False
            else:
                # both sets of keys (currencies) are equal
                for key in self.dough.keys():
                    if self.dough[key] != other.dough[key]:
                        return False
                    
        return True
    
    def __ne__( self, other ): # !=
        return not ( self == other )

    def __imul__( self, other ): 
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

    def __iadd__( self, other ): 
        ''' += a dough '''
        try:
            for currency, amount in other.dough.iteritems():
                if currency in self.dough:
                    self.dough[currency] += amount
                elif other.dough[currency] != 0:
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
    
    def __isub__( self, other ): 
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
        ''' subtract two doughs '''
        # first we make a copy of the self into "thedifference"
        thedifference = self.copy()
        # then we add the other dough
        thedifference -= other
        return thedifference

    def __str__( self ):
        ''' print function '''
        string = []
        for currency, amount in self.dough.iteritems():
            # determine how many pennies (or thousandths, etc.)
            # we need based on the currency's precision:
            dollars, pennies, precision = _get_dollars_pennies(amount, currency)
            
            # now format the dollars and pennies:
            if pennies:
                form = "".join(["%d.%0", str(precision), "d %s"])
                string.append( form%(dollars, pennies, currency) )
            else:
                string.append( "%d %s"%(dollars, currency))
            
        return " + ".join(string)


class DoughFromSplit( Dough ):
    ''' another way to get to the dough class, different initialization '''
    def __init__( self, doughsplit ):
        #doughsplit = doughstring.split()
        self.dough = {}
        if len(doughsplit) == 1:
            self.dough[config.DEFAULTcurrency] = _get_dough( doughsplit[0], 
                config.DEFAULTcurrency)
        else:
            i = 0
            nextMinus = 1
            while i < len(doughsplit):
                try:
                    checkunits = doughsplit[i+1].upper()
                    if checkunits == "EUROS":
                        checkunits = "EURO"
                except IndexError:
                    checkunits = config.DEFAULTcurrency
                self.dough[checkunits] = _get_dough( doughsplit[i], checkunits ) * nextMinus
                # check for a minus sign for the next value
                if i + 2 < len(doughsplit) and doughsplit[i+2] == "-":
                    nextMinus = -1
                else:
                    nextMinus = 1
                i += 3

class Entry(object):
    def __init__( self, info ):
        self.name = ""
        self.recurring = False
        self.averaged = False
        self.paidlanguage = ""
        i = len(info)-1
        try:
            while i >= 0:
                infoupper = info[i].upper()
                if infoupper == "PAID" or infoupper == "FROM":
                    self.name = info[:i]
                    self.paidlanguage = info[i]
                    self.account = info[i+1].upper() # capitalize the account
                    i += 2
                    break
                elif infoupper == "PAIDONLY":
                    self.averaged = True
                    self.name = info[:i]
                    self.paidlanguage = info[i] + " " + info[i+1]
                    self.outmonths = info[i+1].upper()
                    self.account = info[i+2].upper()
                    i += 3
                    break
                i -= 1
            if i < 0:
                raise Exception("While parsing %s, Entry expected a PAID/FROM/PAIDONLY" % " ".join(info))
            
            # use index i to get the dough (probably the last few numbers and currencies):
            self.dough = DoughFromSplit( info[i:] )
            self.dough.clean()
        except IndexError:
            raise Exception("While parsing %s, Entry expected Dough after PAID/FROM/PAIDONLY"% " ".join(info))

        # construct name from the list self.name
        if len(self.name) < 1: 
            self.name = "UNKNOWN"
        else:
            # check for a recurring transaction
            if self.name[0].upper() == "RECURRING":
                self.recurring = True
            self.name = " ".join(self.name)

    def budget( self ):
        if self.averaged:
            return self.dough.copy() * (len(self.outmonths)/ 12.0)
        else:
            return self.dough.copy()
        
    def actual( self, month ):
        if self.averaged:
            if config.MONTHS[int(month)-1] in self.outmonths:
                return self.dough.copy()
            else:
                return Dough(0) 
        else:
            return self.budget()

    def __str__( self ):
        return " ".join([self.name, self.paidlanguage, self.account, str(self.dough)])
        

class Category(object):
    def __init__( self, rootdir, name, accountlist ):
        self.name = name
        self.filename = os.path.join( rootdir, name )

        self.metavalues = {} # is a dictionary

        self.metaflags = {}
        for key in config.ALLOWEDmetaflags:
            self.metaflags[key] = False # set them all false
        self.metaflags["account"] = None # account is a special metaflag

        self.parse(accountlist)

#### CATEGORY CLASS
    def parse( self, accountlist ):
        print " Parsing ", self.filename
        
        self.entries = []
        self.nextmonthentries = []
        
        with open (self.filename) as f:
          for line in f:
            split = line.split() # strip leading/trailing white space and split
            if len(split) == 0:
                pass
            elif split[0][0] == "#":
                ## commented line begins with a #
                if len(split) > 1 and split[1].upper() == "EXPECTING":
                    self.nextmonthentries.append(line)
            elif split[0] in config.ALLOWEDmetaflags:
                # if the file is a metaflag
                self.metaflags[ split[0] ] = True
            elif split[0] == "account":
                accountlist[ self.name ] = self.metaflags[ "account" ] = " ".join( split[1:] )
            elif split[0] in config.ALLOWEDmetavalues:
                # then split[0] is a metavalue, and the rest is the value in EUROS
                self.metavalues[split[0]] = DoughFromSplit( split[1:] )
                self.metavalues[split[0]].clean()
            else:
                newentry = Entry(split)
                self.entries.append( newentry ) 
                if newentry.recurring:
                    self.nextmonthentries.append( "%s\n"%str(newentry) )

        if self.metaflags["account"] and self.metaflags["income"]:
            raise Exception("do not put account and income in the same file.")
        if self.metaflags["income"] and self.metaflags["budgetenough"]:
            print "weird:  should not include \"income\" and \"budgetenough\" in file " +self.filename

        # require "ending balance" to get put in:
        if "startingbalance" not in self.metavalues:
            if self.metaflags["account"]:
                print "Warning, expected to see a startingbalance in account", self.name
            self.metavalues["startingbalance"] = Dough(0)
        self.metavalues["endingbalance"] = self.metavalues["startingbalance"].copy()
        
        self.metavalues["changeactual"] = Dough(0)
        self.metavalues["changebudget"] = Dough(0)
            
#### CATEGORY CLASS
    def total( self, categories, month ):
        if self.metaflags["income"]:
            # we will parse an income file 
            totalinbudget = Dough(0)
            totalinactual = Dough(0)

            for e in self.entries:
                # if the income is averaged over many months...
                actuale = e.actual( month )
                budgete = e.budget()
                totalinactual += actuale
                totalinbudget += budgete
   
                accounte = e.account.upper()
                if accounte not in categories:
                    raise Exception("Unknown category/account:  %s.\n Offending Line:  %s" % (e.account, str(e)))
                    
                if categories[accounte].metaflags["account"]:
                    categories[accounte].metavalues["endingbalance"] += actuale
                    categories[accounte].metavalues["changeactual"] += actuale
                    categories[accounte].metavalues["changebudget"] += budgete
                else:
                    raise Exception("Must send income to an account, not a spending/saving category (e.g. %s).\n Offending Line:  %s" % (e.account, str(e)))

            self.metavalues["changeactual"] = totalinactual.clean()
            self.metavalues["changebudget"] = totalinbudget.clean()
            # experimental
            self.metavalues["endingbalance"] += totalinactual - totalinbudget

            return [ totalinactual, totalinbudget  ]

#### CATEGORY CLASS, TOTAL METHOD
        elif self.metaflags["account"]:
            # an account, like a credit card
            deltabalance = Dough(0)
            for e in self.entries:
                actuale = e.actual( month )
                budgete = e.budget()
                deltabalance += actuale
        
                accounte = e.account.upper()
                if accounte not in categories:
                    raise Exception("Unknown category/account:  %s.\n Offending Line:  %s" % (e.account, str(e)))
                # even though this account is getting money in,
                # the account which we used to get the money in must be debited!
                if categories[accounte].metaflags["account"]:
                    categories[accounte].metavalues["endingbalance"] -= actuale
                    categories[accounte].metavalues["changeactual"] -= actuale
                    self.metavalues["changeactual"] += actuale
                    categories[accounte].metavalues["changebudget"] -= budgete
                    self.metavalues["changebudget"] += budgete
                else:
                    raise Exception("Must transfer between accounts, not into/from a spending/saving category (e.g. %s).\n Offending Line:  %s" % (e.account, str(e)))
            
            self.metavalues["endingbalance"] += deltabalance
           
            # transfering between accounts doesn't give you any money...
            return [ Dough(0), Dough(0) ]

#### CATEGORY CLASS, TOTAL METHOD
        else:
            # regular file of things to buy in a certain category
            deltabalance = Dough(0)
            totaloutbudget = Dough(0)
            totaloutactual = Dough(0)

            for e in self.entries:
                actuale = e.actual( month )
                budgete = e.budget()
               
                accounte = e.account.upper()
                if accounte not in categories:
                    raise Exception("Unknown category/account:  %s.\n Offending Line:  %s" % (e.account, str(e)))

                if categories[accounte].metaflags["account"]:
                    # the account which we used to get the money in must be debited!
                    categories[accounte].metavalues["endingbalance"] -= actuale
                    totaloutactual += actuale
                    totaloutbudget += budgete
                    deltabalance -= actuale
                    
                    # take out money from that account, 
                    categories[accounte].metavalues["changeactual"] -= actuale
                    categories[accounte].metavalues["changebudget"] -= budgete
                   
                    # diminish the money in this category:
                    self.metavalues["changeactual"] -= actuale
                    self.metavalues["changebudget"] -= budgete
                else:
                    # take from one category...
                    categories[accounte].metavalues["endingbalance"] -= actuale
                    # and give it to this one:
                    deltabalance += actuale
                    
                    categories[accounte].metavalues["changeactual"] -= actuale
                    self.metavalues["changeactual"] += actuale
                    categories[accounte].metavalues["changebudget"] -= budgete
                    self.metavalues["changebudget"] += budgete
           
            if "budget" in self.metavalues:
                deltabalance += self.metavalues["budget"]
            elif self.metaflags["budgetenough"]:
                deltabalance += totaloutbudget

            self.metavalues["endingbalance"] += deltabalance.clean()
            
            return [ -totaloutactual, -totaloutbudget ]

#### CATEGORY CLASS
    def writenextmonth( self, directory ): 
        with open( os.path.join(directory, self.name), 'w' ) as f:
            # preludes:
            if self.metaflags["account"]:
                f.write("account %s\n"%self.metaflags["account"])
            for flag in config.ALLOWEDmetaflags:
                if self.metaflags[flag]:
                    f.write(flag)
                    f.write("\n")
            if "budget" in self.metavalues:
                f.write("budget %s\n"%self.metavalues["budget"])

            if not self.metaflags["nocarryover"]:
                f.write("startingbalance %s\n"%self.metavalues["endingbalance"])
            
            f.write("\n")
            for line in self.nextmonthentries:
                f.write(line)

        
#### END CATEGORY CLASS

class Month(object):
    def __init__( self, path, YYYY, mm ):
        self.rootdir = os.path.join( path, YYYY, mm )
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

        self.categories = {}
        self.accountlist = {}
        for catname in self.categorynames:
            self.categories[catname.upper()] = Category( self.rootdir, catname, self.accountlist )
        

    def grandtotal( self, printme=False ): 

        self.totaldeltabudget = Dough(0)
        self.totaldeltaactual = Dough(0)
        # first go through everything and get all accounts up to date
        for catname in self.categories:
            cat = self.categories[catname.upper()]
            actual, budget = cat.total( self.categories,
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
            cat = self.categories[catname.upper()]
            if cat.metaflags["income"]:
                # income category
                if not cat.metaflags["business"]:
                    # don't put business stuff in expected income
                    self.monthlyexpectedincome += cat.metavalues["changebudget"]
                # but do put everything in actual income
                self.totalactualincome += cat.metavalues["changeactual"]

            elif not cat.metaflags["account"]:
                # not an account, some other category
                
                # first see what we're budgeting in each category
                if not cat.metaflags["business"]:
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
                self.accumulatedantisavings += cat.metavalues["endingbalance"]



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


        for account in self.accountlist:
            endmonth = self.categories[account.upper()].metavalues["endingbalance"].clean()
            deltamonth = endmonth - self.categories[account.upper()].metavalues["startingbalance"]
            deltamonth.clean()

            if printme:
                print "delta money in ", account, ": ", deltamonth
                print "   end of month account balance: ", endmonth


    def generatenextmonth( self, deletedir=False ):
        nextmonth = self.month + 1
        nextyear = self.year
        if nextmonth > 12:
            nextmonth = 1
            nextyear += 1

        nextyear = str(nextyear)
        nextmonth = format("%02d")%(nextmonth)
        self.nextyearmonth = nextyear + os.sep + nextmonth
        
        directory = os.path.join( nextyear, nextmonth )
        if os.path.exists( directory ):
            if deletedir:
                for afile in os.listdir( directory ):
                    path = os.path.join(directory, afile)
                    try:
                        if os.path.isfile( path ):
                            os.unlink( path )
                    except Exception, e:
                        print e
                        raise Exception("cannot proceed for some reason")
            else:
                return 1
        else:
            # the directory does not exist, create it
            os.makedirs( directory )
           
        # each category is responsible for writing the next month:
        for catname in self.categories:
            self.categories[catname.upper()].writenextmonth( directory )
                    
        return 0
            


if __name__ == "__main__":
    root, YYYY, mm = getrootYYYYmm(sys.argv)

    if root:
        month = Month( root, YYYY, mm )
        month.grandtotal( True )
    else:
        print " YYYY%smm %s%s%s is unavailable in pynances.  Try another?"%(
            os.sep,YYYY,os.sep,mm )



