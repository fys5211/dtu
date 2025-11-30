import sys
import os
import ctypes
import threading
import socket
import time
from PyQt5 import QtWidgets, QtCore
import serial
from UI import Ui_MainWindow
from qt.login import Ui_MainWindow as Ui_Login

# ====== 配置：把 vspdctl.dll 的路径改为你本地实际路径 ======
VSPD_DLL_PATH = r"E:\Virtual Serial Port Driver 7.2\vspdctl.dll"


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


# ---- 线程函数（转发） ----
def tcp_to_serial_loop(sock: socket.socket, ser: serial.Serial, stop_event: threading.Event, ui_status_cb):
    try:
        while not stop_event.is_set():
            data = sock.recv(4096)
            if not data:
                break
            try:
                ser.write(data)
            except Exception as e:
                ui_status_cb(f"Serial write error: {e}")
                break
    except Exception as e:
        ui_status_cb(f"TCP->Serial error: {e}")
    finally:
        try:
            sock.close()
        except:
            pass


def serial_to_tcp_loop(host: str, port: int, ser: serial.Serial, stop_event: threading.Event, ui_status_cb):
    try:
        while not stop_event.is_set():
            try:
                data = ser.read(4096)
            except Exception as e:
                ui_status_cb(f"Serial read error: {e}")
                break
            if data:
                try:
                    with socket.create_connection((host, port), timeout=5) as s:
                        s.sendall(data)
                except Exception as e:
                    ui_status_cb(f"Serial->TCP send error: {e}")
                    time.sleep(1)
            else:
                time.sleep(0.05)
    except Exception as e:
        ui_status_cb(f"Serial->TCP loop error: {e}")


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

        response = requests.post("http://127.0.0.1:5000/login", json=data)
        if response.status_code == 200:
            response_data = response.json()
            if response_data['ok']:
                print("登录成功！")
                # 登录成功后，跳转到主界面
                self.main_window = MainWindow()  # 主界面
                self.main_window.show()
                self.close()  # 关闭登录界面
            else:
                QtWidgets.QMessageBox.warning(self, "登录失败", response_data['message'])
        else:
            QtWidgets.QMessageBox.warning(self, "请求失败", "无法连接到服务器")


# ---- 主窗口类 ----
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 状态
        self.lib = None
        self.serial_port = None
        self.tcp_thread = None
        self.serial_thread = None
        self.tcp_socket = None
        self.stop_event = threading.Event()
        self.is_bound = False  # 是否已启动转发

        # 绑定按钮事件
        self.ui.pushButton.clicked.connect(self.on_create_pair)  # 创建端口对
        self.ui.pushButton_2.clicked.connect(self.on_connect)  # 连接/断开（绑定）
        self.ui.pushButton_3.clicked.connect(self.on_delete_pair)  # 删除端口对

        # 初始化界面显示（提示）
        self.statusBar().showMessage("Ready")

    # 将状态显示到状态栏（线程安全使用 signal）
    @QtCore.pyqtSlot(str)
    def show_status(self, msg):
        self.statusBar().showMessage(msg)
        print(msg)

    def ui_status_cb(self, msg):
        # 从线程调用时，用信号/slot 回到主线程显示
        QtCore.QMetaObject.invokeMethod(self, "show_status", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, msg))

    def on_create_pair(self):
        com1 = self.ui.comboBox.currentText()
        com2 = self.ui.comboBox_2.currentText()

        if com1 == com2:
            QtWidgets.QMessageBox.warning(self, "Error", "主端口和副端口不能相同")
            return

        # 加载 DLL（若尚未加载）
        if not self.lib:
            self.lib = try_load_vspd(VSPD_DLL_PATH)
            if not self.lib:
                QtWidgets.QMessageBox.critical(self, "DLL Error",
                                               f"无法加载 DLL：{VSPD_DLL_PATH}\n请检查路径并以管理员身份运行。")
                return

        self.show_status(f"Creating pair {com1} <-> {com2} ...")
        ok = attempt_create_pair(self.lib, com1, com2)
        if ok:
            self.show_status(f"Created pair {com1} <-> {com2}")
            # 等待虚拟串口驱动注册端口
            QtCore.QTimer.singleShot(1500, lambda: self.post_create_setup(com1))
        else:
            QtWidgets.QMessageBox.warning(self, "Create Failed", f"创建端口对失败：{com1}, {com2}")
            self.show_status("Create failed")

    def post_create_setup(self, com_primary):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                self.serial_port = None
            self.serial_port = serial.Serial(com_primary, 9600, timeout=0.1)
            self.show_status(f"{com_primary} opened for forwarding (not bound yet)")
        except Exception as e:
            self.serial_port = None
            QtWidgets.QMessageBox.warning(self, "Open Port Failed", f"创建成功但打开 {com_primary} 失败：{e}")
            self.show_status(f"Failed to open {com_primary}: {e}")

    def on_connect(self):
        if not self.serial_port or not self.serial_port.is_open:
            QtWidgets.QMessageBox.warning(self, "Port Closed", "请先创建并打开主端口（Create pair），确保串口已就绪。")
            return

        if not self.is_bound:
            host = self.ui.lineEdit.text().strip()
            port_text = self.ui.lineEdit_2.text().strip()
            if not host or not port_text:
                QtWidgets.QMessageBox.warning(self, "Input Error", "请填写要绑定的 IP 和端口号。")
                return
            try:
                port = int(port_text)
            except:
                QtWidgets.QMessageBox.warning(self, "Input Error", "端口号应为整数。")
                return

            self.stop_event.clear()

            self.serial_thread = threading.Thread(
                target=serial_to_tcp_loop,
                args=(host, port, self.serial_port, self.stop_event, self.ui_status_cb),
                daemon=True
            )
            self.serial_thread.start()

            def tcp_persistent():
                try:
                    with socket.create_connection((host, port)) as s:
                        self.ui_status_cb(f"Connected to {host}:{port}")
                        tcp_to_serial_loop(s, self.serial_port, self.stop_event, self.ui_status_cb)
                except Exception as e:
                    self.ui_status_cb(f"TCP connect error: {e}")

            self.tcp_thread = threading.Thread(target=tcp_persistent, daemon=True)
            self.tcp_thread.start()

            self.is_bound = True
            self.ui.pushButton_2.setText("断开")
            self.show_status("Binding started")
        else:
            self.stop_event.set()
            time.sleep(0.2)
            self.is_bound = False
            self.ui.pushButton_2.setText("连接")
            self.show_status("Binding stopped")

    def on_delete_pair(self):
        com1 = self.ui.comboBox.currentText()
        com2 = self.ui.comboBox_2.currentText()
        if self.is_bound:
            self.stop_event.set()
            time.sleep(0.2)
            self.is_bound = False
            self.ui.pushButton_2.setText("连接")
        if self.serial_port:
            try:
                if self.serial_port.is_open:
                    self.serial_port.close()
            except:
                pass
            self.serial_port = None

        if not self.lib:
            self.lib = try_load_vspd(VSPD_DLL_PATH)
            if not self.lib:
                QtWidgets.QMessageBox.warning(self, "DLL Error", "无法加载 vspdctl.dll，无法删除端口")
                return

        ok = delete_virtual_com(self.lib, com1, com2)
        if ok:
            self.show_status(f"Deleted pair {com1} <-> {com2}")
        else:
            self.show_status(f"Delete failed for {com1} and {com2}")
            QtWidgets.QMessageBox.warning(self, "Delete Failed", "删除端口对失败，可能端口被占用或权限不足。")

    def closeEvent(self, event):
        try:
            if self.is_bound:
                self.stop_event.set()
                time.sleep(0.1)
            if self.serial_port:
                try:
                    if self.serial_port.is_open:
                        self.serial_port.close()
                except:
                    pass
                self.serial_port = None
            if not self.lib:
                self.lib = try_load_vspd(VSPD_DLL_PATH)
            if self.lib:
                com1 = self.ui.comboBox.currentText()
                com2 = self.ui.comboBox_2.currentText()
                delete_virtual_com(self.lib, com1, com2)
        except Exception as e:
            print("Error during cleanup:", e)
        event.accept()


# ---- 程序入口 ----
def main():
    app = QtWidgets.QApplication(sys.argv)

    # 显示登录界面
    window = MainWindow()  # 登录界面
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
