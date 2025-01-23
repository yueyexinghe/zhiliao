from typing import Optional, Type
from types import TracebackType
import logging
import win32api
import traceback
import rich.console
import rich.logging
import json
import os
import sys

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QApplication

from Widget.QMainWindow_CustomMainWindow import CustomMainWindow
import Widget.QWidget_MessageBox as QWidget_MessageBox


logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[rich.logging.RichHandler(rich_tracebacks=True)])
log = logging.getLogger(str(os.getpid()))

log.info("Initializing environment")


class Const:
    PROJECT_ID = "Zhiliao"
    PROJECT_NAME = "知了"
    CURRENT_VERSION = "0.0.1"


class GlobalVar:
    appPath = ""  # 可执行文件目录
    userPath = ""  # 当前工作目录
    # appConfig = {}
    # userConfig: "UserConfig" = None
    qApplication: QApplication | None = None
    mainWindow: CustomMainWindow | None = None


class MessageBox:
    @staticmethod
    def info(msg: str, title: str = "提示"):
        QApplication.processEvents()
        if GlobalVar.qApplication is not None:
            QWidget_MessageBox.MessageBox(GlobalVar.qApplication.activeWindow(), msg).show()
        else:
            win32api.MessageBox(0, msg, title, 0x40)

    @staticmethod
    def warning(msg: str, title: str = "警告"):
        QApplication.processEvents()
        if GlobalVar.qApplication is not None:
            QMessageBox.warning(GlobalVar.qApplication.activeWindow(), title, msg, QMessageBox.Ok, QMessageBox.Ok)
        else:
            win32api.MessageBox(0, msg, title, 0x30)

    @staticmethod
    def error(msg: str, title: str = "错误"):
        QApplication.processEvents()
        if GlobalVar.qApplication is not None:
            QMessageBox.critical(GlobalVar.qApplication.activeWindow(), title, msg, QMessageBox.Ok, QMessageBox.Ok)
        else:
            win32api.MessageBox(0, msg, title, 0x10)

    @staticmethod
    def prompt(msg: str, title: str = "询问") -> bool:
        QApplication.processEvents()
        if GlobalVar.qApplication is not None:
            return QMessageBox.question(GlobalVar.qApplication.activeWindow(), title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes
        else:
            return win32api.MessageBox(0, msg, title, 0x24) == 0x6


def exceptHook(type_: Type[BaseException], value: BaseException, traceback_: Optional[TracebackType]) -> None:
    log.exception("Unhandled exception:", exc_info=value)
    tbInfo = "".join(traceback.format_exception(type_, value, traceback_))
    if GlobalVar.qApplication is not None:
        MessageBox.error(tbInfo, "未处理的异常")
    else:
        MessageBox.error(tbInfo, "初始化时发生错误")
        raise SystemExit


sys.excepthook = exceptHook


GlobalVar.appPath = os.path.dirname(os.path.abspath(sys.argv[0]))
GlobalVar.userPath = os.path.abspath(os.path.curdir)
log.debug(f"Executable path: {GlobalVar.appPath}")
log.debug(f"Current directory: {GlobalVar.userPath}")
log.debug(f"Command line: {sys.argv}")


class InfoDialog(QtWidgets.QDialog):
    def __init__(self, msg="请稍候...") -> None:
        super().__init__(parent=GlobalVar.qApplication.activeWindow())
        self.setObjectName("Dialog")
        self.resize(250, 75)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.setFont(font)
        self.setModal(True)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.MSWindowsFixedSizeDialogHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setWindowTitle("处理中")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.label_msg = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_msg.setFont(font)
        self.label_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.label_msg.setObjectName("label_msg")
        self.label_msg.setText(msg)
        self.gridLayout.addWidget(self.label_msg, 0, 0, 1, 1)
        QtCore.QMetaObject.connectSlotsByName(self)

    def __enter__(self):
        self.show()
        QApplication.processEvents()

    def __exit__(self, type_: Type[BaseException], value: BaseException, traceback_: Optional[TracebackType]):
        self.close()
        QApplication.processEvents()
        if value is not None:
            raise value
