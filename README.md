pynances
========

Python utility for keeping track of your finances


Requirements
------------

pynances has a command line interface mbf.py, which
is platform independent.  

Better to use pynances.py or pyglances.py for a GUI.
These have different requirements.  pynances.py requires
`ncurses`, which comes with python on UNIX platforms (Mac
and Linux), but not Windows.  pyglances.py uses `pyglet`
and `xerox` (`pip install xerox` works well), and is a little
slower to load graphics and such.

I also thought about porting a GUI to `urwid`, which looks 
quite nice and should be fast.

Usage
-----

Run any of these commands...

    python mbf.py YYYY/mm
    python pynances.py YYYY/mm
    python pyglances.py YYYY/mm

where YYYY and mm are the year (e.g. YYYY = 2016) and month 
(mm = 01 for January, ..., 12 = December) that you wish to investigate.
If you leave off YYYY/mm, you get the current month and year.
On Windows you should use backslashes.

mbf.py
------

This is the brains behind the whole operation, and calculates different
monthly totals, tells python how to add money, etc.
mbf.py handles no user input besides the YYYY/mm explained
above.


pynances.py
-----------

This is a nice user interface to mbf.py, which allows you to edit
your bills and income directly, as well as see your finances visually.  

When you first enter pynances.py, you can go through the Category list by
using arrow up/down keys, or by hitting `k`,`j` keys.  Press tab to switch to
the Account list, which you can navigate similarly.

You can exit pynances.py by hitting escape, or by getting to the command
line and typing any word that starts with q, e.g. quit.

You can access the command line by hitting `:`, `;`, or `/`.
Available commands:

+ `e(dit) ASDF` - edit the file ASDF in the current YYYY/mm directory.      
    
+ `reload` - reloads the month from the current YYYY/mm directory, resets the screen.

+ `load YYYY/mm` - loads the finances from YYYY/mm directory.  mm = 01, 02, ..., 12.

+ `load mm` - loads finances from the current year, but month mm.

+ `generate` - starting from the current YYYY/mm, it generates the correct startingbalances for the next month.

+ `q(uit)` - quits.


pyglances.py
-----------

This is another user interface to `mbf.py`, which allows you to edit
your bills and income directly, as well as see your finances 
visually.  Here you can use standard mouse-over scrolling to view your
accounts and spending categories. 

You can exit pyglances.py by typing `ctrl+W` or `ctrl+Q`, 
or by getting to the command line and typing any word that 
starts with q, e.g. quit.

You can access the command line by hitting `/`.
Available commands:

+ `e(dit) ASDF` - edit the file ASDF in the current YYYY/mm directory.      

+ `e` - edit the scratch file in the root directory.  Also can press `e` outside of command mode to accomplish this.      

+ `s(ave)` - saves the current file that you are editing.  REMEMBER TO SAVE, the program will not remind you (as of now).  You can also press `s` outside of the command mode.
    
+ `reload` - reloads the month from the current YYYY/mm directory, resets the screen.

+ `load YYYY/mm` - loads the finances from YYYY/mm directory.  mm = 01, 02, ..., 12.

+ `load mm` - loads finances from the current year, but month mm.

+ `generate` - starting from the current YYYY/mm, it generates the correct startingbalances for the next month.

+ `q(uit)` - quits.

Other notes:  If you click in the accounts or categories,
you can add (and remove) text, but this does not change any files. 
(Use the reload command, as described above, to reset.)  Press escape
or click somewhere else to lose focus; that will allow you
to enter the command mode by pressing `/`.



Editing files
-------------

In pynances.py, the screen needs to be wide enough for the edit window to appear, 
so you may need to resize your window to edit files.  But to quickly
edit bills, you get to the command line and type `e bills`.

Next you will notice that (for pynances.py)
curses editing makes you want to curse!  I have listed some useful commands
in edit mode at the bottom of the edit window -- notice that "C-k" means
Ctrl+k and similarly for other commands -- but not all of these work on
Mac (I have found that C-o does not work there).  Also on Mac you need
to use C-h to backspace and delete characters.

You may also edit files directly in the YYYY/mm directory, with whatever program
you wish.  If you have a running pynances.py / pyglances.py, you can type
`reload` at the command line to accommodate your file changes.

Look into the examples given in the YYYY/mm directory, but here I explain how it kinda works.
Each file in YYYY/mm is either categorized as an account, an income, or a spending category.
Inside the code they have similar internal variables, but their behavior is quite
different when adding totals and what not.  




### Account files

Use the `account` keyword near the top of your account files, with a descriptive account name
following, e.g. `account Savings Account`.  Accounts should have a `startingbalance`, but no 
`budget`.  More on those later.  To specify the account in any given purchase or transfer,
you use the filename of the account, such as `S` in the example provided for the savings account.

You can add transfers into an account, such as your checking account, from another account
(like the savings account saved in file `S`) by specifying, e.g.:

    Urgent Transfer FROM S 10 USD

which will transfer 10 dollars from your S (Savings) account into whatever
account you put that line in.  Instead of FROM, you can also use PAID,
or FrOm, or from, or PaiD -- these keywords are case insensitive.  See the
PAID/FROM keyword below for additional help.

When you spend things in different categories using a given account, 
DO NOT PUT ANYTHING IN YOUR ACCOUNT FILE.  You will put your purchases in your
spending category file, and the code will be smart enough to know that
money is coming out of that account.


### Income files

These files should have `income` near the top.  Like accounts, they should not have
have a `budget`, but unlike accounts they should not have a `startingbalance`.

You can specify how you get money like this.  For example, if you get some
cash from selling your lamp and you get your check from Macrohard Company, you can
add this to your income file:

    Craigslist Lamp PAID X 30 USD
    Macrohard PAID D 1800 USD

This indicates that your X account (cash) will be credited $30, and that
your D account (debit) will be credited 1800 USD.


### Spending category files

These files can have a few different flags at the top.  If you intend to
save for things in a certain category, you can make that category have
a running total by setting its `startingbalance` and its `budget`; the
`budget` is what you budget for this spending category each month, and the
`startingbalance` is whatever you have left over from the previous month:
    
    startingbalance 0 USD
    budget 30 USD

Then next month, depending on what you spent, the startingbalance might be
greater than zero.  Notice that the balances of your spending categories
are not actual money.  If you spend money, it comes out of your real accounts.
That's why in the pynances.py category overview, it lets you know that
these left-over amounts are "Accumulated anti-savings," and are essentially
the worst damage you can yet do to your accounts each month, besides what
you've already spent.

If you want your spending category budget to reset each month, set the
`nocarryover` flag:

    nocarryover
    budget 35 USD

This means that each month you budget $35 for this category, but you don't
let the left-over pieces accumulate.  Nevertheless, what is currently left
for this month goes into the "Accumulated anti-savings" mentioned earlier.

Finally, if you don't know how much a certain category will require, but
you need to pay for it no matter what, you should use the `budgetenough`
flag.  Very few spending categories should merit this evil tag.  Things
like "bills" however, should.  If you use `budgetenough`, you should not 
set any `budget` amount.


### Keywords

Here is a list of all keywords that have a special meaning to the mbf.py (master)
program, and should be used with care inside of the YYYY/mm directory files.

+ `account` - see "Account files" above.

+ `income` - see "Income files" above.

+ `business` - a business income or category indicates reimbursements and expenses paid by your company.

+ `budget` - for a spending category, the monthly amount you think you will spend.

+ `budgetenough` - budget to pay as much as the spending category requires.

+ `from/FROM` - case insensitive.  Immediately following a FROM you should include the account from which you are paying/transfering money.

+ `recurring/RECURRING` - case insensitive.  First word on an payment/entry which indicates it should be repeated next month.

+ `expecting/EXPECTING` - case insensitive.  First word following `# ` (a hash followed by a space) at the front of a line, to be repeated next month.

+ `paid/PAID` - case insensitive.  Immediately following a PAID you should include the account from which you are paying money.

+ `average/AVERAGE` - case insensitive.  Immediately following an AVERAGE come two things:  first, a concatenation of all months that the bill actually gets paid, e.g. 369D for March, June, September, and December, then the account from which it gets paid.  At the end of the line comes the monthly average drain on your account.


### Examples

Check the YYYY/mm directory for some examples of how to put account files,
income files, and spending category files all together.  Or just load up
pynances.py and check some of them out with the edit command.

Here we just show some examples on how to make payments for certain things.

Here we pay $30 cash for the Lord of the Rings movie:

    Lord of the Rings Movie PAID X 30 USD

In the cash account file, you might have something like this:

    ATM Withdrawal FROM D 50 USD

In the car insurance, you might pay it twice a year at $420 a pop; 
the average monthly cost is $70:

    Gecko Insurance AVERAGE 4O D 70 USD

where `4O` implies that 4 = April, O = October (not a zero) is when the
insurance company takes out the money from your debit account.


Closing remarks
---------------

That is pretty much it.  Hope you find it useful, but no guarantee (see the LICENSE).
If there is a bug somewhere, let me know how to replicate it and I will attempt to 
fix it.

Try to keep your "Monthly expected outpour" (everything budgeted but non-business) 
smaller than your "Monthly expected income" (all your non-business income).
Your "Accumulated anti-savings" is the sum of what is left in each of your spending
categories, and that is the worse damage you can do to your accounts this month,
at least from what you are budgeting.  

Money is a means to an end, but is not life or death!  Remember your Creator
and have fun.


