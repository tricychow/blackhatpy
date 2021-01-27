#coding=utf-8
import sys
import socket
import threading
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on %s:%s" % (local_host, local_host))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()   # 接受本地请求
        print("[==>] Received incoming connection from %s:%d" % (addr[0], addr[1]))
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port))
        proxy_thread.start()
def proxy_handler(client_socket, remote_host, remote_port, receive_first):  # client_socket本地连接
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # remote_socket远程连接
    remote_socket.connect((remote_host, remote_port))   # 连接远程主机
    if receive_first:   # 如果有必要从远程主机接受数据
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)  # 16进制导出
        remote_buffer = response_handler(remote_buffer) # 针对响应做处理
        if len(remote_buffer):  # 如果有必要发送数据给本地客户端
            print("[<==] Sending %d bytes to local." % len(remote_buffer))
            client_socket.send(remote_buffer)
    while True:
        # 本地主机循环读取数据
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print("[==>] Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)
            # 发送给的本地请求的返回结果
            local_buffer = request_handler(local_buffer)
            # 向远程主机发送数据
            remote_socket.send(local_buffer)
            print("[==>] Send to remote")
        # 接收响应数据
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
            # 发送到响应处理函数
            remote_buffer = response_handler(remote_buffer)
            # 将响应发送给本地socket
            client_socket.send(remote_buffer)
            print("[<==] Send to localhost")
        # 如果两边都没有数据 关闭连接
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break

def hexdump(src, length=16):
    """16进制导出"""
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b" ".join(["%0*X" % (digits, ord(x)) for x in s])    # 4位不满补0 补0个数括号内第一个参数给
        text = b"".join([x if 0x20 <= ord(x) < 0x7f else b"." for x in s])
        result.append(b"%04X    %-*s   %s" % (i, length*(digits+1), hexa, text))
    print(b"\n".join(result))

def receive_from(connection):
    buffer = ""
    # 设置两秒超时这取决于目标情况可能需要调整
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer+=data
    except:
        pass
    return buffer
def request_handler(buffer):
    """对向远程主机的请求进行修改"""
    return buffer
def response_handler(buffer):
    """对向本地主机的响应进行修改"""
    return buffer
def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    # 设置本地监控参数
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    # 设置远程目标
    remote_host = sys.argv[3]
    remote_port = sys.argv[4]
    # 告诉代理在发送给远程主机前连接和接收数据
    receive_first = sys.argv[5]
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    # 设置监听socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
main()