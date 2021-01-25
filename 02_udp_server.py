#coding=utf-8
import socket

target_host = ""
target_port = 6688

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((target_host, target_port))
while True:
    recv_data = udp_socket.recvfrom(1024)
    print("[%s]:%s" % (str(recv_data[1]), recv_data[0].decode("gb2312")))