from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QLabel
)

from .base import BaseMainWindow
from .pages import AboutPage, FreezePage, StatusPage
from .pages.settings_page import SettingsPage
from ..core.services import is_uwf_installed
from ..core.services.filter import current_enabled, next_enabled


class MainWindow(BaseMainWindow):
    def __init__(self):
        super().__init__(
            title='FreezeLock',
            size=(960, 520)
        )
        self.sidebar: QListWidget  # 左侧导航栏
        self.stack: QStackedWidget  # 右侧页面堆叠

        self.pages: list[tuple[str, callable]]  # 页面列表，包含页面名称和图标路径

        self.uwf_status_value: QLabel

        self._init_ui()

    def _init_ui(self):
        """
        Initialize the UI components.
        :return:
        """
        # 内容
        self.content_layout = QHBoxLayout()
        self.content_wrapper.setLayout(self.content_layout)

        # 初始化页面列表
        self.pages = [
            ("状态", StatusPage(parent=self)),
            ("冻结", FreezePage(parent=self)),
            ("设置", SettingsPage(parent=self)),
            ("关于", AboutPage()),
        ]

        # 初始化左侧导航栏
        self._init_sidebar()
        # 初始化右侧堆叠页面
        self._init_stacked_pages()
        # Initialize status bar
        self._init_status_bar()

    def _init_sidebar(self):
        """
        Initialize the sidebar with navigation items.
        :return:
        """
        # 左侧：导航栏（列表）
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)  # 设置固定宽度
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #f4f6f8;
                border: none;
                padding: 8px;
            }
            QListWidget::item {
                background-color: transparent;
                height: 40px;
                border-radius: 8px;
                margin: 4px 2px;
            }
            QListWidget::item:hover {
                background-color: #d0d0d0;
            }
            QListWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        self.sidebar.setSpacing(8)  # 设置间距
        self.sidebar.setAlternatingRowColors(False)  # 关闭交替行颜色
        self.sidebar.setSelectionMode(QListWidget.SelectionMode.SingleSelection)  # 设置单选模式

        # 添加导航项
        font = QFont()
        font.setPointSize(14)  # 设置字号
        font.setBold(False)
        for item in self.pages:
            page_name, _ = item
            list_item = QListWidgetItem(page_name)
            # TODO: list_item.setIcon(QIcon("assets/icons/about.svg"))  # 设置图标路径
            list_item.setFont(font)
            list_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sidebar.addItem(list_item)

        # 设置默认选中第一个页面
        self.sidebar.setCurrentRow(0)

        # 向主布局添加侧边栏
        self.content_layout.addWidget(self.sidebar)

    def _init_stacked_pages(self):
        """
        Initialize the stacked widget for different pages.
        :return:
        """
        self.stack = QStackedWidget()
        for item in self.pages:
            _, page_widget = item
            self.stack.addWidget(page_widget)

        # 设置默认显示第一个页面
        self.stack.setCurrentIndex(0)
        # 初始化第一个页面
        first_page = self.stack.widget(0)
        if hasattr(first_page, "refresh"):
            first_page.refresh()

        # 连接侧边栏和堆叠页面
        self.sidebar.currentRowChanged.connect(self._on_page_changed)

        # 向主布局添加堆叠页面
        self.content_layout.addWidget(self.stack)

    def _init_status_bar(self):
        """
        Initialize the status bar.
        :return:
        """
        uwf_status_layout = QHBoxLayout()
        uwf_status_label = QLabel("UWF Status: ")
        self.uwf_status_value = QLabel('Unknown')
        uwf_status_layout.addWidget(uwf_status_label)
        uwf_status_layout.addWidget(self.uwf_status_value)
        uwf_status_layout.setSpacing(2)
        self.status_bar.add_layout(name='uwf_status', layout=uwf_status_layout, stretch=-1)

        self.refresh_status_bar_signal.emit()

    def refresh_status_bar(self):
        """ Refresh the status bar with UWF status. """
        if not is_uwf_installed():
            self.uwf_status_value.setText('Service Not Installed')
            self.uwf_status_value.setStyleSheet('color: red; font-weight: bold;')
        else:
            if current_enabled():
                if next_enabled():
                    self.uwf_status_value.setText('Enabled')
                    self.uwf_status_value.setStyleSheet('color: green; font-weight: bold;')
                else:
                    self.uwf_status_value.setText('Enabled (will be disabled after reboot)')
                    self.uwf_status_value.setStyleSheet('color: orange; font-weight: bold;')
            else:
                if next_enabled():
                    self.uwf_status_value.setText('Disabled (will be enabled after reboot)')
                    self.uwf_status_value.setStyleSheet('color: orange; font-weight: bold;')
                else:
                    self.uwf_status_value.setText('Disabled')
                    self.uwf_status_value.setStyleSheet('color: red; font-weight: bold;')

    def _on_page_changed(self, index: int):
        """
        Handle page change event when sidebar selection changes.
        :param index:
        :return:
        """
        self.stack.setCurrentIndex(index)
        page = self.stack.widget(index)
        if hasattr(page, "refresh"):
            page.refresh()
