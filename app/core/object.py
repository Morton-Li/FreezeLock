from functools import cached_property
from typing import Any

from win32com.client import CDispatch


class WMIObject:
    """
    Base class for WMI objects.
    """
    def __init__(self, wmi_object: CDispatch):
        self._wmi_object = wmi_object

    def __getattr__(self, name: str):
        """支持 obj.property 访问 WMI 字段"""
        if name in ['properties', 'methods']: # 避免与 properties 和 methods 属性冲突
            return self.__getattribute__(name)
        try:
            return getattr(self._wmi_object, name)
        except AttributeError as e:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}'") from e

    def __getitem__(self, key: str or int):
        """支持 obj['property'] 访问 WMI 字段"""
        if isinstance(key, int):
            # 如果是整数索引
            return WMIObject(self._wmi_object[key])  # 返回原生对象
        try:
            return getattr(self._wmi_object, key)
        except AttributeError as e:
            raise KeyError(f"{self.__class__.__name__} has no key '{key}'") from e

    def __iter__(self):
        """支持迭代 WMI 对象的属性"""
        for obj in self._wmi_object:
            # 如果是 WMI 对象，则包装为 WMIObject, 否则直接返回原对象
            yield WMIObject(obj) if isinstance(obj, CDispatch) else obj

    def __contains__(self, key: str):
        """支持 'property' in obj 语法检查属性是否存在"""
        return key in self.properties

    @cached_property
    def properties(self) -> list[str]:
        """返回 WMI 对象的所有属性名称"""
        return [prop.Name for prop in self._wmi_object.Properties_]

    @cached_property
    def methods(self) -> list[str]:
        """返回 WMI 对象的所有方法名称"""
        return [method.Name for method in self._wmi_object.Methods_]

    def as_dict(self) -> dict:
        """将 WMI 对象转换为字典"""
        result = {}
        for prop in self._wmi_object.Properties_:
            result[prop.Name] = prop.Value
        return result

    def execute_method(self, method_name: str, **params) -> Any:
        """执行 WMI 对象的方法"""
        if method_name not in self.methods: raise AttributeError(f"{self.__class__.__name__} has no method '{method_name}'")
        method = self._wmi_object.Methods_.Item(method_name)  # 获取方法定义
        in_params_def = method.InParameters  # 获取方法的输入参数定义，可能为 None（无参方法）
        in_obj = None  # 默认输入参数定义，in_obj 设为 None
        if in_params_def is not None:
            in_obj = in_params_def.SpawnInstance_()  # 创建输入参数实例
            # 如果有参数，则在输入参数实例上赋值
            for k, v in (params or {}).items():
                try:
                    in_obj.Properties_.Item(k).Value = v  # 在参数对象上赋值
                except Exception as e:
                    raise ValueError(f"Invalid parameter '{k}' for method '{method_name}'") from e
        return self._wmi_object.ExecMethod_(method_name, in_obj)
