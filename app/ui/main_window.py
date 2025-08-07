from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
    QStatusBar
)
from win32com import client

from .pages import AboutPage, FreezePage, StatusPage
from ..core.services import get_wmi_client, is_uwf_installed
from ..core.services.utils import get_service_instance


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FreezeLock')
        self.setFixedSize(960, 520)

        self.main_widget: QWidget  # 主容器
        self.main_layout: QHBoxLayout  # 主布局
        self.pages: list[tuple[str, callable]]  # 页面列表，包含页面名称和图标路径
        self.sidebar: QListWidget  # 左侧导航栏
        self.stack: QStackedWidget  # 右侧页面堆叠

        self.wmi_client: client.CDispatch  # WMI 客户端对象

        self._init_features()
        self._init_ui()

    def _init_ui(self):
        """
        Initialize the UI components.
        :return:
        """
        # 主容器（中央控件）
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # 初始化页面列表
        self.pages = [
            ("状态", StatusPage(parent=self)),
            ("冻结", FreezePage(parent=self)),
            ("关于", AboutPage()),
        ]

        # 初始化左侧导航栏
        self._init_sidebar()
        # 初始化右侧堆叠页面
        self._init_stacked_pages()
        # 初始化状态栏
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
        self.main_layout.addWidget(self.sidebar)

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
        self.main_layout.addWidget(self.stack)

    def _init_status_bar(self):
        """
        Initialize the status bar.
        :return:
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.refresh_status_bar()

    def _init_features(self):
        """
        Initialize features of the application.
        :return:
        """
        self.wmi_client = get_wmi_client()  # WMI 客户端对象

    def refresh_status_bar(self):
        """ Refresh the status bar with UWF status. """
        status_text = 'UWF 状态: '
        if not is_uwf_installed():
            status_text += '服务不可用'
        else:
            uwf_filter_instance = get_service_instance(instance_name='UWF_Filter')[0].as_dict()
            if uwf_filter_instance:
                if uwf_filter_instance['CurrentEnabled']:
                    status_text += '已启用'
                    if not uwf_filter_instance['NextEnabled']:
                        status_text += ' (重新启动后将禁用)'
                else:
                    status_text += '已禁用'
                    if uwf_filter_instance['NextEnabled']:
                        status_text += ' (重新启动后将启用)'
            else:
                status_text += '状态获取失败'
        self.status_bar.showMessage(status_text)

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
