from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from ...version import __version__  # Assuming __version__ is defined in the app/version.py


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # 软件名称
        title = QLabel('FreezeLock')
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        title.setStyleSheet('color: #2563eb;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 版本信息
        version_label = QLabel('Ver ')
        version_label.setFont(QFont('Segoe UI', 11))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_value = QLabel(__version__)
        version_value.setStyleSheet('color: #555;')
        version_value.setFont(QFont('Segoe UI', 11))
        version_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_layout = QHBoxLayout()
        version_layout.addWidget(version_label)
        version_layout.addWidget(version_value)
        version_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_layout.setSpacing(2)
        layout.addLayout(version_layout)

        # 描述
        description = QLabel('一个基于 PySide6 构建的现代化 UWF 可视化控制工具。')
        description.setFont(QFont('Segoe UI', 10))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet('color: #555; padding: 60 0px;')
        layout.addWidget(description)

        layout.addStretch()

        # 作者信息
        author_label = QLabel('作者: ')
        author_label.setFont(QFont('Segoe UI', 10))
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_value = QLabel('Morton Li')
        author_value.setFont(QFont('Segoe UI', 10))
        author_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_value.setStyleSheet('color: #2563eb;')
        author_layout = QHBoxLayout()
        author_layout.addWidget(author_label)
        author_layout.addWidget(author_value)
        author_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_layout.setSpacing(2)
        layout.addLayout(author_layout)
