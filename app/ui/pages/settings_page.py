from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QGroupBox, QHBoxLayout, QComboBox, QLabel, QSpinBox, QPushButton
)

from ..base import BasePage
from ...core.services.filter import current_enabled
from ...core.services.overlay_config import get_type, maximum_size, UWFOverlayConfig


class SettingsPage(BasePage):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent=parent)

        self.services['uwf_overlay_config'] = UWFOverlayConfig()

        # 禁用提示
        self.disabled_remark = QLabel()
        self.disabled_remark.setStyleSheet('color: red; font-weight: bold;')

        # 运行配置
        run_group = QGroupBox('运行配置')
        run_layout = QVBoxLayout()
        run_layout.setSpacing(24)
        run_group.setLayout(run_layout)

        # 运行模式选择
        mode_row = QVBoxLayout()
        mode_row.setSpacing(6)
        mode_select_row = QHBoxLayout()
        mode_label = QLabel("运行模式：")
        mode_select_row.addWidget(mode_label)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["RAM", "Disk"])
        mode_select_row.addWidget(self.mode_combo)
        mode_select_row.addStretch()  # 添加弹性空间，使内容靠左排列
        mode_row.addLayout(mode_select_row)
        mode_select_remark = QLabel("选择运行模式，RAM 模式使用内存缓存，Disk 模式使用磁盘缓存。")
        mode_row.addWidget(mode_select_remark)
        run_layout.addLayout(mode_row)

        # 最大缓存
        max_cache_row = QVBoxLayout()
        max_cache_row.setSpacing(6)
        max_cache_input_row = QHBoxLayout()
        max_cache_label = QLabel("最大缓存（MB）：")
        max_cache_input_row.addWidget(max_cache_label)
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(1024, 32768)  # 设置范围为 1GB 到 32GB
        self.max_size_spin.setSingleStep(128)
        self.max_size_spin.setSuffix(' MB')
        self.max_size_spin.setValue(1024)
        max_cache_input_row.addWidget(self.max_size_spin)
        max_cache_input_row.addStretch()  # 添加弹性空间，使内容靠左排列
        max_cache_row.addLayout(max_cache_input_row)
        max_cache_remark_i = QLabel('设置最大缓存大小。当覆盖的大小达到缓存值上限时会对任何写入受保护卷的尝试返回错误。')
        max_cache_remark_ii = QLabel('注意：系统卷必须具有大于缓存大小的可用空间。')
        max_cache_row.addWidget(max_cache_remark_i)
        max_cache_row.addWidget(max_cache_remark_ii)
        run_layout.addLayout(max_cache_row)

        # 应用更改按钮
        button_row = QHBoxLayout()
        button_row.addStretch()
        self.apply_button = QPushButton('应用更改')
        self.apply_button.setStyleSheet("padding: 6px 15px;")
        button_row.addWidget(self.apply_button)
        self.reset_button = QPushButton('重置')
        self.reset_button.setStyleSheet("padding: 6px 15px;")
        button_row.addWidget(self.reset_button)

        # 布局构建
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 添加禁用提示
        layout.addWidget(self.disabled_remark)

        # 添加运行配置
        layout.addWidget(run_group)

        layout.addStretch()  # 添加弹性空间

        # 添加按钮行
        layout.addLayout(button_row)

        # 信号绑定
        self.apply_button.clicked.connect(self._apply_settings)
        self.reset_button.clicked.connect(self.refresh)

    def _apply_settings(self):
        """应用设置"""
        print(f"[+] 应用设置")

        mode = self.mode_combo.currentText()
        if mode != get_type():
            if not self.services['uwf_overlay_config'].set_type(mode):
                print(f"[!] 设置运行模式失败: {mode}")

        max_cache = self.max_size_spin.value()
        if max_cache != maximum_size():
            if not self.services['uwf_overlay_config'].set_maximum_size(max_cache):
                print(f"[!] 设置最大缓存失败: {max_cache}MB")

    def refresh(self):
        """刷新页面内容"""
        if current_enabled():
            self.disabled_remark.setText("当前 UWF 服务已启用，请停用后再进行设置。")
            self.disabled_remark.show()

            self.apply_button.setEnabled(False)
            self.reset_button.setEnabled(False)
        else:
            self.disabled_remark.hide()

            self.apply_button.setEnabled(True)
            self.reset_button.setEnabled(True)

        self.mode_combo.setCurrentText(get_type())
        self.max_size_spin.setValue(maximum_size())
