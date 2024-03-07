import socket
import struct

MCAST_GRP_RCV = '224.0.0.94'
MCAST_PORT_RCV = 5007
MCAST_GRP_REPUB = '224.0.0.98'
MCAST_PORT_REPUB = 5008
IS_ALL_GROUPS = True

sock_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_rcv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock_repub = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_repub.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)


if IS_ALL_GROUPS:
    print('on this port, receives ALL multicast groups')
    sock_rcv.bind(('', MCAST_PORT_RCV))
else:
    print('on this port, listen NOLY to MCAST_GRP_RCV')
    sock_rcv.bind((MCAST_GRP_RCV, MCAST_PORT_RCV))

mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP_RCV), socket.INADDR_ANY)

sock_rcv.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

while True:
  # For Python 3, change next line to "print(sock.recv(10240))"
  message = sock_rcv.recv(10240)
  sock_repub.sendto(message, (MCAST_GRP_REPUB, MCAST_PORT_REPUB))
