#!/usr/bin/env python3
#
# packet.py -- Wadih Khairallah <woody@smallroom.com>

from struct import *
import sys
import getopt
import socket
import pyshark
from graph import Graph

# Prepare login items for neo4j
scheme = "neo4j"  # Connecting to Aura, use the "neo4j+s" URI scheme
host_name = "192.168.1.202"
port = 7687
url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
user = "neo4j"
password = '12#9akk' 
graph = Graph(url, user, password)

# Default settings
dev = "eth1"
pktCount = 1

# Get options for execution
argv = sys.argv[1:]

try:
	opts, args = getopt.getopt(argv, "i:c:")

except:
	print("error")
	exit()

for opt, arg in opts:
	if opt == '-i':
		dev = arg
	elif opt == '-c':
		pktCount = int(arg)

# Init capture
capture = pyshark.LiveCapture(interface=dev)

# Evaluate each packet
for p in capture.sniff_continuously(packet_count=pktCount):
    #print(p.eth)
    #print(dir(p))
    #print("******")

    proto = "UNKNOWN"
    srcport = ""
    dstport = ""

    # Determine layer 2 
    if 'arp' in p:
        proto = "ARP"
        ipsrc = p.arp.src_proto_ipv4
        ipdst = p.arp.dst_proto_ipv4
        #print(p.arp.field_names)

    # Deterimine layer 3 ipv4 vs ipv6
    if 'ip' in p:
        ipsrc = p.ip.src
        ipdst = p.ip.dst
        #print(p.ip.field_names)

    if 'ipv6' in p:
        ipsrc = p.ipv6.src
        ipdst = p.ipv6.dst
        #print(dir(p))
        #print(p.ipv6.field_names)

    if 'icmpv6' in p:
        proto = "ICMPv6"
        #print(p.icmpv6.field_names)
    
    if 'icmp' in p:
        proto = "ICMP"
        #print(p.icmp.field_names)

    if 'igmp' in p:
        proto = "IGMP"
        #print(p.igmp.field_names)

    # Determine layer 4 protocol
    if 'tcp' in p:
        proto = "TCP"
        srcport = p.tcp.srcport
        dstport = p.tcp.dstport
        #print(p.tcp.field_names)

    if 'udp' in p:
        proto = "UDP"
        srcport = p.udp.srcport
        dstport = p.udp.dstport
        #print(p.udp.field_names)

    if proto == "ARP":
        pass
    elif proto == "UNKNOWN":
        pass
    else:
        graph.create_relation(ipsrc, ipdst)

    '''
    if proto == "ARP":
        pass
        #print(proto + " " + ipsrc + " --> " + ipdst)
    elif proto == "ICMP" or proto == "ICMPv6" or proto == "IGMP":
        print(proto + " " + ipsrc + " --> " + ipdst)
    elif proto == "UNKNOWN":
        pass
        #print(proto + "<----")
        print(dir(p))
        #print("********")
    else:
        print(proto + " " + ipsrc + ":" + srcport + " --> " + ipdst + ":" + dstport)
    '''

graph.close()
