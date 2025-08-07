# FreezeLock

**FreezeLock** 是一款基于 PySide6 构建的 Windows 平台图形化工具，旨在简洁、可靠地管理 **UWF（Unified Write Filter）统一写入过滤器**。

---

## 🎯 功能特性

- ✅ 实时查看 UWF 当前启用状态
- ✅ 开启 / 关闭统一写入过滤器
- ✅ 管理文件、文件夹排除项
- ✅ 控制磁盘保护范围（启用卷过滤）

---

## 🛠 安装与运行

### ✅ 运行已构建版本

> 建议使用已打包的 `.exe` 文件，无需 Python 环境，双击即可运行。

### 🔧 从源代码运行（开发者）

```bash
# 安装依赖
pip install -r requirements.txt

# 启动主程序
python main.py
```

### 🧊 打包构建（推荐使用 Nuitka）

FreezeLock 使用 Nuitka 将 PySide6 项目编译为可执行文件：

```bash
python build.py
```

---

## 🔐 权限说明

FreezeLock 启动时将自动请求 **管理员权限**，以确保能够访问 WMI 接口并修改 UWF 设置。UWF 的配置修改通常需要重启系统以生效。

---

## 🧱 技术栈

* **Python 3.12+**
* **PySide6**：图形界面构建
* **win32com**：WMI 接口访问
* **Nuitka**：编译为独立可执行文件

---

## 📌 注意事项

* 本工具仅适用于 **Windows 10 / 11 专业版、专业工作站版、企业版或 LTSC**。
* 启用 UWF 后，除被排除的路径外，所有更改将在重启后丢失。

---

## 📄 许可协议

FreezeLock Project 遵循 Apache License 2.0 协议发布。

