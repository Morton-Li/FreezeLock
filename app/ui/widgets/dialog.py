import subprocess
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout, QPushButton, QHBoxLayout


class BaseDialog(QDialog):
    def __init__(
        self,
        title: str,
        size: tuple[int, int] = (400, 200),
        modal: bool = True,
    ):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(*size)
        self.setModal(modal)


class InstallUWFServiceDialog(BaseDialog):
    """对话框，用于显示安装 UWF 服务的进度"""
    def __init__(self):
        super().__init__(
            title="安装 UWF 服务",
            size=(300, 100),
            modal=True
        )
        self.label = QLabel("正在安装 UWF 服务，请稍候...", self)

        # 禁止窗口最大化、最小化和调整大小、关闭
        self.setWindowFlags(self.windowFlags() & ~(
            Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint
        ))

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

    def update_progress(self, value):
        self.progress_bar.setValue(value)


class RebootDialog(BaseDialog):
    """对话框，用于提示用户重启系统"""
    def __init__(
        self,
        title: str = "提示",
        size: tuple[int, int] = (300, 100),
        description: Optional[str] = None,
    ):
        super().__init__(
            title=title,
            size=size,
            modal=True
        )

        # 禁止窗口最大化、最小化和调整大小、关闭
        self.setWindowFlags(self.windowFlags() & ~(
            Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowContextHelpButtonHint
        ))

        # 重启按钮
        self.restart_button = QPushButton("重启", self)
        self.restart_button.clicked.connect(self.accept)
        self.restart_button.setStyleSheet('padding: 6px 15px; font-size: 14px;')
        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet('padding: 6px 15px; font-size: 14px;')
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.restart_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout = QVBoxLayout(self)
        if description:
            self.label = QLabel(description, self)
            layout.addWidget(self.label)
        layout.addLayout(button_layout)

    def accept(self):
        """执行重启操作"""
        self.restart_button.setText(f'系统即将重启...')
        self.restart_button.setEnabled(False)
        subprocess.run(["shutdown", "/r", "/t", "0"], check=True)


class WaitDialog(BaseDialog):
    """对话框，用于显示等待状态"""
    def __init__(
        self,
        title: str = "正在处理",
        size: tuple[int, int] = (300, 100),
        description: Optional[str] = None,
    ):
        super().__init__(
            title=title,
            size=size,
            modal=True
        )

        # 禁止窗口最大化、最小化和调整大小、关闭
        self.setWindowFlags(self.windowFlags() & ~(
            Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint
        ))

        layout = QVBoxLayout(self)

        if description:
            self.label = QLabel(description, self)
            layout.addWidget(self.label)
