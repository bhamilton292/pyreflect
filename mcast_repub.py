import argparse
import socket
import struct
import psutil

def validate_multicast_ip(ip):
 
  octets = ip.split('.')
  if len(octets) == 4:
    if 224 <= int(octets[0]) <= 239:
      for octet in octets[1:]:
        if 0 <= int(octet) <= 255:
          return True
  print(f'error: {ip} is not a valid multicast ip address (not in 224.0.0.0/4)')
  return False
         

def validate_mgroups(args):

  print(args)

  if args.mgroup_listen == args.mgroup_repub:
    print(f'error: arguments mgroup-listen and mgroup-repub cannot be the same (both are \'{args.mgroup_listen}\')')
    exit(1)

  if not (validate_multicast_ip(args.mgroup_listen) and validate_multicast_ip(args.mgroup_repub)):
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
