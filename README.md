# PyReverseProxy
Transparent reverse proxy (mainly for HTTP and HTTPS) using python

## Requirements
You can install the requirements via `python -m pip install -r requirements.txt`, or look through the requirements file and add them via your package manager.

## Server Side
The server side can be started by running `python -m ReverseProxy.server`, try `--help` to see the usage string.  For a simple example, listening for one virtual host, use:

`python -m ReverseProxy.server --listenInterface 0.0.0.0 --listenPort=8080 vhost --hostname some.regex.com --socket /path/to/unix/socket`

When a connection comes in with the SSL SNI or HTTP Host line matching the specified regex, the connection will get passed to through the socket specified

## Client side
The python side can be started by running `python -m ReverseProxy.client`, try `--help` to see the usage string.  For a simple example (non ssl) use:
`python -m ReverseProxy.client --listenPort /path/to/unix/socket --application fully.qualified.python.name.of.twisted.application` 

Most other web servers can be used as clients, using an LD_PRELOAD library.  The LD_PRELOAD library needs to intercept listening on some tcp port and instead listen on a UNIX socket.  A simple LD_PRELOAD library is included.  To set the proxy socket location, set `REVERSE_PROXY_PORT=/path/to/unix/socket`.  For programs trying to listen on lots of sockets, set `REVERSE_PROXY_PREFIX=/path/to/unix` and it will make subfolders for each hostname/port combination (hex encoded).
