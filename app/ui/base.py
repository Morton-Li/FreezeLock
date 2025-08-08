from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from win32com import client

from .widgets.status_bar import StatusBar
from ..core.services import get_wmi_client


class BaseMainWindow(QMainWindow):

    refresh_status_bar_signal = Signal()

    def __init__(
        self,
        title: str = 'FreezeLock',
        size: tuple[int, int] = (960, 520)
    ):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(*size)

        # 主容器
        self._main_widget: QWidget = QWidget()
        self.setCentralWidget(self._main_widget)
        # 主布局
        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self._main_widget.setLayout(self._main_layout)

        # 内容容器
        self._content_wrapper = QWidget()
        self._main_layout.addWidget(self._content_wrapper, stretch=1)

        # 状态栏
        self._status_bar = StatusBar()
        self._main_layout.addWidget(self._status_bar)

        self.refresh_status_bar_signal.connect(self.refresh_status_bar)

        self._wmi_client: client.CDispatch = get_wmi_client()  # WMI 客户端对象

    @property
    def main_widget(self) -> QWidget:
        """
        获取主容器（中央控件）。
        :return: 主容器
        """
        return self._main_widget

    @property
    def main_layout(self) -> QVBoxLayout:
        """
        获取主布局。
        :return: 主布局
        """
        return self._main_layout

    @property
    def content_wrapper(self) -> QWidget:
        """
        获取内容容器。
        :return: 内容容器
        """
        return self._content_wrapper

    @property
    def status_bar(self) -> StatusBar:
        """
        获取状态栏组件。
        :return: 状态栏组件
        """
        return self._status_bar

    @property
    def wmi_client(self) -> client.CDispatch:
        """
        获取 WMI 客户端对象。
        :return: WMI 客户端
        """
        return self._wmi_client

    def refresh_status_bar(self):
        """
        刷新状态栏。
        通过信号触发，子类可以重载此方法以更新状态栏信息。
        """
        raise NotImplementedError("子类必须实现 refresh_status_bar 方法否则不可使用 refresh_status_bar_signal 信号")


class BasePage(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent = parent
        self.services: dict[str, Any] = {}

    def refresh(self):
        """
        页面刷新时调用。可用于重新加载数据或重置状态。
        子类必须实现。
        """
        raise NotImplementedError("子类必须实现 refresh 方法")
