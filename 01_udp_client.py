#coding=utf-8
import socket
# udp client
def udp_client():
    target_host = "127.0.0.1"
    target_port = 6688
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto("AAABBBCCC", (target_host, target_port))
    data, addr = client.recvfrom(4096)
    print(data)
    print(addr)
udp_client()