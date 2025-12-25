import socket
import threading
import time

# 定义要转发的两个端口
PORT1 = 8000
PORT2 = 8001
# 绑定的主机地址（0.0.0.0表示监听所有网卡）
HOST = '0.0.0.0'

# 用于存储两个端口的连接套接字
conn1 = None
conn2 = None
# 线程退出标志
stop_flag = False
# 新增：存储转发线程，避免重复启动
forward_threads = {
    "8000_to_8001": None,
    "8001_to_8000": None
}

def handle_data(src_conn, dst_conn, src_port, dst_port):
    """
    处理数据转发：从源连接读取数据，转发到目标连接
    :param src_conn: 源连接套接字
    :param dst_conn: 目标连接套接字
    :param src_port: 源端口（仅用于日志）
    :param dst_port: 目标端口（仅用于日志）
    """
    global stop_flag, conn1, conn2
    try:
        # 新增：设置TCP_NODELAY，减少数据延迟
        src_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        dst_conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        while not stop_flag:
            # 接收数据，缓冲区大小为8192字节（增大缓冲区）
            data = src_conn.recv(8192)
            if not data:
                # 没有数据表示连接关闭
                print(f"[{src_port}→{dst_port}] 连接关闭")
                break
            # 转发数据到目标端口
            dst_conn.sendall(data)
            print(f"[{src_port}→{dst_port}] 转发数据: {len(data)} bytes | {data.hex() if len(data) > 10 else data.decode('utf-8', errors='ignore')}")
    except Exception as e:
        if not stop_flag:
            print(f"[{src_port}→{dst_port}] 转发异常: {e}")
    finally:
        # 关闭连接
        try:
            src_conn.close()
            dst_conn.close()
        except:
            pass
        # 修复2：主动重置连接状态，让新连接能触发转发
        conn1 = None
        conn2 = None
        # 修复2：重置转发线程状态
        if src_port == PORT1:
            forward_threads["8000_to_8001"] = None
        else:
            forward_threads["8001_to_8000"] = None
        print(f"[{src_port}→{dst_port}] 连接已关闭，等待新连接...")

def start_server(port, is_first_port):
    """
    启动单个端口的服务端，等待客户端连接
    :param port: 监听端口
    :param is_first_port: 是否是第一个端口（用于区分conn1/conn2）
    """
    global conn1, conn2, stop_flag, forward_threads
    while not stop_flag:
        # 创建TCP套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置套接字选项，避免端口占用问题
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            # 绑定地址和端口
            server_socket.bind((HOST, port))
            # 开始监听（最大挂起连接数为5，适配多连接）
            server_socket.listen(5)
            print(f"[{port}] 服务端已启动，等待客户端连接...")
            # 等待客户端连接
            conn, addr = server_socket.accept()
            print(f"[{port}] 客户端已连接: {addr}")
            # 保存连接
            if is_first_port:
                conn1 = conn
            else:
                conn2 = conn
            # 当两个端口都有连接时，启动转发线程（修复3：检查线程是否已启动，避免重复）
            if conn1 and conn2:
                # 8000→8001 转发线程
                if not forward_threads["8000_to_8001"] or not forward_threads["8000_to_8001"].is_alive():
                    print("=== 启动8000→8001转发 ===")
                    t1 = threading.Thread(target=handle_data, args=(conn1, conn2, PORT1, PORT2))
                    t1.daemon = True
                    t1.start()
                    forward_threads["8000_to_8001"] = t1
                # 8001→8000 转发线程
                if not forward_threads["8001_to_8000"] or not forward_threads["8001_to_8000"].is_alive():
                    print("=== 启动8001→8000转发 ===")
                    t2 = threading.Thread(target=handle_data, args=(conn2, conn1, PORT2, PORT1))
                    t2.daemon = True
                    t2.start()
                    forward_threads["8001_to_8000"] = t2
                # 修复1：删除t1.join()和t2.join()，避免阻塞监听线程
        except Exception as e:
            if not stop_flag:
                print(f"[{port}] 服务端异常: {e}")
        finally:
            server_socket.close()
            print(f"[{port}] 服务端套接字已关闭")
        # 连接断开后，短暂休眠再重新监听
        if not stop_flag:
            time.sleep(1)

if __name__ == "__main__":
    try:
        # 启动两个端口的服务端线程
        t_server1 = threading.Thread(target=start_server, args=(PORT1, True))
        t_server2 = threading.Thread(target=start_server, args=(PORT2, False))
        t_server1.daemon = True
        t_server2.daemon = True
        t_server1.start()
        t_server2.start()
        # 主线程等待用户输入退出
        input("按回车键退出程序...\n")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    finally:
        stop_flag = True
        # 等待子线程结束
        t_server1.join()
        t_server2.join()
        print("程序已退出")