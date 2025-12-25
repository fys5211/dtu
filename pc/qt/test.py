from PyQt5.QtWidgets import QMainWindow, QApplication, QStackedWidget, QWidget
from login import Ui_MainWindow as LoginUi  # 导入登录界面的代码
from regist import Ui_MainWindow as RegistUi  # 导入注册界面的代码
from modify import Ui_MainWindow as ModifyUi
from forget import Ui_MainWindow as ForgetUi
from app import MainWindow as AppMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("主窗口")
        self.setGeometry(100, 100, 461, 273)

        # 创建一个堆叠窗口，用于存放登录和注册窗口
        self.stacked_widget = QStackedWidget(self)

        # 创建登录窗口并将其添加到堆叠窗口
        self.login_window = QMainWindow()  # 修改为 QMainWindow
        self.login_ui = LoginUi()
        self.login_ui.setupUi(self.login_window)
        self.login_ui.main_window = self
        self.stacked_widget.addWidget(self.login_window)

        # 创建注册窗口并将其添加到堆叠窗口
        self.regist_window = QMainWindow()  # 修改为 QMainWindow
        self.regist_ui = RegistUi()
        self.regist_ui.setupUi(self.regist_window)
        self.regist_ui.main_window = self  # ← 传入 regist ui
        self.stacked_widget.addWidget(self.regist_window)

        # 创建修改密码窗口并将其添加到堆叠窗口
        self.modify_window = QMainWindow()  # 修改为 QMainWindow
        self.modify_ui = ModifyUi()
        self.modify_ui.setupUi(self.modify_window)
        self.modify_ui.main_window = self  # ← 传入 modify ui
        self.stacked_widget.addWidget(self.modify_window)

        # 创建忘记密码窗口并将其添加到堆叠窗口
        self.forget_window = QMainWindow()  # 修改为 QMainWindow
        self.forget_ui = ForgetUi()
        self.forget_ui.setupUi(self.forget_window)
        self.forget_ui.main_window = self  # ← 传入 forget ui
        self.stacked_widget.addWidget(self.forget_window)

        self.app_window = AppMainWindow(parent=self)  # parent 可选，传 parent 有助于管理
        self.stacked_widget.addWidget(self.app_window)

        # 设置主窗口的中心部件
        self.setCentralWidget(self.stacked_widget)

        # 连接登录窗口的 "注册账号" 按钮事件到切换到注册窗口的方法
        self.login_ui.pushButton_2.clicked.connect(self.show_regist_window)

        # 连接登录窗口的 "修改密码" 按钮事件到切换到修改密码窗口的方法
        self.login_ui.pushButton_3.clicked.connect(self.show_modify_window)

        # 连接登录窗口的 "忘记密码" 按钮事件到切换到忘记密码窗口的方法
        self.login_ui.pushButton_4.clicked.connect(self.show_app_window)

        # 显示登录窗口
        self.stacked_widget.setCurrentWidget(self.login_window)

    def show_regist_window(self):
        # 切换到注册窗口
        self.stacked_widget.setCurrentWidget(self.regist_window)

    def show_modify_window(self):
        # 切换到修改密码窗口
        self.stacked_widget.setCurrentWidget(self.modify_window)

    def show_forget_window(self):
        # 切换到忘记密码窗口
        self.stacked_widget.setCurrentWidget(self.forget_window)

    def show_app_window(self):
        # 切换到应用页面
        self.stacked_widget.setCurrentWidget(self.app_window)
        self.app_window.setFixedSize(1033, 535)  # 这里写你 app 的设计尺寸
        self.resize(1033, 535)

    def show_login_window(self):
        self.stacked_widget.setCurrentWidget(self.login_window)


if __name__ == "__main__":
    app = QApplication([])

    # 创建主窗口并运行
    main_window = MainWindow()
    main_window.show()

    app.exec_()
