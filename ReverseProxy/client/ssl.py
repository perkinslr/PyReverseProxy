from twisted.internet import ssl


# noinspection PyMissingConstructor
class OpenSSLContextFactory(ssl.DefaultOpenSSLContextFactory):
    def __init__(self, privateKeyFileName, certificateFileName, chainFileName):
        self.sslmethod = ssl.SSL.SSLv23_METHOD
        self.privateKeyFileName = privateKeyFileName
        self.certificateFileName = certificateFileName
        self.chainFileName = chainFileName
        self.cacheContext()

    def cacheContext(self):
        if self._context is None:
            ctx = ssl.SSL.Context(self.sslmethod)
            # Disallow SSLv2!  It's insecure!  SSLv3 has been around since
            # 1996.  It's time to move on.
            ctx.set_options(ssl.SSL.OP_NO_SSLv2)
            ctx.set_options(ssl.SSL.OP_NO_SSLv3)
            ctx.set_options(ssl.SSL.OP_NO_TLSv1)
            ctx.set_options(ssl.SSL.OP_NO_TLSv1_1)
            ctx.use_certificate_chain_file(self.chainFileName)
            ctx.use_certificate_file(self.certificateFileName)
            ctx.use_privatekey_file(self.privateKeyFileName)

            self._context = ctx


def makeContextFactory(conf):
    return OpenSSLContextFactory(conf.privateKey.path, conf.certificate.path, conf.chain.path)
