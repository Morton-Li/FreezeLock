import math
import time
from typing import Optional

from PySide6.QtCore import Qt, QEventLoop
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, QPushButton

from ..base import BasePage, BaseMainWindow
from ..widgets.dialog import InstallUWFServiceDialog, RebootDialog
from ...core.services import refresh_wmi_client, is_uwf_installed
from ...core.services.filter import current_enabled, next_enabled
from ...core.services.overlay_config import get_type
from ...core.services.utils import get_service_instance
from ...worker.uwf import InstallUWFServiceWorker


class StatusPage(BasePage):
    def __init__(self, parent: BaseMainWindow):
        super().__init__(parent=parent)

        self.install_service_worker: Optional[InstallUWFServiceWorker] = None

        # 标题
        self.title_label = QLabel("运行状态")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563eb;")

        self.status_value = QLabel("Unknown")
        self.status_value.setStyleSheet("font-size: 15px;")
        status_label = QLabel("当前状态：")
        status_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        status_layout.addWidget(QLabel("●"))
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_value)
        status_layout.addStretch()
        # 安装按钮
        self.install_button = QPushButton("安装 UWF 服务")
        self.install_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 6px; padding-bottom: 6px;')
        self.install_button.clicked.connect(self.install_service)
        self.install_button.hide()
        status_layout.addWidget(self.install_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.cache_mode_value = QLabel("Unknown")
        self.cache_mode_value.setStyleSheet("font-size: 15px;")
        cache_mode_label = QLabel('缓存模式：')
        cache_mode_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        cache_mode_layout = QHBoxLayout()
        cache_mode_layout.setSpacing(10)
        cache_mode_layout.addWidget(QLabel("●"))  # 圆点图标（可用自定义图标替换）
        cache_mode_layout.addWidget(cache_mode_label)
        cache_mode_layout.addWidget(self.cache_mode_value, stretch=1, alignment=Qt.AlignmentFlag.AlignLeft)
        cache_mode_layout.addStretch()

        usage_row = QVBoxLayout()
        usage_label = QLabel("缓存使用情况：")
        usage_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        usage_row.addWidget(usage_label)

        # 使用率进度条
        self.usage_bar = QProgressBar()
        self.usage_bar.setFormat("当前使用率：%p%")
        self.usage_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.usage_bar.setFixedHeight(20)
        self.usage_bar.setStyleSheet("""
            QProgressBar {
                font-size: 13px;
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                width: 10px;
            }
        """)
        usage_row.addWidget(self.usage_bar)

        # 主体布局
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.addWidget(self.title_label)
        layout.addLayout(status_layout)
        layout.addLayout(cache_mode_layout)
        layout.addStretch()
        layout.addLayout(usage_row)

    def install_service(self):
        """
        安装 UWF 服务
        """
        self.install_button.setText('安装中...')
        self.install_button.setEnabled(False)

        install_dialog = InstallUWFServiceDialog()
        install_dialog.show()

        self.install_service_worker = InstallUWFServiceWorker()
        loop = QEventLoop()

        def on_install_result(install_result):
            if install_result:
                install_dialog.update_progress(85)
                self.install_button.hide()
                time.sleep(3)  # 等待系统刷新
                refresh_wmi_client()
                install_dialog.update_progress(100)
            else:
                self.install_button.setText('安装失败')
                self.install_button.setStyleSheet("color: red; font-size: 15px; padding: 5px;")
                self.status_value.setText(f'安装 UWF 服务失败')
            self.install_service_worker.deleteLater()
            self.install_service_worker = None
            loop.quit()

        self.install_service_worker.install_result_signal.connect(on_install_result)
        self.install_service_worker.start()

        install_dialog.update_progress(25)
        loop.exec()

        install_dialog.close()

        reboot_dialog = RebootDialog(
            description='安装 UWF 服务后需要重启系统才能生效。请保存您的工作并重启系统。',
        )
        reboot_dialog.show()
        self.status_value.setText('等待重启...')

    def refresh(self):
        """
        刷新状态信息
        """
        if not is_uwf_installed():
            self.status_value.setText("未安装 UWF 服务")
            self.cache_mode_value.setText("N/A")
            self.usage_bar.setValue(0)
            self.install_button.show()
            return

        if current_enabled():
            if next_enabled():
                self.status_value.setText('Enabled')
                self.status_value.setStyleSheet('color: green; font-weight: bold; font-size: 15px;')
            else:
                self.status_value.setText('Enabled (will be disabled after reboot)')
                self.status_value.setStyleSheet('color: orange; font-weight: bold; font-size: 15px;')
        else:
            if next_enabled():
                self.status_value.setText('Disabled (will be enabled after reboot)')
                self.status_value.setStyleSheet('color: orange; font-weight: bold; font-size: 15px;')
            else:
                self.status_value.setText('Disabled')
                self.status_value.setStyleSheet('color: red; font-weight: bold; font-size: 15px;')

        # 更新缓存模式显示
        self.cache_mode_value.setText(get_type())

        # 获取缓存使用情况
        uwf_overly_instance = get_service_instance(instance_name='UWF_Overlay')[0].as_dict()
        if uwf_overly_instance:
            # {'AvailableSpace': 0, 'CriticalOverlayThreshold': 1024, 'Id': 'UWF_Overlay', 'OverlayConsumption': 0, 'WarningOverlayThreshold': 512}
            available_space = uwf_overly_instance.get('AvailableSpace', 0)
            critical_threshold = uwf_overly_instance.get('CriticalOverlayThreshold', 0)
            warning_threshold = uwf_overly_instance.get('WarningOverlayThreshold', 0)
            overlay_consumption = uwf_overly_instance.get('OverlayConsumption', 0)
            if critical_threshold > 0:
                usage_percentage = (overlay_consumption / critical_threshold) * 100
                self.usage_bar.setValue(math.floor(usage_percentage))
                self.usage_bar.setToolTip(
                    f"当前使用: {overlay_consumption} MB / 临界阈值: {critical_threshold} MB"
                )
        else:
            self.usage_bar.setValue(0)
            self.usage_bar.setToolTip("无法获取缓存使用情况")
