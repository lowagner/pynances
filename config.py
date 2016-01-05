DEFAULTcurrency = "EURO"
# DEFAULTcurrency = "USD"

# one character abbreviations for months.  should not be equal to any of the above ACCOUNTS... probably.
# these are only used for AVERAGE payment types.
MONTHS = [ "1", "2", "3", "4", "5", "6", "7", "8", "9", "O", "N", "D" ]

# money will have DEFAULTprecision numbers after the decimal point, unless
# otherwise specified in the precision dict below.  
#   e.g. precision = { "YEN" : 3 } to avoid the DEFAULTprecision.
DEFAULTprecision = 2
precision = {} 
        
        
ALLOWEDmetaflags = [ "income", # flags which are either there or not
                     "budgetenough",
                     "nocarryover",
                     "business" ]
ALLOWEDmetavalues = [ "startingbalance", # meta-information with a value
                      "budget" ]
