#coding=utf-8
"""
p10
"""
import socket

# tcp client
def tcp_client():
    target_host = "www.baidu.com"
    target_port = 80

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((target_host, target_port))
    client.send("GET / HTTP/1.1\r\nHOST: www.baidu.com\r\n\r\n".encode("utf-8"))
    response = client.recv(4096)
    print(response)



tcp_client()
