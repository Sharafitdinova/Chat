from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import datetime

port = 12345
chatLog = []


class ChatProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.name = None
        self.state = "start"

    def getTime(self):
        return '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

    def connectionMade(self):
        self.sendLine("======== Hello! You are successfully connected to the Chat Server!")
        self.sendLine(self.getTime())

        self.sendLine("======== Please, send your name:")

    def connectionLost(self, reason):
        leftMsg = '======== %s has disconnected.' % (self.name,)
        if self.name in self.factory.users:
            del self.factory.users[self.name]
            self.broadcastMessage(leftMsg)
        chatLog.append(self.name + " has disconnected.")
        self.updateSessionInfo()

    def lineReceived(self, line):
        if self.state == "start":
            self.handle_REGISTER(line)
        elif line == "/list":
            self.sendLine('======== List of connected clients: %s ' % (", ".join(self.factory.users)))
        elif line == "/exit":
            self.connectionLost()
        elif line == ":cat:":
            self.sendLine("  /\_/\ \n ( o.o ) \n  > ^ <")
        elif line == ":dog:":
            self.sendLine(" ,-.___,-. \n \_/_ _\_/ \n   )O_O( \n  { (_) } \n   `-^-' ")
        elif line == ":love:":
            self.sendLine(",d88b.d88b,\n88888888888\n'Y8888888Y'\n  'Y888Y'  \n    'Y'  ")
        elif line == ":car:":
            self.sendLine("               .--.      [ATM]\n          .----'   '--.    |\n          '-()-----()-'    |")
        elif line == ":fish:":
            self.sendLine(
                "                       _,--,\n                    .-'---./_    __\n                   /o \\     '-.' /\n                   \  //    _.-'._\ \n                    `'\)--'` ")
        else:
            self.handle_chat(line)

    def handle_REGISTER(self, name):
        if name in self.factory.users:
            self.sendLine("Sorry, name %r is already in use. Try another one, please." % name)
            return

        self.sendLine("======== You always can see the list of connected clients. Just send '/list'.")
        self.sendLine("======== You always can use stikers. Just send ':cat:', ':dog:', ':love:', ':car:', ':fish:'.")
        self.sendLine("======== You always can quit from the chat. Just send '/exit'.")
        self.sendLine('Welcome to the chat, %s!' % (name,))
        self.broadcastMessage('%s has joined to the chat.' % (name,))
        self.broadcastMessage("======== Send '/list' to display the list of connected clients.")
        self.broadcastMessage("======== You always can use stikers. Just send ':cat:', ':dog:', ':love:', ':car:', ':fish:'.")
        self.broadcastMessage("======== You always can quit from the chat. Just send '/exit'.")
        self.name = name
        self.factory.users[name] = self
        self.state = "Chat"
        self.updateSessionInfo()

        if len(self.factory.users) > 1:
            self.sendLine('======== Wow! You can chat with these connected clients: %s ' % (", ".join(self.factory.users)))
        else:
            self.sendLine("======== Unfortunately, here you are only one, %r :(" % name)


    def handle_chat(self, message):
        message = self.getTime() + " %s says: %s" % (self.name, message)
        self.broadcastMessage(message)
        chatLog.append(message)
        self.updateSessionInfo()

    def broadcastMessage(self, message):
        for name, protocol in self.factory.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)
                self.updateSessionInfo()

    def updateSessionInfo(self):
        print('List of connected clients: %s ' % (", ".join(self.factory.users)))
        global chatLog
        chatLog = chatLog[-20:]
        print("\n".join(chatLog))


class ChatFactory(Factory):
    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return ChatProtocol(self)


reactor.listenTCP(port, ChatFactory())
print("Chat server started on port %s" % (port,))
reactor.run()
