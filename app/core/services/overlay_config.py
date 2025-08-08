import pywintypes

from .base import BaseUWFService
from .utils import get_service_instance, format_com_error


class UWFOverlayConfig(BaseUWFService):
    """
    UWF OverlayConfig Class.

    https://learn.microsoft.com/en-us/windows/configuration/unified-write-filter/uwf-overlayconfig
    """

    @staticmethod
    def set_type(type_str: str) -> bool:
        """
        Set the overlay type.
        :param type_str: The type of overlay to set (e.g., "RAM", "Disk").
        :return: True if the operation was successful, False otherwise.
        """
        type_map = {
            "RAM": 0,
            "Disk": 1,
        }
        try:
            instance = get_service_instance(instance_name='UWF_OverlayConfig')[0]
            result = instance.execute_method("SetType", type=type_map[type_str])
            return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Setting UWF overlay type failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def set_maximum_size(size: int) -> bool:
        """
        Set the maximum size of the overlay.
        :param size: The maximum size in bytes.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            instance = get_service_instance(instance_name='UWF_OverlayConfig')[0]
            result = instance.execute_method("SetMaximumSize", size)
            return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Setting UWF overlay maximum size failed: {format_com_error(e=e)}')
        return False


def current_session() -> bool:
    """
    Check if the current session is using UWF.
    :return: True if UWF is enabled in the current session, False otherwise.
    """
    try:
        instance = get_service_instance(instance_name='UWF_OverlayConfig')[0]
        return instance['CurrentSession']
    except pywintypes.com_error as e:
        print(f'[!] Checking UWF current session failed: {format_com_error(e=e)}')
        return False


def get_type() -> str:
    """
    Get the current overlay type.
    :return: The type of overlay (e.g., "RAM", "Disk").
    """
    type_map = {
        0: "RAM",
        1: "Disk",
    }
    try:
        instance = get_service_instance(instance_name='UWF_OverlayConfig')[0]
        type_value = instance['Type']
        return type_map.get(type_value, "Unknown")
    except pywintypes.com_error as e:
        print(f'[!] Getting UWF overlay type failed: {format_com_error(e=e)}')
        return "Error"


def maximum_size() -> int:
    """
    Get the maximum size of the overlay.
    :return: The maximum size in bytes.
    """
    try:
        instance = get_service_instance(instance_name='UWF_OverlayConfig')[0]
        return instance['MaximumSize']
    except pywintypes.com_error as e:
        print(f'[!] Getting UWF overlay maximum size failed: {format_com_error(e=e)}')
        return 0
