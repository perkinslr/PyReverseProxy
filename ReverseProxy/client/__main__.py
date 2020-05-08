import sys

from twisted.internet.protocol import ServerFactory

from .configuration import Configuration
from .click import cli
from ..reactor import reactor
from .receiver import FDReceiverProtocol
import click.core
click.core.Exit = SystemExit

def __main__(argv=sys.argv):
    from twisted.python.log import startLogging
    startLogging(sys.stderr)
    configuration: Configuration = cli.main(argv, standalone_mode=False).obj
    reactor.listenUNIX(configuration.listenPort, ServerFactory.forProtocol(lambda: FDReceiverProtocol(configuration)))
    return reactor.run()

if __name__=='__main__':
    argv = sys.argv
    argv[0] = __package__
    raise SystemExit(__main__(argv))

