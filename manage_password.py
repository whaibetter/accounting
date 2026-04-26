#!/usr/bin/env python3
"""
密码管理命令行工具。

用法：
    python manage_password.py reset [--password NEW_PASSWORD]
    python manage_password.py change --old OLD_PASSWORD --new NEW_PASSWORD
    python manage_password.py check  --password PASSWORD
    python manage_password.py info

功能：
    - reset:  重置密码（无需旧密码，直接设置新密码）
    - change: 修改密码（需验证旧密码）
    - check:  检查密码强度
    - info:   查看当前密码存储状态

审计日志：
    所有密码操作均记录到 server/logs/password_audit.log
"""

import argparse
import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

LOG_DIR = os.path.join(os.path.dirname(__file__), "server", "logs")
LOG_DIR = os.path.abspath(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)

AUDIT_LOG = os.path.join(LOG_DIR, "password_audit.log")

audit_logger = logging.getLogger("password_audit")
audit_logger.setLevel(logging.INFO)
audit_handler = logging.FileHandler(AUDIT_LOG, encoding="utf-8")
audit_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
audit_logger.addHandler(audit_handler)


def _audit_log(action: str, detail: str, success: bool) -> None:
    status = "SUCCESS" if success else "FAILED"
    audit_logger.info(f"{status} | {action} | {detail}")


def cmd_reset(args) -> None:
    from app.database import init_db
    init_db()

    from app.auth import reset_password, check_password_strength

    new_password = args.password
    if not new_password:
        new_password = input("请输入新密码: ").strip()
        if not new_password:
            print("❌ 密码不能为空")
            _audit_log("RESET", "密码为空", False)
            return
        confirm = input("请确认新密码: ").strip()
        if new_password != confirm:
            print("❌ 两次输入的密码不一致")
            _audit_log("RESET", "密码不一致", False)
            return

    valid, msg = check_password_strength(new_password)
    if not valid:
        print(f"❌ 密码强度不足: {msg}")
        _audit_log("RESET", f"密码强度不足: {msg}", False)
        return

    success, msg = reset_password(new_password)
    if success:
        print(f"✅ {msg}")
        _audit_log("RESET", "密码重置成功", True)
    else:
        print(f"❌ {msg}")
        _audit_log("RESET", f"重置失败: {msg}", False)


def cmd_change(args) -> None:
    from app.database import init_db
    init_db()

    from app.auth import change_password

    old_password = args.old
    new_password = args.new

    if not old_password:
        old_password = input("请输入旧密码: ").strip()
    if not new_password:
        new_password = input("请输入新密码: ").strip()
        confirm = input("请确认新密码: ").strip()
        if new_password != confirm:
            print("❌ 两次输入的密码不一致")
            _audit_log("CHANGE", "新密码不一致", False)
            return

    success, msg = change_password(old_password, new_password)
    if success:
        print(f"✅ {msg}")
        _audit_log("CHANGE", "密码修改成功", True)
    else:
        print(f"❌ {msg}")
        _audit_log("CHANGE", f"修改失败: {msg}", False)


def cmd_check(args) -> None:
    from app.auth import check_password_strength

    password = args.password
    if not password:
        password = input("请输入要检查的密码: ").strip()

    valid, msg = check_password_strength(password)
    if valid:
        print("✅ 密码强度符合要求")
        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:',.<>?/`~" for c in password):
            score += 1
        levels = ["弱", "一般", "较强", "强", "非常强"]
        print(f"   密码强度等级: {levels[min(score, 4)]}")
    else:
        print(f"❌ 密码强度不足: {msg}")


def cmd_info(args) -> None:
    from app.database import init_db
    init_db()

    from app.database import SessionLocal
    from app.models import SystemConfig

    db = SessionLocal()
    try:
        pw_row = db.query(SystemConfig).filter(SystemConfig.key == "password_hash").first()
        key_row = db.query(SystemConfig).filter(SystemConfig.key == "jwt_secret_key").first()
    finally:
        db.close()

    print("=" * 50)
    print("  密码存储状态信息")
    print("=" * 50)

    if pw_row:
        algo = "bcrypt" if not pw_row.value.startswith("sha256:") else "SHA-256（待升级）"
        print(f"  密码哈希算法: {algo}")
        print(f"  密码更新时间: {pw_row.updated_at}")
    else:
        print("  密码状态: 未初始化")

    if key_row:
        print(f"  JWT密钥状态: 已配置")
        print(f"  JWT密钥更新时间: {key_row.updated_at}")
    else:
        print("  JWT密钥状态: 未配置")

    print(f"  审计日志路径: {AUDIT_LOG}")
    print("=" * 50)

    legacy_pw = os.path.join(os.path.dirname(__file__), "server", "data", ".access_password")
    legacy_key = os.path.join(os.path.dirname(__file__), "server", "data", ".secret_key")
    if os.path.exists(legacy_pw) or os.path.exists(legacy_key):
        print("⚠️  检测到旧版密码/密钥文件仍存在，可手动删除：")
        if os.path.exists(legacy_pw):
            print(f"   - {legacy_pw}")
        if os.path.exists(legacy_key):
            print(f"   - {legacy_key}")


def main():
    parser = argparse.ArgumentParser(
        description="密码管理命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python manage_password.py reset --password myNewPass123
  python manage_password.py reset
  python manage_password.py change --old oldPass123 --new newPass456
  python manage_password.py check  --password testPass123
  python manage_password.py info
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    reset_parser = subparsers.add_parser("reset", help="重置密码（无需旧密码）")
    reset_parser.add_argument("--password", "-p", default=None, help="新密码（不提供则交互输入）")

    change_parser = subparsers.add_parser("change", help="修改密码（需旧密码验证）")
    change_parser.add_argument("--old", "-o", default=None, help="旧密码")
    change_parser.add_argument("--new", "-n", default=None, help="新密码")

    check_parser = subparsers.add_parser("check", help="检查密码强度")
    check_parser.add_argument("--password", "-p", default=None, help="要检查的密码")

    subparsers.add_parser("info", help="查看密码存储状态")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "reset": cmd_reset,
        "change": cmd_change,
        "check": cmd_check,
        "info": cmd_info,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
