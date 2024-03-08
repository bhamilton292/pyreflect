import argparse
import socket
import struct
import psutil
from ipaddress import IPv4Address, AddressValueError

def validate_multicast_ip(ip):

  try:
    if IPv4Address(ip).is_multicast:
      return True
  except AddressValueError:
    pass 

  print(f'error: {ip} is not a valid IPv4 multicast address')
  return False
 

def validate_mgroups(args):

  if args.mgroup_listen == args.mgroup_repub:
    print(f'error: arguments mgroup-listen and mgroup-repub cannot be the same (both are \'{args.mgroup_listen}\')')
    exit(1)

  # checked in separate lines to ensure error messages are logged for both when both have bad values
  check_first = validate_multicast_ip(args.mgroup_listen)
  check_second = validate_multicast_ip(args.mgroup_repub)

  if not (check_first and check_second):
    exit(2)


def validate_interface(iface):

  psutil.net_if_addrs()
  ifaces = psutil.net_if_addrs()

  if iface not in ifaces.keys():
    print(f'error: interface {iface} does not exist on this host')
    exit(3)    
  
  if ifaces[iface][0].family == socket.AF_INET:
    return ifaces[iface][0].address
  else:
    print(f'error: interface {iface} is not type AF_INET')
    print(f'the following interfaces on this host are valid:')
    for iface in ifaces:
      if ifaces[iface][0].family == socket.AF_INET:
        print(f'\t{iface}: {ifaces[iface][0].address}')
    exit(4)


def main():

  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--interface', required=True)
  parser.add_argument('-l', '--mgroup-listen', required=True)
  parser.add_argument('-r', '--mgroup-repub',required=True)
  parser.add_argument('-p', '--port',type=int,required=True)

  args = parser.parse_args()

  validate_mgroups(args)
  listen_iface = validate_interface(args.interface)
      
  # create UDP socket
  sock_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock_rcv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  print(f'Binding to {args.mgroup_listen}:{args.port}')
  sock_rcv.bind((args.mgroup_listen, args.port))

  mreq = struct.pack("4s4s", socket.inet_aton(args.mgroup_listen), socket.inet_aton(listen_iface))
  sock_rcv.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

  sock_repub = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock_repub.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

  while True:
    message = sock_rcv.recv(4096)
    sock_repub.sendto(message, (args.mgroup_repub, args.port))


if __name__ == '__main__':
    main()
