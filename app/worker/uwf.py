from PySide6.QtCore import Signal

from .base import BaseWorker
from ..core.services.utils import install_uwf_service


class InstallUWFServiceWorker(BaseWorker):
    """安装 UWF 服务的工作线程"""

    install_result_signal = Signal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        """执行安装 UWF 服务的具体逻辑"""
        # 调用 UWF 服务的安装方法
        self.install_result_signal.emit(install_uwf_service())
