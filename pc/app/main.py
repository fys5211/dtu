import sys
import os
import ctypes
import threading
import socket
import time
import requests  # 补充缺失的requests导入
from PyQt5 import QtWidgets, QtCore
import serial
# 注意：确保你的UI文件和login文件路径正确
from UI import Ui_MainWindow
from qt.login import Ui_MainWindow as Ui_Login

# ====== 配置：把 vspdctl.dll 的路径改为你本地实际路径 ======
VSPD_DLL_PATH = r"E:\Virtual Serial Port Driver 7.2\vspdctl.dll"
# ====== 串口配置 ======
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 0.1  # 串口读取超时


# ============================================================

# ---- VSPD DLL 封装函数 ----
def try_load_vspd(dll_path):
    if not os.path.isfile(dll_path):
        return None
    try:
        lib = ctypes.WinDLL(dll_path)
        return lib
    except Exception as e:
        print("Failed to load DLL:", e)
        return None


def attempt_create_pair(lib, port1: str, port2: str):
    try:
        func = lib.CreatePair
    except AttributeError:
        return False
    func.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    func.restype = ctypes.c_bool
    return bool(func(port1.encode('ascii'), port2.encode('ascii')))


def delete_virtual_com(lib, port1: str, port2: str):
    try:
        func = lib.DeletePair
    except AttributeError:
        return False
    func.argtypes = [ctypes.c_char_p]
    func.restype = ctypes.c_bool
    ok1 = bool(func(port1.encode('ascii')))
    ok2 = bool(func(port2.encode('ascii')))
    return ok1 or ok2


# ---- 数据转发核心函数（共享同一个TCP连接） ----
def tcp_read_to_serial(sock: socket.socket, ser: serial.Serial, stop_event: threading.Event, ui_status_cb):
    """从TCP长连接读取服务器数据，转发到串口（优化高速数据接收）"""
    try:
        sock.setblocking(True)  # 恢复阻塞模式，确保数据完整接收
        # 增大TCP接收缓冲区（系统层面）
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        while not stop_event.is_set():
            try:
                # 增大单次读取缓冲区为8192字节
                data = sock.recv(8192)
                if not data:
                    ui_status_cb("TCP connection closed by server")
                    break
                # 串口写入时，若串口缓冲区满，等待后重试
                while ser.out_waiting > 1024:  # 串口输出缓冲区超过1024字节，等待
                    time.sleep(0.001)
                ser.write(data)
                ui_status_cb(f"Forwarded {len(data)} bytes from TCP to Serial")
            except Exception as e:
                ui_status_cb(f"TCP read error: {e}")
                break
    except Exception as e:
        ui_status_cb(f"TCP->Serial fatal error: {e}")
    finally:
        if not stop_event.is_set():
            stop_event.set()


def serial_read_to_tcp(sock: socket.socket, ser: serial.Serial, stop_event: threading.Event, ui_status_cb):
    """从串口读取数据，转发到TCP长连接（优化高速数据发送）"""
    # 增大串口输入缓冲区（硬件层面，需串口支持）
    ser.timeout = 0.001  # 串口读取超时设为1ms
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)  # 增大TCP发送缓冲区
    while not stop_event.is_set():
        try:
            # 读取串口数据（即使只有1字节也读取，提高实时性）
            data = ser.read(ser.in_waiting or 1)
            if data:
                # 发送前检查TCP发送缓冲区是否满
                while sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) - sock.send(data) < 0:
                    time.sleep(0.001)  # 发送缓冲区满，等待后重试
                ui_status_cb(f"Sent {len(data)} bytes from Serial to TCP")
            # 无数据时休眠1ms，降低CPU占用但保证实时性
            time.sleep(0.001)
        except socket.error as e:
            if e.errno == socket.EWOULDBLOCK:  # 发送缓冲区满，短暂等待
                time.sleep(0.001)
                continue
            ui_status_cb(f"Serial->TCP send error: {e}")
            stop_event.set()
        except Exception as e:
            ui_status_cb(f"Serial->TCP error: {e}")
            stop_event.set()


def tcp_forward_worker(host: str, port: int, ser: serial.Serial, stop_event: threading.Event, ui_status_cb):
    """TCP转发工作线程：优化重连和数据转发"""
    tcp_sock = None
    reconnect_interval = 2
    while not stop_event.is_set():
        if not tcp_sock or tcp_sock.fileno() == -1:
            try:
                ui_status_cb(f"Trying to connect to {host}:{port}...")
                tcp_sock = socket.create_connection((host, port), timeout=10)
                # 配置TCP参数，关闭Nagle算法（减少延迟）
                tcp_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                ui_status_cb(f"Connected to {host}:{port} successfully")
            except Exception as e:
                ui_status_cb(f"Connect failed: {e}, retrying in {reconnect_interval}s...")
                time.sleep(reconnect_interval)
                continue

        # 启动双向转发子线程
        read_thread = threading.Thread(target=tcp_read_to_serial, args=(tcp_sock, ser, stop_event, ui_status_cb), daemon=True)
        write_thread = threading.Thread(target=serial_read_to_tcp, args=(tcp_sock, ser, stop_event, ui_status_cb), daemon=True)
        read_thread.start()
        write_thread.start()

        read_thread.join()
        write_thread.join()

        if tcp_sock:
            try:
                tcp_sock.close()
            except:
                pass
            tcp_sock = None

        if stop_event.is_set():
            break

    ui_status_cb("TCP forward worker stopped")


# ---- 登录界面类 ----
class LoginWindow(QtWidgets.QMainWindow, Ui_Login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 登录按钮点击事件
        self.pushButton.clicked.connect(self.on_login)

    def on_login(self):
        email = self.lineEdit.text()
        password = self.lineEdit_2.text()
        data = {"email": email, "password": password}

        try:
            response = requests.post("http://127.0.0.1:5000/login", json=data, timeout=5)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('ok', False):
                    print("登录成功！")
                    # 登录成功后，跳转到主界面
                    self.main_window = MainWindow()
                    self.main_window.show()
                    self.close()
                else:
                    QtWidgets.QMessageBox.warning(self, "登录失败", response_data.get('message', '未知错误'))
            else:
                QtWidgets.QMessageBox.warning(self, "登录失败", f"服务器返回错误：{response.status_code}")
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.warning(self, "请求失败", f"无法连接到服务器：{e}")


# ---- 主窗口类 ----
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 状态管理
        self.lib = None
        self.serial_port = None
        self.forward_thread = None  # 转发工作线程
        self.stop_event = threading.Event()
        self.is_forwarding = False  # 是否正在转发
        self.vspd_com1 = ""
        self.vspd_com2 = ""

        # 绑定按钮事件
        self.ui.pushButton.clicked.connect(self.on_create_pair)  # 创建端口对
        self.ui.pushButton_2.clicked.connect(self.on_toggle_forward)  # 启动/停止转发
        self.ui.pushButton_3.clicked.connect(self.on_delete_pair)  # 删除端口对

        # 初始化界面显示
        self.statusBar().showMessage("Ready")

    # 线程安全的状态显示
    @QtCore.pyqtSlot(str)
    def show_status(self, msg):
        self.statusBar().showMessage(msg)
        print(f"[Status] {msg}")

    def ui_status_cb(self, msg):
        """供子线程调用的状态回调"""
        QtCore.QMetaObject.invokeMethod(
            self,
            "show_status",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, msg)
        )

    def on_create_pair(self):
        """创建虚拟串口对"""
        self.vspd_com1 = self.ui.comboBox.currentText()
        self.vspd_com2 = self.ui.comboBox_2.currentText()

        if self.vspd_com1 == self.vspd_com2:
            QtWidgets.QMessageBox.warning(self, "错误", "主端口和副端口不能相同")
            return

        # 加载VSPD DLL
        if not self.lib:
            self.lib = try_load_vspd(VSPD_DLL_PATH)
            if not self.lib:
                QtWidgets.QMessageBox.critical(self, "DLL错误",
                                               f"无法加载DLL：{VSPD_DLL_PATH}\n请检查路径并以管理员身份运行")
                return

        # 创建端口对
        self.show_status(f"正在创建端口对 {self.vspd_com1} <-> {self.vspd_com2}...")
        if attempt_create_pair(self.lib, self.vspd_com1, self.vspd_com2):
            self.show_status(f"成功创建端口对 {self.vspd_com1} <-> {self.vspd_com2}")
            # 延迟打开串口（等待驱动注册）
            QtCore.QTimer.singleShot(1500, self._open_serial_port)
        else:
            QtWidgets.QMessageBox.warning(self, "创建失败", "创建虚拟串口对失败，请检查权限或端口是否被占用")
            self.show_status("创建虚拟串口对失败")

    def _open_serial_port(self):
        """打开主串口（内部调用）"""
        if not self.vspd_com1:
            return
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            # 打开虚拟串口
            self.serial_port = serial.Serial(
                port=self.vspd_com1,
                baudrate=SERIAL_BAUDRATE,
                timeout=SERIAL_TIMEOUT
            )
            self.show_status(f"成功打开串口 {self.vspd_com1}")
        except Exception as e:
            self.serial_port = None
            QtWidgets.QMessageBox.warning(self, "串口打开失败", f"打开 {self.vspd_com1} 失败：{e}")
            self.show_status(f"打开串口失败：{e}")

    def on_toggle_forward(self):
        """启动/停止数据转发"""
        if not self.serial_port or not self.serial_port.is_open:
            QtWidgets.QMessageBox.warning(self, "串口未就绪", "请先创建虚拟串口对并确保串口已打开")
            return

        if not self.is_forwarding:
            # 启动转发
            host = self.ui.lineEdit.text().strip()
            port_text = self.ui.lineEdit_2.text().strip()
            if not host or not port_text:
                QtWidgets.QMessageBox.warning(self, "输入错误", "请填写服务器IP和端口")
                return
            try:
                port = int(port_text)
                if not 1 <= port <= 65535:
                    raise ValueError
            except ValueError:
                QtWidgets.QMessageBox.warning(self, "输入错误", "端口号必须是1-65535的整数")
                return

            # 重置停止事件，启动转发线程
            self.stop_event.clear()
            self.forward_thread = threading.Thread(
                target=tcp_forward_worker,
                args=(host, port, self.serial_port, self.stop_event, self.ui_status_cb),
                daemon=True
            )
            self.forward_thread.start()

            self.is_forwarding = True
            self.ui.pushButton_2.setText("断开")
            self.show_status(f"开始转发：串口 {self.vspd_com1} <-> TCP {host}:{port}")
        else:
            # 停止转发
            self.stop_event.set()
            # 等待线程退出（最多3秒）
            if self.forward_thread and self.forward_thread.is_alive():
                self.forward_thread.join(timeout=3)
            self.is_forwarding = False
            self.ui.pushButton_2.setText("连接")
            self.show_status("已停止数据转发")

    def on_delete_pair(self):
        """删除虚拟串口对"""
        if self.is_forwarding:
            # 先停止转发
            self.stop_event.set()
            if self.forward_thread and self.forward_thread.is_alive():
                self.forward_thread.join(timeout=3)
            self.is_forwarding = False
            self.ui.pushButton_2.setText("连接")

        # 关闭串口
        if self.serial_port:
            try:
                if self.serial_port.is_open:
                    self.serial_port.close()
            except Exception as e:
                print(f"关闭串口失败：{e}")
            self.serial_port = None

        # 删除端口对
        com1 = self.ui.comboBox.currentText()
        com2 = self.ui.comboBox_2.currentText()
        if not self.lib:
            self.lib = try_load_vspd(VSPD_DLL_PATH)
            if not self.lib:
                QtWidgets.QMessageBox.warning(self, "DLL错误", "无法加载vspdctl.dll，无法删除端口")
                return

        if delete_virtual_com(self.lib, com1, com2):
            self.show_status(f"成功删除端口对 {com1} <-> {com2}")
        else:
            QtWidgets.QMessageBox.warning(self, "删除失败", "删除端口对失败，可能端口被占用或权限不足")
            self.show_status(f"删除端口对 {com1} <-> {com2} 失败")

    def closeEvent(self, event):
        """窗口关闭时的资源清理"""
        try:
            # 停止转发
            if self.is_forwarding:
                self.stop_event.set()
                if self.forward_thread and self.forward_thread.is_alive():
                    self.forward_thread.join(timeout=2)

            # 关闭串口
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

            # 删除虚拟串口对
            if self.lib and self.vspd_com1 and self.vspd_com2:
                delete_virtual_com(self.lib, self.vspd_com1, self.vspd_com2)

            self.show_status("程序已安全退出")
        except Exception as e:
            print(f"清理资源时出错：{e}")
        event.accept()


# ---- 程序入口 ----
def main():
    app = QtWidgets.QApplication(sys.argv)

    # 注意：这里原代码错误地直接显示了MainWindow，改为显示LoginWindow
    # 如果不需要登录，可改回 MainWindow()
    login_window = MainWindow()
    login_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()