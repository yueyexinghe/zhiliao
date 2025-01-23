import sys
import os

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QProgressDialog
from PyQt5.QtCore import pyqtSlot, Qt

from Environment import *
import ApiRequest
from Widget.QMainWindow_CustomMainWindow import CustomMainWindow

from Widget.QWidget_Home import Home
from Widget.QWidget_CreateBook import CreateBook
from Widget.QWidget_BookInfo import BookInfo
from Widget.QWidget_CreateGood import CreateGood
from Widget.QWidget_CreateOrder import CreateOrder
from Widget.QWidget_MyOrder import MyOrder
from Widget.QWidget_OrderInfo import OrderInfo
from Widget.QWidget_UserSettings import UserSettings
from Widget.QWidget_Product import Product
from Widget.QWidget_Counter import Counter


class MainWindow(CustomMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.ui.menuButton_createBook.setVisible(False)
        self.ui.menuButton_product.setVisible(False)
        self.ui.menuButton_counter.setVisible(False)

        self.registerPage("home", Home(), self.ui.menuButton_home)
        self.registerPage("createBook", CreateBook(), self.ui.menuButton_createBook)
        self.registerPage("bookInfo", BookInfo(), self.ui.menuButton_bookInfo)
        self.registerPage("createGood", CreateGood(), self.ui.menuButton_createGood)
        self.registerPage("createOrder", CreateOrder(), self.ui.menuButton_createOrder)
        self.registerPage("myOrder", MyOrder(), self.ui.menuButton_myOrder)
        self.registerPage("userSettings", UserSettings(), self.ui.menuButton_userSettings)
        self.registerPage("product", Product(), self.ui.menuButton_product)
        self.registerPage("counter", Counter(), self.ui.menuButton_counter)
        self.registerPage("orderInfo", OrderInfo())

    @pyqtSlot()
    def on_pushButton_login_clicked(self):
        payload = {
            "username": self.ui.lineEdit_login_username.text(),
            "password": self.ui.lineEdit_login_password.text(),
        }
        if ApiRequest.post("/login", payload) is not None:
            isAdmin = self.ui.lineEdit_login_username.text() == "admin"
            self.ui.menuButton_createBook.setVisible(isAdmin)
            self.ui.menuButton_product.setVisible(isAdmin)
            self.ui.menuButton_counter.setVisible(isAdmin)
            self.ui.titleLabel_username.setText("当前账号：" + self.ui.lineEdit_login_username.text())
            self.toggleLeftMenu(menuEnabled=True)
            self.gotoPage("home")

    @pyqtSlot()
    def on_pushButton_register_clicked(self):
        payload = {
            "username": self.ui.lineEdit_register_username.text(),
            "password": self.ui.lineEdit_register_password.text(),
        }
        if ApiRequest.post("/register", payload) is not None:
            self.gotoPage("login")

    @pyqtSlot()
    def on_pushButton_gotoRegister_clicked(self):
        self.gotoPage("register")

    @pyqtSlot()
    def on_pushButton_gotoLogin_clicked(self):
        self.gotoPage("login")

    @pyqtSlot()
    def on_menuButton_extra_clicked(self):
        self.ui.titleLabel_username.setText("当前账号：游客")
        if ApiRequest.post("/logout") is not None:
            self.toggleLeftMenu(menuEnabled=False)
            self.gotoPage("login")


if __name__ == "__main__":
    log.info("Starting up")

    # 解决高dpi设置下ui的缩放问题
    # Solution 1 目前图标会有显示问题
    # QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    # QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    # Solution 2 legacy
    os.environ["QT_FONT_DPI"] = "96"

    app = QApplication(sys.argv)
    with open(os.path.join(GlobalVar.appPath, "Ui\\themes\\kw_dark.qss"), "r") as fi:
        app.setStyleSheet(fi.read())
    GlobalVar.qApplication = app

    window = MainWindow()
    GlobalVar.mainWindow = window
    window.show()

    window.setWindowTitle("知了 - 二手书交易平台", "知了")
    window.setStatus(status="Idle", version=f"{Const.PROJECT_ID} - v{Const.CURRENT_VERSION}")

    exitcode = app.exec()
    log.info("Exiting, QApplication returned %d", exitcode)
    sys.exit(exitcode)
