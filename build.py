import os
import subprocess
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from app.version import __version__


def build():
    """
    使用 Nuitka 构建应用程序
    :return:
    """
    print("[*] 开始构建 FreezeLock 应用程序...")

    venv_dir_list = ['venv', '.venv']
    python_bin = None
    for venv_dir in venv_dir_list:
        abs_venv_dir = os.path.join(project_root, venv_dir)
        if os.path.exists(abs_venv_dir) and os.path.exists(os.path.join(abs_venv_dir, 'Scripts', 'python.exe')):
            print(f"[*] 找到虚拟环境目录: {venv_dir}")
            python_bin = os.path.join(abs_venv_dir, 'Scripts', 'python.exe')
            break
    if not python_bin:
        print("[!] 未找到可用的虚拟环境目录 'venv'，请先创建虚拟环境。")
        exit(1)

    cmd = [
        python_bin, '-m', 'nuitka',
        '--standalone',
        # r'--include-data-dir=app\assets=assets',
        '--output-dir=build',
        '--output-filename=FreezeLock',
        '--no-pyi-file',
        '--no-pyi-stubs',
        '--assume-yes-for-downloads',
        '--windows-console-mode=disable',
        r'--windows-icon-from-ico=app\assets\freezelock.ico',
        '--windows-uac-admin',
        '--enable-plugin=pyside6',
        '--product-name=FreezeLock',
        f'--product-version={__version__}',
        'main.py',
    ]

    print("[*] 执行 Nuitka 构建命令...")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] 构建失败: {e}")
        exit(1)
    print("[✓] 构建完成")

if __name__ == "__main__":
    build()
