import attr


@attr.s()
class Configuration(object):
    listenPort: str = attr.ib()
    sslFactory = attr.ib(None)
    privateKey = attr.ib(None)
    certificate = attr.ib(None)
    chain = attr.ib(None)
    factory = attr.ib(None)
    tlsFactory = attr.ib(None)
