import pyglet
from pyglet.gl import *
from pyglet.window import key
import types
import commands
import os

import xerox
# https://github.com/kennethreitz/xerox
# for copy and paste

# the money module
from mbf import *



# HERE RGBA in 0 to 255 for font colors.
EARTHpalette = { "alertfont" : "Monospaced",
                "alertfontsize" : 20,
                "alertfontcolor" : (0,0,0,255), # font in 0 to 255 (R,G,B,A)
                "bodyfont" : "Arial",
                "bodyfontsize" : 12,
                "bodyfontcolor" : (0,0,0,255), # font in 0 to 255 (R,G,B,A)
                "bodybgcolor" : (255,255,200,255),
                "titlefont" : "Monospaced",
                "titlefontsize" : 30,
                "titlefontcolor" : (180,190,255,255), # font in 0 to 255 (R,G,B,A)
                 "background" : (0.8,0.8,0.8,1), # color in 0 to 1 (R,G,B,A)
                 "banner" : (0.4,0.3,0.3,1), 
                 "header" : (0.55,0.35,0.15,1), 
                 "footer" : (0.55,0.35,0.15,1),
                 "widecolumns" : (0.5,0.25,0,0.5) }

DARKAQUApalette = { "alertfont" : "Monospaced",
                "alertfontsize" : 18,
                "alertfontcolor" : (255,255,255,255), # font in 0 to 255 (R,G,B,A)
                "bodyfont" : "Arial",
                "bodyfontsize" : 10,
                "bodyfontcolor" : (150,150,150,255), # font in 0 to 255 (R,G,B,A)
                #"bodyfontcolor" : (255,100,100,255), # font in 0 to 255 (R,G,B,A)
                "bodybgcolor" : (0.1,0.1,0.1,1), # in 0 to 1
                #"bodybgcolor" : (0.2,0,0,1), # in 0 to 1
                "titlefont" : "Monospaced",
                "titlefontsize" : 25,
                "titlefontcolor" : (255,255,255,255), # font in 0 to 255 (R,G,B,A)
                "background" : (0,0,0,1),# color in 0 to 1 (R,G,B,A)
                 "banner" : (0.1,0.3,0.3,1), 
                 "header" : (0.1,0.35,0.15,1), 
                 "footer" : (0.1,0.35,0.15,1),
                 #"widecolumns" : (0.25,0.1,0.25,0.7) } # nice purple!
                 "widecolumns" : (0.7,0.7,0.7,0.2) }

LIGHTAQUApalette = { "alertfont" : "Monospaced",
                "alertfontsize" : 18,
                "alertfontcolor" : (250,200,180,255), # font in 0 to 255 (R,G,B,A)
                "bodyfont" : "Arial",
                "bodyfontsize" : 10,
                "bodyfontcolor" : (20,20,15,255), # font in 0 to 255 (R,G,B,A)
                #"bodyfontcolor" : (255,100,100,255), # font in 0 to 255 (R,G,B,A)
                "bodybgcolor" : (0.9,0.9,0.9,1), # in 0 to 1
                #"bodybgcolor" : (0.2,0,0,1), # in 0 to 1
                "titlefont" : "Monospaced",
                "titlefontsize" : 25,
                "titlefontcolor" : (255,255,255,255), # font in 0 to 255 (R,G,B,A)
                "background" : (0.5,0.5,0.5,1),# color in 0 to 1 (R,G,B,A)
                 "banner" : (0.1,0.3,0.3,1), 
                 "header" : (0.1,0.35,0.15,1), 
                 "footer" : (0.1,0.35,0.15,1),
                 #"widecolumns" : (0.25,0.1,0.25,0.7) } # nice purple!
                 "widecolumns" : (0.2,0.2,0.2,0.5) }

DEFAULTpalette = LIGHTAQUApalette


class Rectangle(object):
    def __init__(self, x1, y1, x2, y2, color, group, batch):
        self.vertex_list = batch.add(4, GL_QUADS, group,
            ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
            ('c4f', [color[0], color[1], color[2], color[3]] * 4))

    def move( self, x1, y1, x2, y2 ):
        self.vertex_list.vertices = [x1, y1, x2, y1, x2, y2, x1, y2]
#    def draw( self ):
#        self.vertex_list.draw( pyglet.gl.GL_QUADS )


class BaseBanner(Rectangle):
    def __init__(self, ytop, height, screenwidth, color, group, batch):
        super(BaseBanner, self).__init__( 0, ytop, screenwidth, ytop-height, color, group, batch ) 
        self.height = height
    
    def move( self, newytop ):
        # move all y positions to where they should be...
        self.vertex_list.vertices[1] = newytop
        self.vertex_list.vertices[3] = newytop
        self.vertex_list.vertices[5] = newytop - self.height
        self.vertex_list.vertices[7] = newytop - self.height
    
    def resize( self,  screenwidth ):
        # move x positions of the rectangle to encompass the full screen
        self.vertex_list.vertices[2] = screenwidth
        self.vertex_list.vertices[4] = screenwidth


class Item( object ):
    def __init__( self, text, foregroundgroup, backgroundgroup, batch, **kwargs ):
        self.interactive = False
        self.text = text
        self.anchor_x = 'center'
        self.anchor_y = 'center'
        # SET PRE DEFAULTS
        self.style = "body"
        self.palette = DEFAULTpalette
        self.width = 100
        self.x = 10
        self.y = 10
        
        # LET USER ADJUST SETTINGS...
        # now set all the stuff from kwargs
        for key, value in kwargs.iteritems():
            setattr( self, key, value )

        # SET POST DEFAULTS.  USER cannot modify these by kwargs.
        self.addtobatch( foregroundgroup, backgroundgroup, batch )

        # to customize later, set via the following methods...

    def gettext( self ):
        return self.text

##  ITEM CLASS
    def deletefrombatch( self ):
        # remove from batch
        try:
            if self.thing and self.thing.batch:
                self.thing.delete()
        except AttributeError:
            pass

    def addtobatch( self, foregroundgroup, backgroundgroup, batch ):
        self.deletefrombatch()
        if self.text:
            self.thing = pyglet.text.Label(self.text,
                                        font_name=self.palette[self.style+"font"],
                                        width=self.width, # changed on resize by default
                                        multiline=True,
                                        font_size=self.palette[self.style+"fontsize"],
                                        color=self.palette[self.style+"fontcolor"],
                                        x=self.x, y=self.y, group=foregroundgroup, batch=batch,
                                        anchor_x=self.anchor_x, anchor_y=self.anchor_y)
            self.height = self.thing.content_height
        else:
            raise TypeError("Should put some text into an item...")
            self.height = 0


    def resize( self, newscreenwidth, newscreenheight ):
        if self.text:
            self.thing.width = newscreenwidth
            self.width = newscreenwidth
            self.height = self.thing.content_height

    def move( self, newx, newy ):
        if self.text:
            self.x = newx
            self.y = newy
            self.thing.x = newx
            self.thing.y = newy
##  ITEM CLASS

#    def draw( self ):
#        if self.drawme and self.text:
#            self.thing.draw()

##  ITEM CLASS
##  ITEM CLASS

    def settext( self, text ):
        self.text = text
        self.thing.text = text
    
    def gettext( self ):
        return self.text # file name


class InteractiveItem( Item ):
    def __init__(self, text, foregroundgroup, backgroundgroup, batch, **kwargs):
        # SET PRE DEFAULTS
        self.palette=DEFAULTpalette
        self.originaltext = text
        self.anchor_x = 'left'
        self.anchor_y = 'top'
        self.style = "body"
        self.multiline = False
        self.scrollable = True
        self.height = 100
        self.width = 400
        self.background = None
        self.x = 10
        self.y = 10
        self.padding = 5

        # LET USER ADJUST SETTINGS...
        # now set all the stuff from kwargs
        for key, value in kwargs.iteritems():
            setattr( self, key, value )
        
        # SET POST DEFAULTS.  USER cannot modify these by kwargs.

        self.interactivemode = "text"

        # create a document object
        self.document = pyglet.text.document.UnformattedDocument( text )

        # set the font style for the document
        self.document.set_style(0, len(self.document.text), 
                        dict(font_size=self.palette[self.style+"fontsize"], 
                             font_name=self.palette[self.style+"font"]))
        if not self.multiline:
            font = self.document.get_font()
            self.height = font.ascent - font.descent

        # CONTINUE TO SET POST DEFAULTS.  USER cannot modify these by kwargs.
        # calculate the height of the box from the font height
        self.interactive = True
        self.addtobatch( foregroundgroup, backgroundgroup, batch )

        # SET POST DEFAULTS.  USER cannot modify these by kwargs.
   
##  INTERACTIVE ITEM CLASS
    def deletefrombatch( self ):
        try:
            if self.thing and self.thing.batch:
                self.thing.delete()
            if self.caret and self.caret.batch:
                self.caret.delete()
            if self.background and self.background.batch:
                self.background.delete()
        except AttributeError:
            pass
        
    def addtobatch( self, foregroundgroup, backgroundgroup, batch ):
        self.deletefrombatch()
        font = self.document.get_font()
        self.thing = pyglet.text.layout.IncrementalTextLayout(
            self.document, self.width, self.height, multiline=self.multiline,
            group=foregroundgroup, batch=batch)
        self.thing.anchor_x = self.anchor_x
        self.thing.anchor_y = self.anchor_y
        self.thing.x = self.x
        self.thing.y = self.y

        self.caret = pyglet.text.caret.Caret( self.thing, batch=batch )
        
        #self.caret.group = foregroundgroup
        if self.background:
            self.background = Rectangle(self.x-self.padding,self.y+self.padding,
                                        self.x+self.width+self.padding,self.y-self.height-self.padding,
                                        self.palette[self.style+"bgcolor"],
                                        backgroundgroup, batch)
        r,g,b,a = self.palette[self.style+"fontcolor"] 
        self.setcolor((r,g,b,a) )
        self.caret.set_style( dict(color=(r,g,b) ) )

    def gettext( self ):
        return self.document.text

    def addtext( self, text="", textstyle={} ):
        lastchar = len(self.document.text)
        self.document.insert_text( lastchar, text )
        if textstyle:
            self.document.set_style( lastchar, len(self.document.text), textstyle )
        else:
            self.document.set_style( lastchar, len(self.document.text), 
                                    dict(bold=False,italic=False) )
    
    def addline( self, line="", textstyle={} ):
        self.addtext( line+"\n", textstyle )

    def loadtextfromfile( self, filename ):
        self.document.text = ""
        try:
            with open(filename) as f:
                data = f.readlines()
            error = 0
        except:
            data = [ "NO SUCCEED IN LOAD" ]
            error = 1

        for line in data:
            self.addtext( line )
        return error

    def getselectedtext( self ):
        if self.caret.mark:
            i1 = min(self.caret.position, self.caret.mark)
            i2 = max(self.caret.position, self.caret.mark)
            return self.document.text[i1:i2]
        else:
            return ""

    def settext( self, text ):
        self.document.delete_text(0, len(self.document.text))
        self.document.insert_text(0, text)

    def setcolor( self, color255 ):
        r,g,b,a = color255
        self.document.set_style(0, len(self.document.text), 
                        dict(color=color255 ) )
        
        # this breaks things if we transition while selecting some text
        #self.caret.set_style( dict(color=(r,g,b) ) )
        
    
##  INTERACTIVE ITEM CLASS

    def move( self, newx, newy ):
        self.x = newx
        self.y = newy
        self.thing.x = newx
        self.thing.y = newy
        if self.background:
            self.background.move( newx-self.padding, newy+self.padding, 
                                    newx+self.width+self.padding, newy-self.height-self.padding)
    
    def resize( self, newscreenwidth, newscreenheight ):
        self.thing.width = newscreenwidth
        self.thing.height = newscreenheight
        self.width = newscreenwidth
        self.height = newscreenheight
        self.thing.anchor_x = self.anchor_x
        self.thing.anchor_y = self.anchor_y
        if self.background:
            self.background.move( self.x-self.padding, self.y+self.padding, 
                                  self.x+self.width+self.padding, self.y-self.height-self.padding)

#    def draw( self ):
#        if self.drawme and self.document.text:
#            self.thing.draw()

##  INTERACTIVE ITEM CLASS

    def gainfocus( self ):
        self.caret.visible = True
        #self.caret.mark = 0
        #self.caret.position = len(self.thing.document.text)

    def losefocus( self ):
        #self.caret.mark = self.caret.position
        #self.caret.mark = self.caret.position
        self.caret.visible = False
        if (self.document.text).strip() == "":
            self.document.text = self.originaltext

        self.thing.anchor_x = self.anchor_x
        self.thing.anchor_y = self.anchor_y

##  INTERACTIVE ITEM CLASS

    def hittest(self, x, y):
        if self.thing.batch:
            if self.anchor_x == "left":
                truth = (0 < x - self.thing.x < self.thing.width)
            elif self.anchor_x == 'right':
                truth = (-self.thing.width < x - self.thing.x < 0)
            else:
                truth = (-self.thing.width//2 < x - self.thing.x < self.thing.width//2)
            
            if truth:
                if self.anchor_y == "bottom":
                    truth = (0 < y - self.thing.y < self.height)
                elif self.anchor_y == 'top':
                    truth = (-self.height < y - self.thing.y < 0)
                else:
                    truth = (-self.height//2 < y - self.thing.y < self.height//2)
            
            return truth
        else:
            return 0
    
##  INTERACTIVE ITEM CLASS

    def mousepress( self, x, y, button, modifiers ):
        self.caret.on_mouse_press( x, y, button, modifiers )

    def mousescroll( self, x, y, scrollx, scrolly ):
        if self.scrollable:
            self.caret.on_mouse_scroll( x, y, scrollx, scrolly )

    def mousedrag( self, x, y, dx, dy, button, modifiers ):
        self.caret.on_mouse_drag( x, y, dx, dy, button, modifiers )

    def dealwithtext( self, text ):
        self.caret.on_text( text )

    def dealwithmotion( self, motion ):
        self.caret.on_text_motion( motion )
    
    def dealwithselectmotion( self, motion ):
        self.caret.on_text_motion_select( motion )

# Pyglance


class Pyglance( pyglet.window.Window ):

##  CLASS PYGLANCE

    def __init__(self, *args, **kwargs):
        # run the pyglet window initialization
        super(Pyglance, self).__init__(900, 550, resizable=True, caption="Pyglance")
        # SET PRE DEFAULTS
        self.palette = DEFAULTpalette
        self.texthandled = True
        self.title = ""
         
        for key, value in kwargs.iteritems():
            setattr( self, key, value )

        # define the groups... things for the batch to handle 
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        self.textground = pyglet.graphics.OrderedGroup(3)
        # define the batch
        self.batch = pyglet.graphics.Batch()

        self.items = [ InteractiveItem('asdf\nasdfasdf\nasdfasdf', self.textground, self.foreground,
                            self.batch,
                            multiline=True, scrollable=True, background=True ),
                    InteractiveItem('asdf\nasd  fasdf\nasdfasdf', self.textground, self.foreground, 
                            self.batch,
                            multiline=True, scrollable=True, background=True ),
                    InteractiveItem('asdf', self.textground, self.foreground, 
                            self.batch,
                            multiline=True, scrollable=True, background=True) ]

        # SET POST DEFAULTS.  USER cannot modify these by kwargs.
        # presentation specific stuff
        # titles
        if self.title:
            self.titlelabel = Item(self.title, self.textground, self.foreground, self.batch, 
                                    anchor_x="left", anchor_y="center",
                                        style="title")

        pyglet.clock.schedule_interval( self.update, 1.0/80 )

        # create the label and text widget for text entry
        self.commandmode = False
        self.alertlabel = Item('asdf',  self.textground, self.foreground, self.batch, 
                                    anchor_y="bottom", anchor_x="left", x=38, y=30,
                                style="alert", palette=self.palette )
        self.alertlabel.resize( 800, 50 ) 
        self.textinput  = InteractiveItem('balasdf', self.textground, self.foreground, self.batch, 
                                     anchor_x="left", anchor_y="bottom", x=115, y=30,
                                               style="alert", palette=self.palette, multiline=False, width=400)
        self.normalcursor = self.get_system_mouse_cursor( self.CURSOR_DEFAULT )
        self.textcursor = self.get_system_mouse_cursor( self.CURSOR_TEXT )
        self.crosscursor = self.get_system_mouse_cursor( self.CURSOR_CROSSHAIR )
        self.textinput.deletefrombatch()
        self.alertlabel.deletefrombatch()

        self.interactives = [ self.textinput ]
        for item in self.items:
            if item.interactive:
                item.losefocus()
                self.interactives.append( item )

        self.alerttime = 0 # length of time left to display the label, if there is a non-command alert

        # set up the initial focus
        self.focus = None
        #self.set_focus(self.textinput)

        self.fullscreenwait = 0

        self.previouscommandtext = ""
       
        # standard header, footer stuff 
        # set some arbitrary defaults for positions of rectangles... they get moved in resize()
        self.header = BaseBanner( 0, 50, 1, self.palette["header"], self.background, self.batch )
        self.banner = BaseBanner( 0, 50, 1, self.palette["banner"], self.foreground, self.batch )
        self.footer = BaseBanner( 0, 50, 1, self.palette["footer"], self.background, self.batch )

        # these guys only appear if we're in wide screen
        self.widebatch = pyglet.graphics.Batch() # batch to use when widescreen
        
        # set some arbitrary defaults for positions of rectangles... they get moved in resize()
        self.leftrectangle = Rectangle( 10, 10, 50, 100, self.palette["widecolumns"], 
                                        self.background, self.widebatch )
        self.rightrectangle = Rectangle( 10, 10, 50, 100, self.palette["widecolumns"], 
                                         self.background, self.widebatch )
        
        self.widecolumnstoedge = True
        self.widecolumnsfullheight = True
        self.alerted = False
        self.lastalert = "Hello!"
        self.loadfile("scratch")


    def gotime( self ):
        pyglet.app.run()

    def alert( self, text="", duration=2 ):
        if text:
            self.alerted = True
            self.alerttime = duration
            self.alertlabel.addtobatch( self.textground, self.foreground, self.batch )
            self.alertlabel.settext( text )
            self.lastalert = text
            #self.alertlabel.move( 60, 30 )
        else:
            # no text, just delete
            self.alerted = False
            self.alertlabel.deletefrombatch()

    def update( self, dt ):
        if self.alerted:
            if self.alerttime > 0:
                self.alerttime -= dt
            else:
                self.alerted = False
                self.alertlabel.deletefrombatch()

        if self.fullscreenwait > 0:
            self.fullscreenwait -= dt
        else:
            self.fullscreenwait = 0


    def setcommand( self, on=True ):
        if on:
            self.alerted = False
            self.alertlabel.addtobatch( self.textground, self.foreground, self.batch )
            self.textinput.addtobatch( self.textground, self.foreground, self.batch )
            self.commandmode = True
            self.alertlabel.settext( "cmd:" )
            self.textinput.settext( "" )
            self.set_focus( self.textinput )
        else:
            # killing command mode.  but let's see what we tried to command
            # remove from batches
            self.alertlabel.deletefrombatch()
            self.textinput.deletefrombatch()

            self.command( (self.textinput.gettext()).strip() )
            self.commandmode = False
            # set the focus back to nothing
            self.set_focus( None )


    def command( self, commandtext ): 
        self.previouscommandtext = commandtext 

        if len(commandtext) > 0:
            if commandtext == "q" or commandtext == "quit":
                pyglet.app.exit()
            else:
                split = commandtext.split()
                if split[0] == "load" or split[0] == "open" or split[0] == "o":
                    if len(split) == 1:
                        self.alert("use load YYYY/mm, or open mm")
                    else:
                        args = split[1].split( os.sep )
                        if len(args) == 1:
                            YYYY = self.YYYY
                            mm = args[0]
                        else:
                            YYYY, mm = args[0], args[1]
                        self.setyearmonth( YYYY, mm, split[1:] )

                    self.loadfile("scratch")
                
                elif split[0] == "reload":
                    self.reload()

                elif split[0][0] == "e":
                    if len(split) == 1:
                        self.loadfile("scratch")
                    else: 
                        self.loadfile(os.path.join(self.month.rootdir, split[1]) )

                elif split[0][0] == "w":
                    self.alert(self.lastalert,10)

                elif split[0][0] == "s":
                    self.savefile()

                elif commandtext == "generate":
                    if self.month.generatenextmonth():
                        self.alert("next month already exists.  type GENERATE to force.", 10)
                    else:
                        self.alert(self.month.nextyearmonth+" generated!", 5)
                
                elif commandtext == "GENERATE":
                    self.month.generatenextmonth( True )
                    self.alert(self.month.nextyearmonth+" re-generated!", 5)

                else:
                    self.alert('unknown command: '+commandtext)

    def loadfile( self, filename ):
        self.items[2].loadtextfromfile( filename )
        self.editfiledir = filename
        self.alert( "editing: "+filename, 4 )

    def savefile( self ):
        with open(self.editfiledir, 'w') as f:
            f.write(self.items[2].gettext())
            self.alert("saved: "+self.editfiledir, 4)
        if self.editfiledir != "scratch":
            self.reload()
            self.alert("saved: "+self.editfiledir+" and reloaded", 5)

##  CLASS PYGLANCE
    def setyearmonth( self, YYYY, mm, errormsg=["YEAR","MONTH"] ):
        path = os.path.join( YYYY, mm )
        if os.path.exists( path ):
            self.month = Month( YYYY, mm )
            self.YYYY = YYYY
            self.mm = mm
            self.month.grandtotal()
            self.load() 
            self.alert(self.month.name+" loaded!", 5)
        else:
            self.alert(" ".join(errormsg)+" is unavailable." )

    def reload( self ):
        self.setyearmonth( self.YYYY, self.mm, ["this","should","work"] )
        self.alert(self.month.name+" reloaded!", 5)

    def load( self ):
        # get our title all set up
        self.title = self.month.name
        try:
            if self.titlelabel:
                self.titlelabel.settext( self.title )

        except AttributeError:
            self.titlelabel = Item(self.title, self.textground, self.foreground, self.batch, 
                                    anchor_x="left", anchor_y="center",
                                        style="title")

        self.items[0].settext("") 
        self.items[1].settext("") 
        self.printtoacctwin()
        self.printtocatwin() 

    def printtoacctwin( self ):
        acctwin = self.items[0]
        
        acctwin.addline( "Account information", dict(bold=True) )
        acctwin.addline()

        starttotaldough = Dough(0)
        endtotaldough = Dough(0)
        for i in range(len(config.ACCOUNTS)):
            account = config.ACCOUNTS[i]
            accountname = config.ACCOUNTnames[i]
            acctwin.addline(accountname+" ("+account+")", dict(bold=True)) # true for bold
            try:
                sbalance = self.month.categories[account].metavalues["startingbalance"]
            except KeyError:
                sbalance = Dough(0)
            acctwin.addline("    start "+str(sbalance))
            starttotaldough += sbalance

            ebalance = self.month.categories[account].metavalues["endingbalance"]
            acctwin.addline("     end "+str(ebalance))
            endtotaldough += ebalance
            acctwin.addline() 
        
        acctwin.addline() 

        acctwin.addline("Totals", dict(bold=True))
        acctwin.addline("    start "+str(starttotaldough.clean()))
        acctwin.addline("     end "+str(endtotaldough.clean()))
        acctwin.addline("   delta "+str(endtotaldough-starttotaldough))

    def printcat( self, cat ):
        # if not an account, it's a category we can analyze more
        catwin = self.items[1]
        if cat.name in config.BUSINESScategories:
            catwin.addline("Business "+str(cat.name), dict(bold=True))
        else:
            catwin.addline(str(cat.name), dict(bold=True))

        if cat.metaflags["income"]:
            catincome = cat.metavalues["changebudget"]
            if cat.metavalues["endingbalance"] != 0:
                catwin.addline("  average "+str(catincome)) 
                catwin.addline("    slush "+str(cat.metavalues["endingbalance"])) 
            else:
                catwin.addline("      got "+str(catincome)) 
        else:
            try:
                catbudget = cat.metavalues["budget"].clean()
                #budgetenough = False
            except KeyError:
                # assume budget enough
                #budgetenough = True
                catbudget = -cat.metavalues["changebudget"].clean()
          
            if cat.name not in config.BUSINESScategories:
                catwin.addline( "   budget "+str(catbudget) )

            try:
                catchange = -cat.metavalues["changeactual"]
            except KeyError:
                catchange = Dough(0)
            
            catwin.addline( "      spent "+str(catchange) )
            
#            if budgetenough:
#                catbalance = Dough(0)
#            else:
            try:
                catbalance = cat.metavalues["endingbalance"]
            except KeyError:
                catbalance = Dough(0)
            
            if catbalance != Dough(0):
                catwin.addline( "          left "+str(catbalance) )
        
        catwin.addline() 

    def printtocatwin( self ):
        catwin = self.items[1]
        catwin.addline( "Spending categories", dict(bold=True) )
        catwin.addline()
        
        sortedcategories = (self.month.categories.keys())
        sortedcategories.sort()
        for category in sortedcategories:
            cat = self.month.categories[category]
            # don't print accounts here, or business categories (yet)
            if not ( cat.metaflags["account"] or category in config.BUSINESScategories ):
                self.printcat( cat )
        
        catwin.addline()

        catwin.addline( "Monthly expected income", dict(bold=True) )
        catwin.addline( "    "+str(self.month.monthlyexpectedincome) )
        catwin.addline( "Monthly expected outpour", dict(bold=True) )
        catwin.addline( "    "+str(self.month.monthlyexpectedoutpour) )
        catwin.addline( "Accumulated anti-savings", dict(bold=True) )
        catwin.addline( "    "+str(self.month.accumulatedantisavings) )

        catwin.addline()
        catwin.addline()

        # now print business categories
        for category in config.BUSINESScategories:
            if category in self.month.categories:
                cat = self.month.categories[category]
                if not cat.metaflags["account"]:
                    self.printcat( cat )
        
        catwin.addline() 

        catwin.addline( "Total actual income", dict(bold=True) )
        catwin.addline( "    "+str(self.month.totalactualincome) )
        catwin.addline( "Total actual spendings", dict(bold=True) )
        catwin.addline( "    "+str(self.month.totalactualspendings) )
        catwin.addline( "Delta", dict(bold=True) )
        catwin.addline( "    "+str(self.month.totalactualincome-self.month.totalactualspendings) )

##  CLASS PYGLANCE


    ##################
    ## Events
    ##################
    def on_resize(self, screenwidth, screenheight):
        # first resize the window based on its own methods...
        super(Pyglance, self).on_resize( screenwidth, screenheight )
        
        # update all the backgroundy type stuff
        self.header.height = min(20, int(0.1*screenheight))
        self.banner.height = 60 
        self.footer.height = min(20, int(0.1*screenheight))
         
        padx = 25
        if (screenwidth // 2 - 2 * screenheight // 3 > 2 * padx):
            self.widescreen = True
            if self.widecolumnstoedge:
                x1 = 0
            else:
                x1 = padx

            if self.widecolumnsfullheight:
                pady = 0 
            else:
                pady = max(20, int(0.05*screenheight) )

            y2 = self.footer.height +  pady # bottom of screen
            y1 = screenheight - self.header.height - self.banner.height - pady # top of screen
            x2 = padx #screenwidth // 2 - 2*screenheight//3 - padx # get the center to be roughly 4:3 aspect ratio

            self.leftrectangle.move(x1,y1,x2,y2)
            x1right = screenwidth - x1
            x2right = screenwidth - x2
            self.rightrectangle.move(x1right,y1,x2right,y2)
            
        else:
            self.widescreen = False
            x2 = padx

        if self.title:
            self.titlelabel.move( x2, screenheight-self.banner.height//2-self.header.height )
            self.titlelabel.resize( 0.9*screenwidth, screenheight )

        self.header.resize( screenwidth )
        self.header.move( screenheight )
        self.banner.resize( screenwidth )
        self.banner.move( screenheight-self.header.height )
        self.footer.resize( screenwidth )
        self.footer.move( self.footer.height )

        # here update all the text stuff

        if self.widescreen:
            self.textinput.move(105, 30)
            self.alertlabel.move(38, 30)
            self.textwidth = screenwidth - 2*x2 - 4*padx
            itemheight = screenheight - (
                    self.header.height + 2*self.banner.height + 2*self.footer.height
                        )
            # grab the height of all the items
            self.items[0].resize( 7*self.textwidth//24, itemheight )
            self.items[1].resize( 7*self.textwidth//24, itemheight )
            self.items[2].resize( 10*self.textwidth//24, itemheight )


            # adjusting everything by the left/top
            xitem = x2 + padx
            for item in self.items:
                item.move( xitem, screenheight - 2*self.header.height - self.banner.height )
                xitem += padx + item.width
        else:
            self.textinput.move(99, 30)
            self.alertlabel.move(20, 30)
            self.textwidth = screenwidth - 2*padx
            pady = self.header.height
            itemheight = screenheight - (
                    self.header.height + 2*self.banner.height + 2*self.footer.height + pady
                        )
            # grab the height of all the items
            self.items[0].resize( (self.textwidth-padx)//2, itemheight//2 )
            self.items[1].resize( (self.textwidth-padx)//2, itemheight//2 )
            self.items[2].resize( self.textwidth, itemheight//2 )


            # adjusting everything by the left/top
            xitem = x2
            yitem = screenheight - self.header.height - self.banner.height - pady
            self.items[0].move( xitem, yitem )
            self.items[1].move( xitem+padx+self.items[0].width, yitem )
            self.items[2].move( xitem, yitem - itemheight//2 - 4*pady/3 )


    def on_draw(self):
        glClearColor(*self.palette["background"]) # background:  (R,G,B,A) with ranges 0 to 1.
        
        # enable transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 

        self.clear()

        self.batch.draw()
        if self.widescreen:
            self.widebatch.draw()

#        for item in self.items:
#            item.draw()
#        
#        # titles
#        if self.title:
#            self.titlelabel.draw()
#
#
#        if self.commandmode:
#            self.alertlabel.draw()
#            self.textinput.draw()
#        elif self.alerttime > 0:
#            self.alertlabel.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        # every time the mouse moves, choose which cursor to use
        hitsuccess = False
        for tin in self.interactives:
            if tin.hittest( x, y ):
                if tin.interactivemode == "text":
                    self.set_mouse_cursor(self.textcursor)
                else:
                    self.set_mouse_cursor(self.crosscursor)
                hitsuccess = True
                break
        
        if not hitsuccess:
            self.set_mouse_cursor( self.normalcursor )

    def on_mouse_press( self, x, y, button, modifiers ):
        # check all the widgets to see if we're in a text box
        hitsuccess = False
        for tin in self.interactives:
            if tin.hittest( x, y ):
                self.set_focus( tin )
                hitsuccess = True
                break
        
        if hitsuccess:
        # run the caret's on_mouse_press function (sets the cursor)
        #if self.focus: 
            self.focus.mousepress( x, y, button, modifiers )
        else:
            self.set_focus( None )
    
    def on_mouse_scroll( self, x, y, scroll_x, scroll_y ):
        # this scrolls whatever is being moused-over
        for tin in self.interactives:
            if tin.hittest( x, y ):
                tin.mousescroll( x, y, scroll_x, scroll_y )
#
#        # this will scroll the focused object first
#        if self.focus:
#            self.focus.mousescroll( x, y, scroll_x, scroll_y )
#        else:
#            for tin in self.interactives:
#                if tin.hittest( x, y ):
#                    tin.mousescroll( x, y, scroll_x, scroll_y )

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focus: 
            self.focus.mousedrag( x, y, dx, dy, buttons, modifiers )

    def on_text( self, text ):
        print "on text ", text, " are we handled? ", self.texthandled

        if self.focus and (not self.texthandled): 
            self.focus.dealwithtext( text )

    def on_text_motion( self, motion ):
        if self.focus: 
            self.focus.dealwithmotion( motion )

    def on_text_motion_select( self, motion ):
        if self.focus: 
            self.focus.dealwithselectmotion( motion )

    def on_key_press( self, symbol, modifiers ):
        # whether we handle the text here 
        self.texthandled = 0
        
        # kill the alert if you push anything
        self.alerttime = 0
        # some global key strokes
        if symbol == key.F11:
            if self.fullscreenwait == 0:
                self.set_fullscreen( not self.fullscreen )
                self.fullscreenwait = 1 # wait a second before allowing switching back
                self.activate()
                self.set_focus(None)
            self.texthandled = 1
        elif (symbol == key.Q or symbol == key.W) and modifiers & key.MOD_CTRL:
            pyglet.app.exit()
        # check for command mode...
        elif self.commandmode:
            if symbol == key.RETURN:
                # if we pressed enter after entering a command...
                self.setcommand( False )
                self.texthandled = 1
        # check for inputting things in some other focus box...
        elif self.focus:
            # if we are focused on some input device, don't let
            # any other commands be available except to possibly escape from it,
            # also basic copy and paste.
            if symbol == key.ESCAPE:
                self.set_focus( None )
                self.texthandled = 1
            elif symbol == key.C and modifiers & key.MOD_CTRL:
                xerox.copy(  self.focus.getselectedtext()  )
                self.texthandled = 1
            elif symbol == key.V and modifiers & key.MOD_CTRL:
                self.focus.dealwithtext( xerox.paste() )
                self.texthandled = 1
        # otherwise look at what it could mean for the global guy
        else:
            if ( symbol == key.Q or symbol == key.ESCAPE ):
                self.texthandled = 1
                self.alert( "ctrl+Q or ctrl+W to quit" )
            elif symbol == key.SLASH:
                self.texthandled = 1
                self.setcommand() # get command mode ready

            elif symbol == key.W:
                self.alert(self.lastalert,10)

            elif symbol == key.S:
                self.savefile()

            elif symbol == key.E:
                self.loadfile( "scratch" )

        print "key press ", symbol, " are we handled? ", self.texthandled
        return pyglet.event.EVENT_HANDLED


    def set_focus(self, focus):
        if self.focus:
            # we previously had something under focus
            if self.focus != focus:
                # we are changing focus to some other part
                self.focus.losefocus()
                
        self.focus = focus
        if self.focus:
            self.focus.gainfocus()
    
##  END CLASS PYGLANCE


if __name__=="__main__":
    if len(sys.argv) == 1:
        # only one argument supplied to sys, i.e. this program
        currentyear = time.strftime("%Y")   # 2014, etc.
        currentmonth = time.strftime("%m")  # 01 = jan, ..., 12 = dec
        if os.path.exists( os.path.join( currentyear, currentmonth ) ):
            presenter = Pyglance()
            presenter.setyearmonth( currentyear, currentmonth )
            presenter.gotime()
        else:
            sys.exit(" Current month is unavailable in pynances.  Try YYYY"+os.sep+"mm" )
    else:
        if os.path.exists( sys.argv[1] ):
            args = sys.argv[1].split( os.sep )
            YYYY, mm = args[0], args[1]
            presenter = Pyglance()
            presenter.setyearmonth( YYYY, mm )
            presenter.gotime()
        else:
            sys.exit(" Month "+sys.argv[1]+" is unavailable in pynances.  Try YYYY"+os.sep+"mm" )


