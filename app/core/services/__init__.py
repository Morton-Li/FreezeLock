import threading

from win32com import client

# 全局私有 WMI 对象引用
_wmi_client = None
_uwf_service_installed: bool = False  # UWF 服务安装状态
_uwf_classes: list[str] = []  # ['UWF_Filter', 'UWF_ExcludedRegistryKey', 'UWF_Overlay', 'UWF_Volume', 'UWF_OverlayConfig', 'UWF_RegistryFilter', 'UWF_OverlayFile', 'UWF_Servicing', 'UWF_ExcludedFile']
_lock = threading.Lock()

__all__ = [
    'get_wmi_client',
    'refresh_wmi_client',
    'uwf_classes',
    'is_uwf_installed',
]


def get_wmi_client() -> client.CDispatch:
    """
    获取 WMI 客户端对象
    :return:
    """
    if _wmi_client is None:
        with _lock:
            if _wmi_client is None:  # 双重检查锁定
                _init_wmi_client()
    return _wmi_client


def _init_wmi_client() -> bool:
    """
    初始化 WMI 客户端对象
    :return:
    """
    global _wmi_client, _uwf_classes, _uwf_service_installed

    _wmi_client = None  # 重置 WMI 客户端对象
    _uwf_service_installed = False  # 重置 UWF 服务安装状态
    _uwf_classes.clear()  # 清空全局 UWF 类列表

    try:
        # 使用 win32com.client 获取 WMI 客户端
        _wmi_client = client.GetObject(Pathname=r'winmgmts:\\.\root\standardcimv2\embedded')
        # 获取所有类定义防止超范围
        all_classes = _wmi_client.SubclassesOf()
        print(f'[+] WMI 客户端初始化成功，找到 {len(all_classes)} 个类')
        # 过滤出 UWF 相关的类
        _uwf_classes.extend([
            cls.Path_.Class
            for cls in all_classes
            if cls.Path_.Class.startswith("UWF_")
        ])
        print(f'[+] 找到 {len(_uwf_classes)} 个 UWF 相关类: {_uwf_classes}')
        # 检查 UWF 服务是否安装
        _uwf_service_installed = bool(_uwf_classes)
    except Exception as e:
        raise RuntimeError(f'[!] 初始化 WMI 客户端失败: {e}') from e

    return _wmi_client is not None


def refresh_wmi_client() -> client.CDispatch:
    """
    刷新 WMI 客户端对象
    :return:
    """
    with _lock:
        _init_wmi_client()
    return _wmi_client


def is_uwf_installed() -> bool:
    """
    检查 UWF 服务是否安装
    :return:
    """
    return _uwf_service_installed is True  # 防止修改全局状态


def uwf_classes() -> list[str]:
    """
    获取已安装的 UWF 类列表
    :return: UWF 类列表
    """
    return _uwf_classes.copy()  # 返回类列表的副本以防止修改全局状态
