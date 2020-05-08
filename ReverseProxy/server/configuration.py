import attr
import re


@attr.s()
class VHost(object):
    socket: str = attr.ib()
    hostname = attr.ib(converter=lambda x: re.compile(bytes(x, 'charmap')))


@attr.s()
class Configuration(object):
    listenPort: int = attr.ib()
    listenInterface: str = attr.ib()

    vhosts: list = attr.ib(default=attr.Factory(list))

    def addVHost(self, hostname, socket):
        self.vhosts.append(VHost(socket, hostname))
