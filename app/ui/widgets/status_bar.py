from typing import Optional, Callable

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLayout


class StatusBar(QWidget):
    """状态栏组件"""
    def __init__(
        self,
        layer_map: Optional[dict[str, Callable]] = None,
    ):
        super().__init__()
        self.setFixedHeight(28)  # 设置固定高度

        self._main_layout = QHBoxLayout()
        self._main_layout.setContentsMargins(8, 2, 8, 2)
        self._main_layout.setSpacing(12)
        self.setLayout(self._main_layout)

        self.child_layout_names = []
        if layer_map:
            for name, func in layer_map.items():
                component = func()
                if not isinstance(component, QLayout):
                    raise TypeError(f"Layer '{name}' must return a QLayout instance, got {type(component).__name__}")
                setattr(self, name, component)
                self.child_layout_names.append(name)
                self._main_layout.addLayout(component)

    def __getitem__(self, key: str):
        """支持 status_bar['name'] 访问子组件"""
        if key in self.child_layout_names:
            return getattr(self, key)
        raise KeyError(f"'{self.__class__.__name__}' object has no key '{key}'")

    @property
    def layout_names(self) -> list[str]:
        """返回所有子布局的名称"""
        return self.child_layout_names

    @property
    def layout(self) -> QLayout:
        """返回主布局"""
        return self._main_layout

    def add_layout(self, name: str, layout: QLayout, stretch: int = 0):
        """添加新的布局到状态栏"""
        if not isinstance(layout, QLayout): raise TypeError("Only QLayout instances can be added to StatusBar")
        if name in self.child_layout_names: raise ValueError(f"Layout with name '{name}' already exists in StatusBar")
        setattr(self, name, layout)
        self.child_layout_names.append(name)

        if stretch >= 0:
            self._main_layout.addLayout(layout, stretch)
        else:
            self._main_layout.addLayout(layout)
            self._main_layout.addStretch()  # 自动插入弹性空间
