from typing import Optional

import pywintypes

from . import uwf_classes, get_wmi_client
from ..errors.hresult import HRESULT
from ..object import WMIObject


def get_service_class(class_name: str) -> WMIObject:
    """
    获取指定 WMI 类的客户端对象
    :param class_name: WMI 类名
    :return: WMI 类的客户端对象
    """
    if class_name not in uwf_classes(): raise ValueError(f'[!] 无效的 WMI 类名: {class_name}')
    try:
        return WMIObject(get_wmi_client().Get(class_name))
    except Exception as e:
        raise RuntimeError(f'[!] 获取 WMI 类 {class_name} 失败: {e}') from e


def get_service_instance(instance_name: str) -> WMIObject:
    """
    获取指定 WMI 实例的客户端对象
    :param instance_name: WMI 实例名
    :return: WMI 实例的客户端对象
    """
    if instance_name not in uwf_classes(): raise ValueError(f'[!] 无效的 WMI 实例名: {instance_name}')
    try:
        return WMIObject(get_wmi_client().InstancesOf(instance_name))
    except Exception as e:
        raise RuntimeError(f'[!] 获取 WMI 实例 {instance_name} 失败: {e}') from e


def query_service_instance(class_name: str, query: str) -> WMIObject:
    """
    获取指定UWF类的服务实例
    :param class_name: UWF类名
    :param query: WMI查询语句
    :return: UWF类的服务实例
    """
    if class_name not in uwf_classes(): raise ValueError(f'[!] 类名 "{class_name}" 不在已安装的UWF类列表中。')
    try:
        return WMIObject(get_wmi_client().ExecQuery(query))
    except Exception as e:
        raise RuntimeError(f'[!] 执行 WMI 查询失败: {e}') from e


def install_uwf_service() -> bool:
    """
    安装 UWF 服务
    :return: True if the service was installed successfully, False otherwise.
    """
    import subprocess
    from win32com import client

    try:
        # 连接到 WMI 服务
        wmi = client.GetObject(r'winmgmts:\\.\root\cimv2')
        # 查询功能
        features = wmi.ExecQuery(r'SELECT * FROM Win32_OptionalFeature WHERE Name = "Client-UnifiedWriteFilter"')

        if not features: raise ValueError("未找到 UWF 功能")
        feature = features[0]
        if feature.InstallState == 1: return True  # UWF 已安装
        elif feature.InstallState == 2:
            try:
                # 使用 DISM 安装 Windows 可选功能
                result = subprocess.run(
                    args=f"DISM /Online /Enable-Feature /FeatureName:Client-UnifiedWriteFilter /All",
                    shell=True, capture_output=True, text=True
                )
                return result.returncode == 0
            except Exception as e:
                print(f"[!] 安装 UWF 功能失败: {e}")
                return False
        else:
            return False
    except Exception as e:
        print(f"[!] Failed to install UWF service: {e}")
        return False


def format_com_error(e: pywintypes.com_error) -> str:
    hresult, text, excepinfo, argerr = e.args
    # COM 错误码, 错误描述文本, 扩展异常信息, 发生错误的参数索引（从 0 开始），若无参数错误则为 None
    # excepinfo: wCode，辅助错误码, 错误源, 错误描述信息, helpFile, helpContext, SCODE（WMI 错误码）
    if hresult == -2147352567:  # 处理 HRESULT 0x80020009 (DISP_E_EXCEPTION)
        hresult = excepinfo[5]
    hresult = HRESULT.from_code(hresult)
    return f'{hresult.describe()} (HRESULT: {hresult.hex()})'


def get_volume_instance(drive: str, current_session: bool = False) -> Optional[WMIObject]:
    """
    获取指定盘符的 UWF 卷实例
    :param drive: 盘符字符串，例如 "C:"
    :param current_session: 是否查询当前会话的卷
    :return: UWF 卷实例或 None
    """
    try:
        volumes = query_service_instance(
            class_name='UWF_Volume',
            query=f'SELECT * FROM UWF_Volume WHERE DriveLetter="{drive}" AND CurrentSession={str(current_session)}'
        )
        return volumes[0]
    except pywintypes.com_error as e:
        print(f'[!] Querying volume failed: {format_com_error(e=e)}')
    except IndexError:
        print(f'[!] No UWF volume found for drive {drive}')
    except Exception as e:
        print(f'[!] An unexpected error occurred: {e}')
    return None
