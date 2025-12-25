# app.py
# 合并后的 app 界面 + 主逻辑（把 main.py 的逻辑迁移到这里）
# WARNING: 如果你用的是 virtual serial driver，请修改 VSPD_DLL_PATH 为真实路径

import sys
import os
import ctypes
import threading
import socket
import time
from PyQt5 import QtCore, QtGui, QtWidgets
import serial

# 如果登录逻辑需要 requests，可以在登录模块里导入 requests（本文件不做登录请求）
# import requests

# ====== 配置：把 vspdctl.dll 的路径改为你本地实际路径 ======
VSPD_DLL_PATH = r"E:\Virtual Serial Port Driver 7.2\vspdctl.dll"
# ============================================================

# 下面是由 pyuic 生成的 Ui_MainWindow（你原来的 app.py 前半部分）
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1033, 535)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(230, 60, 111, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox_2 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(230, 100, 111, 22))
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(170, 60, 61, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(170, 100, 61, 21))
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(380, 55, 101, 31))
        self.pushButton.setObjectName("pushButton")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(340, 64, 21, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(340, 104, 21, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(351, 70, 20, 41))
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(230, 180, 113, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(230, 220, 113, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(200, 180, 21, 21))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(190, 220, 41, 21))
        self.label_4.setObjectName("label_4")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(380, 95, 101, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(380, 200, 101, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1033, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.comboBox.setItemText(0, _translate("MainWindow", "COM1"))
        self.comboBox.setItemText(1, _translate("MainWindow", "COM2"))
        self.comboBox.setItemText(2, _translate("MainWindow", "COM3"))
        self.comboBox.setItemText(3, _translate("MainWindow", "COM4"))
        self.comboBox.setItemText(4, _translate("MainWindow", "COM5"))
        self.comboBox.setItemText(5, _translate("MainWindow", "COM6"))
        self.comboBox.setItemText(6, _translate("MainWindow", "COM7"))
        self.comboBox.setItemText(7, _translate("MainWindow", "COM8"))
        self.comboBox.setItemText(8, _translate("MainWindow", "COM9"))
        self.comboBox.setItemText(9, _translate("MainWindow", "COM10"))
        self.comboBox.setItemText(10, _translate("MainWindow", "COM11"))
        self.comboBox.setItemText(11, _translate("MainWindow", "COM12"))
        self.comboBox.setItemText(12, _translate("MainWindow", "COM13"))
        self.comboBox.setItemText(13, _translate("MainWindow", "COM14"))
        self.comboBox.setItemText(14, _translate("MainWindow", "COM15"))
        self.comboBox.setItemText(15, _translate("MainWindow", "COM16"))
        self.comboBox.setItemText(16, _translate("MainWindow", "COM17"))
        self.comboBox.setItemText(17, _translate("MainWindow", "COM18"))
        self.comboBox.setItemText(18, _translate("MainWindow", "COM19"))
        self.comboBox.setItemText(19, _translate("MainWindow", "COM20"))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "COM1"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "COM2"))
        self.comboBox_2.setItemText(2, _translate("MainWindow", "COM3"))
        self.comboBox_2.setItemText(3, _translate("MainWindow", "COM4"))
        self.comboBox_2.setItemText(4, _translate("MainWindow", "COM5"))
        self.comboBox_2.setItemText(5, _translate("MainWindow", "COM6"))
        self.comboBox_2.setItemText(6, _translate("MainWindow", "COM7"))
        self.comboBox_2.setItemText(7, _translate("MainWindow", "COM8"))
        self.comboBox_2.setItemText(8, _translate("MainWindow", "COM9"))
        self.comboBox_2.setItemText(9, _translate("MainWindow", "COM10"))
        self.comboBox_2.setItemText(10, _translate("MainWindow", "COM11"))
        self.comboBox_2.setItemText(11, _translate("MainWindow", "COM12"))
        self.comboBox_2.setItemText(12, _translate("MainWindow", "COM13"))
        self.comboBox_2.setItemText(13, _translate("MainWindow", "COM14"))
        self.comboBox_2.setItemText(14, _translate("MainWindow", "COM15"))
        self.comboBox_2.setItemText(15, _translate("MainWindow", "COM16"))
        self.comboBox_2.setItemText(16, _translate("MainWindow", "COM17"))
        self.comboBox_2.setItemText(17, _translate("MainWindow", "COM18"))
        self.comboBox_2.setItemText(18, _translate("MainWindow", "COM19"))
        self.comboBox_2.setItemText(19, _translate("MainWindow", "COM20"))
        self.label.setText(_translate("MainWindow", "主端口"))
        self.label_2.setText(_translate("MainWindow", "副端口"))
        self.pushButton.setText(_translate("MainWindow", "创建端口对"))
        self.label_3.setText(_translate("MainWindow", "ip"))
        self.label_4.setText(_translate("MainWindow", "端口号"))
        self.pushButton_2.setText(_translate("MainWindow", "删除端口对"))
        self.pushButton_3.setText(_translate("MainWindow", "连接"))


# ----------------- 下面是主逻辑：VSPD 封装 + 转发线程 + MainWindow -----------------

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
    # 有些版本 DeletePair 接口不同，这里尝试按名字调用并处理异常
    try:
        func = lib.DeletePair
    except AttributeError:
        return False
    # DeletePair 可能接收一个参数或两个参数，根据你的 SDK 调整
    try:
        func.argtypes = [ctypes.c_char_p]
        func.restype = ctypes.c_bool
        ok1 = bool(func(port1.encode('ascii')))
        ok2 = bool(func(port2.encode('ascii')))
        return ok1 or ok2
    except Exception:
        try:
            func.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return bool(func(port1.encode('ascii'), port2.encode('ascii')))
        except Exception as e:
            print("DeletePair call failed:", e)
            return False


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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.ui.pushButton.clicked.connect(self.on_create_pair)   # 创建端口对
        self.ui.pushButton_2.clicked.connect(self.on_connect)     # 连接/断开（绑定）
        self.ui.pushButton_3.clicked.connect(self.on_delete_pair) # 删除端口对

        # 初始化界面显示（提示）
        self.statusBar().showMessage("Ready")

    # 将状态显示到状态栏（线程安全使用 signal）
    @QtCore.pyqtSlot(str)
    def show_status(self, msg):
        self.statusBar().showMessage(msg)
        # 也打印到控制台以便调试
        print(msg)

    def ui_status_cb(self, msg):
        # 从线程调用时，用 signal/slot 回到主线程显示
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
            # 打开主端口用于转发（波特率、timeout 可根据需要调整）
            self.serial_port = serial.Serial(com_primary, 9600, timeout=0.1)
            self.show_status(f"{com_primary} opened for forwarding (not bound yet)")
        except Exception as e:
            self.serial_port = None
            QtWidgets.QMessageBox.warning(self, "Open Port Failed", f"创建成功但打开 {com_primary} 失败：{e}")
            self.show_status(f"Failed to open {com_primary}: {e}")

    def on_connect(self):
        if not self.serial_port or not getattr(self.serial_port, "is_open", False):
            QtWidgets.QMessageBox.warning(self, "Port Closed", "请先创建并打开主端口（创建端口对），确保串口已就绪。")
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

            # 串口到 TCP 的线程（持续读取串口并发送到远端）
            self.serial_thread = threading.Thread(
                target=serial_to_tcp_loop,
                args=(host, port, self.serial_port, self.stop_event, self.ui_status_cb),
                daemon=True
            )
            self.serial_thread.start()

            # TCP 到串口：建立一个持久连接并把收到的数据写回串口
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
            # 断开绑定
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
                if getattr(self.serial_port, "is_open", False):
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
                    if getattr(self.serial_port, "is_open", False):
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


# 可选：直接运行 app.py 作为独立程序（不含登录）
def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
