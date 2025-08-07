import subprocess


def run_command(cmd: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            shell=False  # 更安全
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip() or str(e)
