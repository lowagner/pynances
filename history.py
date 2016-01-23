import os, time

def getrootYYYYmm(args, mayberoot="."):
    # get the year and month from args, if possible.
    YYYY = None
    mm = None
    if len(args) == 1:
        # only one argument supplied to sys, i.e. this program
        YYYY = time.strftime("%Y")   # 2014, etc.
        mm = time.strftime("%m")  # 01 = jan, ..., 12 = dec
        if os.path.exists(os.path.join(mayberoot, YYYY, mm)):
            rootdir = mayberoot
    else:
        split = args[1].split(os.sep)
        print split
        if len(split) == 1: # just a month probably...
            YYYY = time.strftime("%Y")   # 2014, etc.
            if os.path.exists(os.path.join(mayberoot, YYYY, split[0])):
                rootdir = mayberoot
                mm = split[0]
        elif len(split) == 2: # probably year and month
            YYYY, mm = split[0], split[1]
            if os.path.exists(os.path.join(mayberoot, YYYY, mm)):
                rootdir = mayberoot
        else: # probably a full path
            if split[0] == "~":
                split[0] = os.path.expanduser("~")
            rootdir = os.sep.join(split[:-2])
            YYYY, mm = split[-2], split[-1]
            if not os.path.exists(os.path.join(rootdir, YYYY, mm)):
                rootdir = None

    if YYYY is None or mm is None:
        print "got YYYY, mm ", YYYY, mm
        rootdir = None

    return rootdir, YYYY, mm

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

