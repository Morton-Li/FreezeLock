import os
from getpass import getuser

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QListWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView,
)

from ..base import BasePage
from ..widgets.dialog import WaitDialog
from ...core.services import is_uwf_installed
from ...core.services.filter import UWFFilter as UWF_Filter
from ...core.services.utils import get_service_instance, get_service_class, get_system_volume
from ...core.services.volume import UWFVolume as UWF_Volume


class FreezePage(BasePage):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent=parent)

        self.services['uwf_filter'] = UWF_Filter()
        self.services['uwf_volume'] = UWF_Volume()

        # 状态显示
        status_section_layout = QHBoxLayout()
        status_section_layout.addWidget(QLabel("当前状态："))
        self.status_value = QLabel("未知")
        status_section_layout.addWidget(self.status_value)
        status_section_layout.addStretch()
        # 启用/禁用按钮
        self.enable_button = QPushButton("启用 UWF")
        self.enable_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 6px; padding-bottom: 6px;')
        status_section_layout.addWidget(self.enable_button)
        self.disable_button = QPushButton("禁用 UWF")
        self.disable_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 6px; padding-bottom: 6px;')
        status_section_layout.addWidget(self.disable_button)

        # 卷列表
        volume_group = QGroupBox("卷列表")
        volume_layout = QVBoxLayout(volume_group)
        self.volume_table = QTableWidget()
        self.volume_table.setColumnCount(3)  # 三列：选择、盘符、状态
        self.volume_table.setHorizontalHeaderLabels(['选择', '盘符', '状态'])
        volume_table_header = self.volume_table.horizontalHeader()
        self.volume_table.setColumnWidth(0, 40)  # 设置选择列宽度
        volume_table_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 设置选择列宽度为固定
        volume_table_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        volume_table_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 设置状态列宽度为自适应
        self.volume_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.volume_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.volume_table.setAlternatingRowColors(True)
        self.volume_table.setFixedHeight(120)
        volume_layout.addWidget(self.volume_table)
        self._volumes_info: dict[str, dict[str, dict]] = {}
        # 卷管理区
        volume_button_row = QHBoxLayout()
        volume_button_row.addStretch()
        self.volume_protect_button = QPushButton("保护选中卷")
        self.volume_protect_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 6px; padding-bottom: 6px;')
        volume_button_row.addWidget(self.volume_protect_button)
        self.volume_unprotect_button = QPushButton("撤销选中卷保护")
        self.volume_unprotect_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 6px; padding-bottom: 6px;')
        volume_button_row.addWidget(self.volume_unprotect_button)
        volume_layout.addLayout(volume_button_row)

        # 排除路径
        exclusions_group = QGroupBox("排除路径")
        exclusions_layout = QVBoxLayout(exclusions_group)
        self.exclusions_list = QListWidget()
        self.exclusions_list.setFixedHeight(100)
        self.exclusions_list.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px;
            }
            QListWidget::item:selected {
                background-color: #d0eaff;
                font-weight: bold;
            }
            QListWidget::item:hover {
                background-color: #f0f8ff;
            }
        """)
        exclusions_layout.addWidget(self.exclusions_list)
        # 排除功能行
        exclusion_feature_row = QHBoxLayout()
        exclusion_feature_row.addStretch()
        self.select_file_button = QPushButton('选择文件')
        self.select_file_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 6px; padding-bottom: 6px;')
        exclusion_feature_row.addWidget(self.select_file_button)
        self.select_dir_button = QPushButton('选择目录')
        self.select_dir_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 6px; padding-bottom: 6px;')
        exclusion_feature_row.addWidget(self.select_dir_button)
        self.remove_exclude_button = QPushButton("删除选中项")
        self.remove_exclude_button.setStyleSheet('padding-left: 15px; padding-right: 15px; padding-top: 6px; padding-bottom: 6px;')
        exclusion_feature_row.addWidget(self.remove_exclude_button)
        exclusions_layout.addLayout(exclusion_feature_row)

        # 布局构建
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 状态栏区
        layout.addLayout(status_section_layout)

        # 卷管理区
        layout.addWidget(volume_group)

        # 排除路径区
        layout.addWidget(exclusions_group)

        # 添加空白间隔
        layout.addStretch()

        # 信号绑定
        self.enable_button.clicked.connect(self._enable_uwf)
        self.disable_button.clicked.connect(self._disable_uwf)
        self.volume_protect_button.clicked.connect(self._protect_volumes)
        self.volume_unprotect_button.clicked.connect(self._unprotect_volumes)
        self.select_file_button.clicked.connect(self._add_exclusion_file)
        self.select_dir_button.clicked.connect(self._add_exclusion_dir)
        self.remove_exclude_button.clicked.connect(self._remove_exclusion)

    def _enable_uwf(self):
        """
        启用 UWF 服务。
        """
        print(f'[+] 启用 UWF 服务...')
        wait_dialog = WaitDialog(
            title="启用 UWF 服务",
            description="正在启用 UWF 服务，请稍候..."
        )
        wait_dialog.show()
        msg_box = QMessageBox()
        msg_box.setMinimumWidth(150)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        if self.services['uwf_filter'].enable():
            self.refresh()
            self.parent.refresh_status_bar()
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("提示")
            msg_box.setText("UWF 服务已启用")
            msg_box.setInformativeText("请重启系统以使更改生效。")
        else:
            self.status_value.setText("启用 UWF 服务失败")
            self.status_value.setStyleSheet("color: red;")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText("启用 UWF 服务失败")
            msg_box.setInformativeText("请检查系统日志以获取更多信息。")
        wait_dialog.close()

        msg_box.exec()

    def _disable_uwf(self):
        """
        禁用 UWF 服务。
        """
        print(f'[+] 禁用 UWF 服务...')
        wait_dialog = WaitDialog(
            title="禁用 UWF 服务",
            description="正在禁用 UWF 服务，请稍候..."
        )
        wait_dialog.show()
        msg_box = QMessageBox()
        msg_box.setMinimumWidth(150)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        if self.services['uwf_filter'].disable():
            self.refresh()
            self.parent.refresh_status_bar()
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("提示")
            msg_box.setText("UWF 服务已禁用")
            msg_box.setInformativeText("请重启系统以使更改生效。")
        else:
            self.status_value.setText("禁用 UWF 服务失败")
            self.status_value.setStyleSheet("color: red;")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText("禁用 UWF 服务失败")
            msg_box.setInformativeText("请检查系统日志以获取更多信息。")
        wait_dialog.close()

        msg_box.exec()

    def get_checked_volumes(self) -> list[str]:
        """
        获取已选中的卷列表。
        :return:
        """
        checked = []
        for row in range(self.volume_table.rowCount()):
            item = self.volume_table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                volume_info = item.data(Qt.ItemDataRole.UserRole)
                current_session = volume_info.get('CurrentSession', {})
                next_session = volume_info.get('NextSession', {})
                driver_letter = current_session['DriveLetter']
                if driver_letter: checked.append(driver_letter)
        return checked

    def _protect_volumes(self):
        """
        保护选中的卷。
        这将使选中的卷受 UWF 保护。
        :return:
        """
        wait_dialog = WaitDialog(
            title="保护卷",
            description="正在保护选中的卷，请稍候..."
        )
        wait_dialog.show()
        msg_box = QMessageBox()
        msg_box.setMinimumWidth(150)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        result = []
        for drive in self.get_checked_volumes():
            result.append(self.services['uwf_volume'].protect(drive=drive))
        self.refresh()
        if any(result):
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("提示")
            msg_box.setText("选中的卷已成功保护")
            msg_box.setInformativeText("请重启系统以使更改生效。")
        else:
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText("保护卷失败")
            msg_box.setInformativeText("请检查系统日志以获取更多信息。")
        wait_dialog.close()

        msg_box.exec()

    def _unprotect_volumes(self):
        """
        撤销选中的卷保护。
        这将使选中的卷不再受 UWF 保护。
        :return:
        """
        wait_dialog = WaitDialog(
            title="撤销卷保护",
            description="正在撤销选中的卷保护，请稍候..."
        )
        msg_box = QMessageBox()
        msg_box.setMinimumWidth(150)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        result = []
        for drive in self.get_checked_volumes():
            result.append(self.services['uwf_volume'].unprotect(drive=drive))
        self.refresh()
        if any(result):
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("提示")
            msg_box.setText("选中的卷保护已成功撤销")
            msg_box.setInformativeText("请重启系统以使更改生效。")
        else:
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText("撤销卷保护失败")
            msg_box.setInformativeText("请检查系统日志以获取更多信息。")
        wait_dialog.close()

        msg_box.exec()

    def _add_exclusion(self, path: str):
        """
        添加排除项
        :return:
        """
        msg_box = QMessageBox()
        msg_box.setMinimumWidth(150)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)

        driver_letter, absolute_path = os.path.splitdrive(path)
        normpath_absolute_path = os.path.normpath(absolute_path)
        if normpath_absolute_path == '\\':
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("警告")
            msg_box.setText("无法添加卷根目录作为排除项")
            msg_box.exec()
            return

        # 排除项禁用列表
        system_volume = get_system_volume()
        disabled_exclusions = [
            r'\Windows',
            r'\EFI\Microsoft\Boot\BOOTSTAT.DAT',
            r'\Boot\BOOTSTAT.DAT',
            fr'\Users\{getuser()}\NTUSER.DAT',
        ]
        if driver_letter == system_volume and (
            normpath_absolute_path in disabled_exclusions or any(
                normpath_absolute_path.startswith(disabled_exclusion_item) for disabled_exclusion_item in disabled_exclusions
            )
        ):
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("警告")
            msg_box.setText("无法添加特殊路径作为排除项")
            msg_box.exec()
            return
        print(f'[+] 添加排除项: {path}')
        if self.services['uwf_volume'].add_exclusion(
            drive=driver_letter, file_name=normpath_absolute_path
        ):
            self.refresh()
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("提示")
            msg_box.setText("排除项已成功添加")
            msg_box.setInformativeText("请重启系统以使更改生效。")
        else:
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText("添加排除项失败")
            msg_box.setInformativeText("请检查系统日志以获取更多信息。")
        msg_box.exec()
        self.refresh()

    def _add_exclusion_file(self):
        """
        添加排除项（文件）。
        :return:
        """
        path, _ = QFileDialog.getOpenFileName(self, "选择排除的文件")
        if not path: return  # 如果没有选择文件，则返回
        self._add_exclusion(path=path)

    def _add_exclusion_dir(self):
        """
        添加排除项（目录）。
        :return:
        """
        path = QFileDialog.getExistingDirectory(self, "选择排除的目录")
        if not path: return  # 如果没有选择目录，则返回
        self._add_exclusion(path=path)

    def _remove_exclusion(self):
        """
        删除选中的排除项。
        :return:
        """
        selected_items = self.exclusions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要删除的排除项。")
            return

        msg_box = QMessageBox()
        msg_box.setMinimumWidth(150)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("确认删除")
        msg_box.setText("确定要删除选中的排除项吗？")

        if msg_box.exec() == QMessageBox.StandardButton.Ok:
            result = []
            result_msg_box = QMessageBox()
            result_msg_box.setMinimumWidth(150)
            result_msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            result_msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            for item in selected_items:
                path = item.text()
                drive_letter, absolute_path = os.path.splitdrive(path)
                result.append(self.services['uwf_volume'].remove_exclusion(
                    drive=drive_letter, file_name=os.path.normpath(absolute_path)
                ))
            self.refresh()
            if any(result):
                result_msg_box.setIcon(QMessageBox.Icon.Information)
                result_msg_box.setWindowTitle("提示")
                result_msg_box.setText("选中的排除项已成功删除")
                result_msg_box.setInformativeText("请重启系统以使更改生效。")
            else:
                result_msg_box.setIcon(QMessageBox.Icon.Critical)
                result_msg_box.setWindowTitle("错误")
                result_msg_box.setText("删除排除项失败")
                result_msg_box.setInformativeText("请检查系统日志以获取更多信息。")
            result_msg_box.exec()

    @staticmethod
    def _get_volumes_info() -> dict[str, dict[str, dict]]:
        """
        获取所有卷的信息
        :return: 包含卷信息的字典列表
        """
        volumes_info = {}

        for volume in get_service_instance(instance_name='UWF_Volume'):
            if not volume.DriveLetter: continue

            # 将卷信息存储到字典中
            drive_letter = volume.DriveLetter[:-1]  # 去掉末尾的冒号
            if drive_letter not in volumes_info:
                volumes_info[drive_letter] = {
                    'CurrentSession': {},
                    'NextSession': {},
                }

            volumes_info[drive_letter]['CurrentSession' if volume.CurrentSession else 'NextSession'] = {
                'DriveLetter': volume.DriveLetter,
                'VolumeName': volume.VolumeName,
                'Protected': volume.Protected,
                'CommitPending': volume.CommitPending,
                'CurrentSession': volume.CurrentSession,
                'BindByDriveLetter': volume.BindByDriveLetter,
            }

        for drive_letter, volume_info in volumes_info.items():
            # 检查 NextSession 是否为空
            if not volume_info['NextSession']:
                # 如果 NextSession 为空
                cls = get_service_class(class_name="UWF_Volume")
                inst = cls.SpawnInstance_()
                for prop in inst.Properties_:
                    # 复制 CurrentSession 的值到 NextSession
                    inst.Properties_.Item(prop.Name).Value = volume_info['CurrentSession'][prop.Name]
                if volume_info['CurrentSession']['Protected'] is None:
                    inst.Properties_.Item('Protected').Value = False
                inst.Properties_.Item('CurrentSession').Value = False  # 设置 CurrentSession 为 False

                # Put_ 的 0x2 = wbemChangeFlagCreateOnly
                inst_path = inst.Put_(0x2)

        # 排序卷列表
        volumes_info = dict(sorted(volumes_info.items()))

        return volumes_info

    def _refresh_status(self):
        """
        刷新UWF状态信息。
        """
        uwf_filter_instance = get_service_instance(instance_name='UWF_Filter')[0].as_dict()
        if uwf_filter_instance['CurrentEnabled']:
            service_status_message = '已启用'
            self.status_value.setStyleSheet("color: green;")
            self.enable_button.hide()
            self.disable_button.show()
            if not uwf_filter_instance['NextEnabled']:
                service_status_message += ' (重新启动后将禁用)'
                self.status_value.setStyleSheet("color: orange;")
                self.enable_button.show()
                self.disable_button.hide()
        else:
            service_status_message = '已禁用'
            self.status_value.setStyleSheet("color: red;")
            self.enable_button.show()
            self.disable_button.hide()
            if uwf_filter_instance['NextEnabled']:
                service_status_message += ' (重新启动后将启用)'
                self.status_value.setStyleSheet("color: orange;")
                self.enable_button.hide()
                self.disable_button.show()
        self.status_value.setText(service_status_message)

    def _refresh_volumes(self):
        """
        刷新卷列表。
        """
        self.volume_table.setRowCount(0)  # 清空表格行
        self._volumes_info = self._get_volumes_info()

        # 填充表格
        for row, (drive_letter, volume_info) in enumerate(self._volumes_info.items()):
            # 添加行
            self.volume_table.insertRow(row)

            current_session = volume_info.get('CurrentSession', {})
            next_session = volume_info.get('NextSession', {})

            # 选择列
            select_item = QTableWidgetItem()
            select_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            select_item.setCheckState(Qt.CheckState.Unchecked)
            select_item.setData(Qt.ItemDataRole.UserRole, volume_info)  # 存储盘信息
            self.volume_table.setItem(row, 0, select_item)

            # 盘符列
            drive_letter_item = QTableWidgetItem(drive_letter)
            drive_letter_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            drive_letter_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # 禁止编辑
            self.volume_table.setItem(row, 1, drive_letter_item)

            # 状态列
            status_item = QTableWidgetItem("受保护" if current_session['Protected'] else "未保护")
            if next_session and current_session['Protected'] != next_session['Protected']:
                # 初始化时当前会话保护状态为 None，但下一会话状态为 False
                if current_session['Protected'] is None and next_session['Protected'] is False:
                    # 初始化状态，跳过
                    pass
                else:
                    status_item.setText(
                        f"{status_item.text()} (重启后: {'受保护' if next_session['Protected'] else '取消保护'})")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # 禁止编辑
            status_item.setForeground(
                Qt.GlobalColor.darkGreen if current_session['Protected'] else Qt.GlobalColor.red)  # 设置状态颜色
            if next_session and current_session['Protected'] != next_session['Protected']:
                if current_session['Protected'] is None and next_session['Protected'] is False:
                    pass
                else:
                    status_item.setForeground(Qt.GlobalColor.darkYellow)
            self.volume_table.setItem(row, 2, status_item)

    def _refresh_exclusions(self):
        """
        刷新排除路径列表。
        """
        # 更新排除路径列表
        self.exclusions_list.clear()
        # 获取排除项列表
        for drive in self._volumes_info.values():
            drive_letter = drive['CurrentSession']['DriveLetter']
            success, results = self.services['uwf_volume'].get_exclusions(drive=drive_letter)
            if not success: continue
            for path in results:
                # path 是 WMIObject 实例，只有一个属性 FileName
                self.exclusions_list.addItem(f'{drive_letter}{path.FileName}')

    def refresh(self):
        """
        刷新页面内容，重新加载UWF状态和卷列表。
        """
        if not is_uwf_installed():
            self.status_value.setText("未安装 UWF 服务")
            return

        # 更新状态信息
        self._refresh_status()

        # 更新卷列表
        self._refresh_volumes()

        # 更新排除路径列表
        self._refresh_exclusions()
