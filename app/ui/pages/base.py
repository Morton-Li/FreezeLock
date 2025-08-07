from typing import Any

from PySide6.QtWidgets import QMainWindow, QWidget


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
