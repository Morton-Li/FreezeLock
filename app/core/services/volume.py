from typing import Optional

import pywintypes

from .base import BaseUWFService
from .utils import format_com_error, get_volume_instance
from ..object import WMIObject


class UWFVolume(BaseUWFService):
    """
    UWF Volume Class.

    https://learn.microsoft.com/en-us/windows/configuration/unified-write-filter/uwf-volume
    """

    @staticmethod
    def add_exclusion(drive: str, file_name: str) -> bool:
        """
        添加排除项
        :param drive: 盘符字符串，例如 "C:"
        :param file_name: 要排除的文件或注册表路径
        :return: 操作是否成功
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("AddExclusion", FileName=file_name)
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Adding exclusion failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def commit_file(drive: str, file_name: str) -> bool:
        """
        提交文件更改
        :param drive: 盘符字符串，例如 "C:"
        :param file_name: 要提交的文件路径
        :return: 操作是否成功
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("CommitFile", FileName=file_name)
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Committing file failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def commit_file_deletion(drive: str, file_name: str) -> bool:
        """
        提交文件删除
        :param drive: 盘符字符串，例如 "C:"
        :param file_name: 要删除的文件路径
        :return: 操作是否成功
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("CommitFileDeletion", FileName=file_name)
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Committing file deletion failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def find_exclusion(drive: str, file_name: str) -> tuple[bool, Optional[bool]]:
        """
        查找排除项
        :param drive: 盘符字符串，例如 "C:"
        :param file_name: 要查找的文件或注册表路径
        :return: 如果找到排除项则返回 True，否则返回 False
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("FindExclusion", FileName=file_name, bFound=False)
                # result.bFound is a boolean indicating if the exclusion was found
                # result.ReturnValue is an integer indicating the success of the operation
                if result.ReturnValue == 0:
                    return True, result.bFound
        except pywintypes.com_error as e:
            print(f'[!] Finding exclusion failed: {format_com_error(e=e)}')
        return False, None

    @staticmethod
    def get_exclusions(drive: str) -> tuple[bool, list[WMIObject]]:
        """
        获取排除项列表
        :param drive: 盘符字符串，例如 "C:"
        :return: 排除项列表
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("GetExclusions")
                if result.ReturnValue == 0: return True, (([WMIObject(file) for file in result.ExcludedFiles]) if result.ExcludedFiles else [])
        except pywintypes.com_error as e:
            print(f'[!] Getting exclusions failed: {format_com_error(e=e)}')
        return False, []

    @staticmethod
    def protect(drive: str) -> bool:
        """
        保护卷
        :param drive: 盘符字符串，例如 "C:"
        :return: 操作是否成功
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("Protect")
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Protecting volume failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def remove_all_exclusions(drive: str) -> bool:
        """
        移除所有排除项
        :param drive: 盘符字符串，例如 "C:"
        :return: 操作是否成功
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("RemoveAllExclusions")
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Removing all exclusions failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def remove_exclusion(drive: str, file_name: str) -> bool:
        """
        移除排除项
        :param drive: 盘符字符串，例如 "C:"
        :param file_name: 要移除的文件或注册表路径
        :return: 操作是否成功
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("RemoveExclusion", FileName=file_name)
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Removing exclusion failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def set_bind_by_drive_letter(drive: str, bind: bool) -> bool:
        """
        设置BindByDriveLetter属性，该属性指示统一写入筛选器 (UWF) 卷是否通过驱动器号或卷名绑定到物理卷。
        :param drive: 盘符字符串，例如 "C:"
        :param bind: 如果为 True，则表示通过驱动器号绑定（松散绑定）；如果为 False，则表示通过卷名绑定（紧密绑定）。
        :return: 操作是否成功
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("SetBindByDriveLetter", bBindByDriveLetter=bind)
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Setting BindByDriveLetter failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def unprotect(drive: str) -> bool:
        """
        取消保护卷
        :param drive: 盘符字符串，例如 "C:"
        :return: 操作是否成功
        """
        try:
            volume = get_volume_instance(drive=drive, current_session=False)
            if volume:
                result = volume.execute_method("Unprotect")
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Unprotecting volume failed: {format_com_error(e=e)}')
        return False
