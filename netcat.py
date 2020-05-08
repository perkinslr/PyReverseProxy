import os

SERVER_ADDRESS = os.environ.get("UPSTREAM", "127.0.0.1")
SERVER_PORT = int(os.environ.get("UPSTREAM_PORT", 8080))
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, ServerFactory, Protocol
 
class DownstreamProtocol(Protocol):
    def __init__(self):
        self._buffer = []
        self.client = None
 
    def connectionMade(self):
        factory = ClientFactory()
        factory.protocol = UpstreamProtocol
        factory.server = self
        reactor.connectTCP(SERVER_ADDRESS, SERVER_PORT, factory)
 
    def dataReceived(self, data):
        if self.client:
            self.client.write(data)
        else:
            self._buffer.append(data)
 
    def write(self, data):
        self.transport.write(data)
 
class UpstreamProtocol(Protocol):
    def connectionMade(self):
        self.factory.server.client = self
        for b in self.factory.server._buffer:
            self.write(b)
        self.factory.server._buffer.clear()
 
    def dataReceived(self, data):
        self.factory.server.write(data)
 
    def write(self, data):
        if data:
            self.transport.write(data)
 

application = ServerFactory.forProtocol(DownstreamProtocol)
