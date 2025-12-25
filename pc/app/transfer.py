import serial
import socket
import threading

# 配置虚拟串口和TCP服务器地址
COM_PORT = 'COM3'  # 虚拟串口
TCP_HOST = '192.168.56.1'  # TCP服务器IP
TCP_PORT = 4197  # TCP服务器端口

# 创建TCP客户端连接
def tcp_to_serial_thread():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((TCP_HOST, TCP_PORT))
        print(f"Connected to TCP server at {TCP_HOST}:{TCP_PORT}")

        while True:
            data = sock.recv(1024)  # 接收TCP数据
            if not data:
                break
            print(f"Received from TCP server: {data}")
            # 将接收到的数据发送到虚拟串口
            serial_port.write(data)

# 监听虚拟串口，发送数据到TCP服务器
def serial_to_tcp_thread():
    while True:
        data = serial_port.read(1024)  # 从虚拟串口读取数据
        if data:
            print(f"Received from COM port: {data}")
            # 将数据发送到TCP服务器
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((TCP_HOST, TCP_PORT))
                sock.sendall(data)

# 设置虚拟串口
serial_port = serial.Serial(COM_PORT, 9600, timeout=1)
print(f"Listening on {COM_PORT}...")

# 启动TCP客户端线程
tcp_thread = threading.Thread(target=tcp_to_serial_thread)
tcp_thread.daemon = True
tcp_thread.start()

# 启动串口监听线程
serial_thread = threading.Thread(target=serial_to_tcp_thread)
serial_thread.daemon = True
serial_thread.start()

# 主线程保持运行
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Program exited.")
    serial_port.close()
