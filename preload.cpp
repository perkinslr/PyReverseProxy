import std;
import socket;
import dl;
import inet;
import un;
import stat;




static int (*fsocket)(int, int, int) = NULL;
static int (*fbind)(int, const struct sockaddr*, socklen_t) = NULL;
static int (*faccept4)(int, struct sockaddr*, socklen_t*, int) = NULL;

namespace preload {
  template<typename T, std::size_t S>
  struct cmsg_header {
    size_t cmsg_len;
    int cmsg_level;
    int cmsg_type;
    T cmsg_data[S];
  };
  template<typename UserData, std::size_t Count>
  int RecvMsg(int cfd, std::vector<cmsg_header<UserData, Count>> cmsgs, int flags = 0, int iov_len = 1024) {
    std::vector<char> buf(iov_len + 1);
    struct msghdr header;
    struct iovec iov;
    iov.iov_base = &buf[0];
    iov.iov_len = iov_len;
    header.msg_name = nullptr;
    header.msg_iov = &iov;
    header.msg_iovlen = 1;
    if (cmsgs.size() > 0) {
      header.msg_control = &cmsgs[0];
      header.msg_controllen = CMSG_LEN(Count * sizeof(UserData)) * cmsgs.size();
    }
    ssize_t recv_size = recvmsg(cfd, &header, flags);
    
    if (recv_size > 0) {
      if (recv_size > iov_len) {
	recv_size = iov_len;
      }
      if (cmsgs.size() > 0) {
	return cmsgs[0].cmsg_data[0];
      }
      return -1;
    }
    return -1;
  }
  int recvFD(int fd, struct sockaddr* addr, socklen_t* len) {
    cmsg_header<unsigned int, 1> header;
    header.cmsg_len = CMSG_LEN(sizeof(unsigned int) * 1);
    header.cmsg_level = SOL_SOCKET;
    header.cmsg_type = SCM_RIGHTS;
    std::vector<cmsg_header<unsigned int, 1>> headers{ header };
    int newfd = RecvMsg(fd, headers);
    if (newfd < 0) {
      return newfd;
    }
    getpeername(newfd, addr, len);
    return newfd;
  }
  template<typename I>
  inline std::string n2hexstr(I w, size_t hex_len = sizeof(I) << 1) { // Not particularly clean, but efficiently uses SIMD
    static const char *digits = "0123456789ABCDEF";
    std::string rc(hex_len, '0');
    for (size_t i = 0, j = (hex_len - 1) * 4; i < hex_len; ++i, j -= 4)
      rc[i] = digits[(w >> j) & 0x0f];
    return rc;
  }
}
extern "C" {
  int socket(int domain, int type, int protocol) throw() {
    if (domain == AF_INET) {
      domain = AF_UNIX;
    }
    if (!fsocket) {
      fsocket = (int(*)(int,int,int))dlsym(RTLD_NEXT, "socket");
    }
    return (fsocket(domain, type, protocol));
  }

  int bind(int sockfd, const struct sockaddr *addr, socklen_t addrlen) throw(){
    if (!fbind) {
      fbind = (int(*)(int, const struct sockaddr*, socklen_t))dlsym(RTLD_NEXT, "bind");
    }

    if (addr->sa_family != AF_INET) {
      return fbind(sockfd, addr, addrlen);
    }
    
    std::string reroute{""};
    const char *prefix = getenv("REVERSE_PROXY_PREFIX");
    if (!prefix) {
      prefix = "/run/ReverseProxy/tcp";
    }
    
    reroute += prefix;
    const struct sockaddr_in *ipaddr = reinterpret_cast<const struct sockaddr_in*> (addr);

    std::string port = preload::n2hexstr(ipaddr->sin_port);
    std::string address = preload::n2hexstr(ipaddr->sin_addr.s_addr);

    reroute += "/" + address + "/" + port;
    printf("making dir: %s\n", reroute.c_str());

    std::string mkd = "mkdir -p " + reroute;
    system(mkd.c_str());
    reroute += "/proxy.sock";

    struct sockaddr_un uaddr{};
    uaddr.sun_family = AF_UNIX;
    strncpy(uaddr.sun_path, reroute.c_str(), sizeof(uaddr.sun_path) - 1);
    const struct sockaddr * new_addr = reinterpret_cast<const struct sockaddr *>(&uaddr);
    return fbind(sockfd, new_addr, sizeof(uaddr));
  }

  int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen) {
    return accept4(sockfd, addr, addrlen, 0);
  }

  int accept4(int sockfd, struct sockaddr *addr, socklen_t *addrlen, int flags) {
    if (!faccept4) {
      faccept4 = (int(*)(int, struct sockaddr*, socklen_t*, int))dlsym(RTLD_NEXT, "accept4");
    }
    int cfd = faccept4(sockfd, addr, addrlen, flags);
    if (cfd < 0) {
      return cfd;
    }
    return preload::recvFD(cfd, addr, addrlen);
  }


  
  
  
}

