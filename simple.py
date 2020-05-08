from twisted.web.static import File
from twisted.web.server import Site


application = Site(File('.'))
