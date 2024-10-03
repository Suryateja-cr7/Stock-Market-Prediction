import sys
from scapy.all import *
from scapy.layers.inet import TCP
from scapy.layers.inet import UDP

sniffed_packets_all=[]

def tcp_three_way_handshake():
    global sniffed_packets_all

    packets=[]

    print("Capturing Packets for TCP Three-way Handshake")
    
    
    sniffed_packets = sniff(iface="lo", filter="host 142.250.193.206 and (tcp[tcpflags] & (tcp-syn) != 0 or tcp[tcpflags] & (tcp-ack) != 0)", timeout=20)
    
    print("Stopping packet capture")

    syn_src = False
    syn_ack_server = False
    ack_src = False
    sport = 0
    sniffed_packets_all+=sniffed_packets

    for packet in sniffed_packets_all:
        if syn_src == False:
            if packet.haslayer(TCP) and packet[TCP].flags.S:
                if sport == 0:
                    sport = packet[TCP].sport
                syn_src = True
                packets.append(packet)
                continue
        if syn_ack_server == False and packet[TCP].dport == sport and packet.haslayer(TCP) and packet[TCP].flags.S and packet[TCP].flags.A:
            packets.append(packet)
            syn_ack_server = True
            continue
        if ack_src == False and packet[TCP].sport == sport and packet.haslayer(TCP) and packet[TCP].flags.A:
            packets.append(packet)
            ack_src = True
            continue
    print(sport)
    wrpcap("TCP_3_way_handshake_start_2101CS48.pcap", packets)
    return sport

def closing_handshake(sport):
    global sniffed_packets_all

    packets=[]
    
    print("Capturing Packets for Closing Handshake")
    
    sniffed_packets = sniff(iface="lo", filter="host 142.250.193.206 and (tcp[tcpflags] & (tcp-fin) != 0 or tcp[tcpflags] & (tcp-ack) != 0) and not (tcp[tcpflags] & (tcp-syn) == 0)", timeout=30)
    
    print("Stopping packet capture")

    fin_ack_src = False
    fin_ack_server = False
    ack_src = False
    sniffed_packets_all+=sniffed_packets

    for packet in sniffed_packets_all:
        if packet[TCP].flags.S == True:
            continue
        if fin_ack_src == False and packet[TCP].sport == sport and packet[TCP].flags.F and packet[TCP].flags.A:
            fin_ack_src = True
            packets.append(packet)
            continue
        if fin_ack_src == False:
            continue
        if fin_ack_server == False and packet[TCP].dport == sport and packet.haslayer(TCP) and packet[TCP].flags.F and packet[TCP].flags.A:
            packets.append(packet)
            fin_ack_server = True
            continue
        if fin_ack_server==False:
            continue
        if ack_src == False and packet[TCP].sport == sport and packet.haslayer(TCP) and packet[TCP].flags.A:
            packets.append(packet)
            ack_src = True
            continue

    wrpcap("TCP_handshake_close_2101CS48.pcap", packets)

def tcp_packets():
    
    packets=[]
    sport=0

    for packet in sniffed_packets_all:
        if packet.haslayer(TCP) and sport==0:
            sport=packet[TCP].sport
            packets.append(packet)
        else:
            if packet[TCP].dport==sport:
                packets.append(packet)
                break 

    wrpcap("TCP_Packets_2101CS48.pcap", packets)


def udp_packets():
    
    packets=[]
    sport=0

    print("Capturing Packets")
    
    
    sniffed_packets = sniff(iface="lo", timeout=30)
    
    print("Stopping packet capture")
    
    for packet in sniffed_packets:
        if packet.haslayer(UDP) and sport==0:
            sport=packet[UDP].sport
            packets.append(packet)
        else:
            if packet[UDP].dport==sport:
                packets.append(packet)
                break 

    wrpcap("UDP_Packets_2101CS48.pcap", packets)



if __name__ == "__main__":

    # Task 1: Three-way Handshake
    sport=tcp_three_way_handshake()

    # # Task 2: Closing Handshake
    # closing_handshake(sport)

    # #Task 3: TCP Packets
    # tcp_packets()

    # #Task 4: UDP packets
    # udp_packets()

    