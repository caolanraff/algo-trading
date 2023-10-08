import sys
import time
import quickfix as fix
import quickfix42 as fix42


class Application(fix.Application):
    def onCreate(self, sessionID):
        return

    def onLogon(self, sessionID):
        self.sessionID = sessionID
        print("Successful logon to session '%s'." % sessionID.toString())
        return

    def onLogout(self, sessionID):
        return

    def toAdmin(self, sessionID):
        return

    def fromAdmin(self, sessionID):
        return

    def toApp(self, sessionID, message):
        print("Sent the following message: %s" % message.toString())
        return

    def fromApp(self, sessionID, message):
        print("Received the following message: %s" % message.toString())
        return

    def subscribe(self):
        if self.marketSession is None:
            self.lo
