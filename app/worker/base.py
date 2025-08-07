from PySide6.QtCore import QThread, Signal


class BaseWorker(QThread):
    """基础工作线程类，所有工作线程都应继承此类"""
    def __init__(self):
        super().__init__()
