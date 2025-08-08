import pywintypes

from .base import BaseUWFService
from .utils import format_com_error, get_filter_instance


class UWFFilter(BaseUWFService):
    """
    UWF Filter Class.

    https://learn.microsoft.com/en-us/windows/configuration/unified-write-filter/uwf-filter
    """

    @staticmethod
    def enable() -> bool:
        """
        Enable the UWF filter.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            # Get the UWF service class instance
            instance = get_filter_instance()
            if 'NextEnabled' in instance and instance['NextEnabled']:
                # UWF will be enabled on the next boot
                return True
            elif 'CurrentEnabled' in instance:
                # UWF is currently disabled, enable it now
                result = instance.execute_method(method_name="Enable")
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Enabling UWF filter failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def disable() -> bool:
        """
        Disable the UWF filter.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            instance = get_filter_instance()
            if 'NextEnabled' in instance and not instance['NextEnabled']:
                # UWF will be disabled on the next boot
                return True
            elif 'CurrentEnabled' in instance:
                # UWF is currently enabled, disable it now
                result = instance.execute_method("Disable")
                return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Disabling UWF filter failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def reset_settings() -> bool:
        """
        Reset the UWF filter settings.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            instance = get_filter_instance()
            result = instance.execute_method("ResetSettings")
            return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Resetting UWF filter settings failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def shutdown_system() -> bool:
        """
        Shutdown the system.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            instance = get_filter_instance()
            result = instance.execute_method("ShutdownSystem")
            return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Shutting down system failed: {format_com_error(e=e)}')
        return False

    @staticmethod
    def restart_system() -> bool:
        """
        Restart the system.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            instance = get_filter_instance()
            result = instance.execute_method("RestartSystem")
            return result.ReturnValue == 0
        except pywintypes.com_error as e:
            print(f'[!] Restarting system failed: {format_com_error(e=e)}')
        return False


def current_enabled() -> bool:
    """
    Check if the UWF filter is currently enabled.
    :return: True if the UWF filter is currently enabled, False otherwise.
    """
    try:
        instance = get_filter_instance()
        return instance['CurrentEnabled']
    except pywintypes.com_error as e:
        print(f'[!] Checking current UWF filter status failed: {format_com_error(e=e)}')
    return False


def next_enabled() -> bool:
    """
    Check if the UWF filter will be enabled on the next boot.
    :return: True if the UWF filter will be enabled on the next boot, False otherwise.
    """
    try:
        instance = get_filter_instance()
        return instance['NextEnabled']
    except pywintypes.com_error as e:
        print(f'[!] Checking next UWF filter status failed: {format_com_error(e=e)}')
    return False
