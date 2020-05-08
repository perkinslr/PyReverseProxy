from click import group, option, pass_context, pass_obj
from .configuration import Configuration


@group(chain=True)
@option("--listenPort", default=443, type=int)
@option("--listenInterface", default="", type=str)
@pass_context
def cli(context, listenport, listeninterface):
    context.obj = Configuration(listenport, listeninterface)


@cli.command()
@pass_obj
@option("--hostname", type=str, required=True)
@option("--socket", type=str, required=True)
def vhost(conf: Configuration, socket: str, hostname: str):
    conf.addVHost(hostname, socket)
