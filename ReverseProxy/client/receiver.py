from twisted.internet.interfaces import IFileDescriptorReceiver
from twisted.internet.protocol import Protocol
from zope.interface import implementer

import socket
import os

from .. import reactor
from ..parsers import is_ssl


@implementer(IFileDescriptorReceiver)
class FDReceiverProtocol(Protocol):
    descriptor = None

    def __init__(self, conf):
        self.conf = conf

    def fileDescriptorReceived(self, descriptor):
        # Record the descriptor sent to us
        try:
          sock = socket.fromfd(descriptor, socket.AF_INET, socket.SOCK_STREAM)
          try:
              peek = sock.recv(1024, socket.MSG_PEEK)
          finally:
            sock.close()

            if is_ssl(peek) and self.conf.tlsFactory:
                try:
                    reactor.adoptStreamConnection(descriptor, socket.AF_INET, self.conf.tlsFactory)
                except TypeError:
                    reactor.adoptStreamConnection(descriptor, socket.AF_INET6, self.conf.tlsFactory)

            else:
                try:
                    reactor.adoptStreamConnection(descriptor, socket.AF_INET, self.conf.factory)
                except TypeError:
                    reactor.adoptStreamConnection(descriptor, socket.AF_INET6, self.conf.factory)
        finally:
            os.close(descriptor)
