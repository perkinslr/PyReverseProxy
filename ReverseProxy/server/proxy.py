from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet.protocol import ServerFactory, Protocol, Factory
from twisted.internet import error
import socket
from functools import partial

from ..reactor import reactor
from .configuration import Configuration
from ..parsers import parse_host
from .._proxy import send_fd


class ProxyProtocol(Protocol):
    def __init__(self, parent):
        self.parent = parent

    def fakeRead(self):
        sock = self.transport.socket
        try:
            data = sock.recv(self.transport.bufferSize, socket.MSG_PEEK)
        except socket.error as se:
            if se.args[0] == socket.EWOULDBLOCK:
                return
            else:
                return error.getConnectError(se)

        host = parse_host(data)
        self.parent.passTo(host, self)

    def connectionMade(self):
        self.transport.doRead = partial(self.fakeRead)


class ProxyFactory(ServerFactory):
    def __init__(self, configuration: Configuration):
        self.vhosts = configuration.vhosts
        self.sockets = set()

    def buildProtocol(self, addr):
        return ProxyProtocol(self)

    def passTo(self, host, protocol):
        orig_socket = protocol.transport.socket

        if not host:
            host = b'default'
        try:
            for vhost in self.vhosts:
                if vhost.hostname.match(host):
                    dest_socket = vhost.socket
                    endpoint = UNIXClientEndpoint(reactor, dest_socket)
                    connected = endpoint.connect(Factory.forProtocol(Protocol))
                    connected.addCallback(partial(self.passClientTo, orig_socket))
                    connected.addBoth(partial(self.disconnect, protocol))
                    return
        finally:
            pass
            # protocol.transport.socket.close()

    @staticmethod
    def passClientTo(socket, protocol):
        try:
            send_fd(protocol.transport.socket, socket.fileno())
        finally:
            return protocol

    @staticmethod
    def disconnect(orig_protocol, protocol):
        if isinstance(protocol, Protocol):
            protocol.transport.loseConnection()
        orig_protocol.transport._shouldShutdown = False
        orig_protocol.transport.loseConnection()


def run(configuration: Configuration):
    reactor.listenTCP(configuration.listenPort, ProxyFactory(configuration), interface=configuration.listenInterface)
    reactor.run()
