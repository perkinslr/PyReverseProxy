import socket
import array


def send_fd(sock, fd, msg=b"0"):
    return sock.sendmsg([msg], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [fd]))])


def recv_fd(sock, msglen=1):
    fds = array.array("i")
    msg, ancdata, flags, addr = sock.recvmsg(msglen, socket.CMSG_LEN(fds.itemsize))
    for cmsg_level, cmsg_type, cmsg_data in ancdata:
        if (cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS):
            # Append data, ignoring any truncated integers at the end.
            fds.fromstring(cmsg_data[:len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
    return list(fds)[0]


def send_fd_to(path, sock):
    if not isinstance(sock, int):
        sock = sock.fileno()
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(path)
    send_fd(s, sock)

