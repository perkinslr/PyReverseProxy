from twisted.python.filepath import FilePath
import ctypes
tlsheader = ctypes.cdll.LoadLibrary(FilePath(__file__).sibling('tlsheader.so').path)
tlsheader.parseHeader.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]


def parse_tls(data):
    out = ctypes.create_string_buffer(255)
    datalen = len(data)
    success = tlsheader.parseHeader(data, datalen, out)
    return success, out.value


def parse_http(data):
    data = data.replace(b'\r\n', b'\n').split(b'\n\n')[0]

    if b'Host' not in data:
        return None

    host = data.split(b'Host:', 1)[1].split(b'\n')[0].strip().split(b':')[0]
    return host


def parse_host(data):
    if data[:3].isalpha():
        try:
            host = parse_http(data)
            if host:
                return host
            success, host = parse_tls(data)
            if success > -1:
                return host
        except:
            return None
    else:
        success, host = parse_tls(data)
        if success > -1:
            return host
        if success == -2:
            return None

        return parse_http(data)


def is_ssl(data):
    success, host = parse_tls(data)
    if success > -1 or success == -2:
        return True


__all__ = ['parse_host', 'is_ssl']
