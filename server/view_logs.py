"""
日志查看脚本

使用方法:
  python view_logs.py          # 查看最近 50 行日志
  python view_logs.py 100      # 查看最近 100 行日志
  python view_logs.py -f       # 实时查看日志 (类似 tail -f)
"""

import sys
import time
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "logs" / "app.log"


def view_logs(lines: int = 50):
    if not LOG_FILE.exists():
        print(f"日志文件不存在: {LOG_FILE}")
        print("请先启动服务器生成日志")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
        print(f"=== 最近 {len(recent)} 行日志 ===\n")
        for line in recent:
            print(line.rstrip())


def follow_logs():
    if not LOG_FILE.exists():
        print(f"日志文件不存在: {LOG_FILE}")
        print("请先启动服务器生成日志")
        return

    print(f"=== 实时查看日志 (Ctrl+C 退出) ===\n")
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                print(line.rstrip())
            else:
                time.sleep(0.5)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "-f" or arg == "--follow":
            try:
                follow_logs()
            except KeyboardInterrupt:
                print("\n\n已停止查看日志")
        else:
            try:
                lines = int(arg)
                view_logs(lines)
            except ValueError:
                print(f"无效参数: {arg}")
                print("用法: python view_logs.py [行数|-f]")
    else:
        view_logs()
