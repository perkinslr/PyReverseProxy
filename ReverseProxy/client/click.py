from click import group, option, pass_context, pass_obj
from twisted.protocols import tls

from twisted.python.filepath import FilePath
import importlib.util


from .configuration import Configuration
from .ssl import makeContextFactory


@group(invoke_without_command=True, chain=True)
@option("--listenPort", type=str, required=True)
@pass_context
def cli(context, listenport):
    context.obj = Configuration(listenport)


@cli.command()
@pass_obj
@option("--privkey", type=str, required=True)
@option("--cert", type=str, required=True)
@option("--chain", type=str, required=True)
def ssl(conf: Configuration, privkey, cert, chain):
    conf.certificate = FilePath(cert)
    conf.chain = FilePath(chain)
    conf.privateKey = FilePath(privkey)
    conf.sslFactory = makeContextFactory(conf)
    if conf.factory:
        conf.tlsFactory = tls.TLSMemoryBIOFactory(conf.sslFactory, False, conf.factory)


@cli.command()
@pass_obj
@option("--application", type=str, required=True)
def launch(conf: Configuration, application: str):
    module, attribute = application.rsplit('.', 1)
    mod = importlib.import_module(module)
    conf.factory = getattr(mod, attribute)
    if conf.sslFactory:
        conf.tlsFactory = tls.TLSMemoryBIOFactory(conf.sslFactory, False, conf.factory)
