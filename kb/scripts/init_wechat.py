"""Initialize wechat-cli with administrator rights (needed to read WeChat's
decryption key from process memory).

Usage:
    python init_wechat.py            # auto-detect account, ask to elevate
    python init_wechat.py --account wxid_q33w51eblhqz22_ae9c

Why admin is required:
  WeChat 4.x stores each database with an independent SQLCipher 4 key
  (AES-256-CBC + HMAC-SHA512, PBKDF2 256k iterations). The key only exists in
  the WeChat process's memory. Reading another process's memory requires
  PROCESS_VM_READ, which for a process at a higher integrity level requires
  SeDebugPrivilege -- i.e. an elevated terminal.

  Symptom without elevation: the scanner finds every database salt correctly
  but reports "0/N salts 找到密钥" and ReadProcessMemory fails with
  error 299 (ERROR_PARTIAL_COPY).
"""
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

WX_ROOTS = [
    r'E:/Documents/xwechat_files',
    os.path.expanduser('~/Documents/xwechat_files'),
    os.path.expanduser('~/xwechat_files'),
    'D:/Program Files/Tencent/Weixin/xwechat_files',
]

CLI = r'C:/Users/Public/wechat-cli/venv/Scripts/wechat-cli.exe'


def find_accounts():
    accounts = []
    for root in WX_ROOTS:
        for db in glob.glob(os.path.join(root, '*', 'db_storage', 'favorite', 'favorite.db')):
            acc = Path(db).parents[2].name
            size = os.path.getsize(db)
            accounts.append({'account': acc, 'db_dir': str(Path(db).parents[1]), 'fav_kb': round(size / 1024)})
    return accounts


def is_admin():
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def main():
    preset = None
    if '--account' in sys.argv:
        preset = sys.argv[sys.argv.index('--account') + 1]

    # When running elevated the console output is invisible, so mirror it to a log.
    log_path = Path(__file__).resolve().parent / 'init_wechat.log'
    log_fh = None
    try:
        log_fh = open(log_path, 'w', encoding='utf-8')
    except Exception:
        pass

    def emit(text=''):
        print(text)
        if log_fh:
            log_fh.write(text + '\n')
            log_fh.flush()

    accounts = find_accounts()
    if not accounts:
        emit('未找到微信数据目录。请确认已安装微信 4.x 并登录过。')
        emit('搜索位置:')
        for r in WX_ROOTS:
            emit('  ' + r)
        return 1

    emit('发现微信账号:')
    for i, a in enumerate(accounts):
        emit(f"  [{i}] {a['account']}   收藏库 {a['fav_kb']} KB")
        emit(f"      {a['db_dir']}")

    idx = 0
    if preset:
        match = [i for i, a in enumerate(accounts) if a['account'] == preset]
        if not match:
            emit(f'未找到账号 {preset}')
            return 1
        idx = match[0]
    elif len(accounts) > 1:
        raw = input(f'选择账号 [0-{len(accounts)-1}]，回车用 0: ').strip()
        idx = int(raw) if raw.isdigit() and 0 <= int(raw) < len(accounts) else 0

    acc = accounts[idx]
    emit(f"\n使用账号: {acc['account']}")

    if not is_admin():
        emit('')
        emit('[!] 当前不是管理员权限。')
        emit('    读取微信进程内存需要管理员权限(SeDebugPrivilege)。')
        emit('    下面将以管理员身份重新运行本脚本(会弹出 UAC 窗口,请点"是")。')
        ps = (
            f'Start-Process -FilePath "{sys.executable}" -ArgumentList '
            f'"{os.path.abspath(__file__)}","--account","{acc["account"]}" '
            f'-Verb RunAs -Wait'
        )
        subprocess.run(['powershell', '-NoProfile', '-Command', ps],
                       capture_output=True, text=True)
        if log_path.exists():
            emit('')
            emit('--- 提权进程输出 ---')
            emit(log_path.read_text(encoding='utf-8', errors='replace')[-3000:])
        emit('')
        emit('若上面没有输出,说明 UAC 被取消或弹窗未显示。手动以管理员身份运行:')
        emit(f'  {CLI} init --db-dir "{acc["db_dir"]}"')
        return 1

    emit('')
    emit('管理员模式，开始提取密钥...')
    cmd = [CLI, 'init', '--db-dir', acc['db_dir'], '--force']
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    emit(r.stdout[-3000:])
    if r.stderr:
        emit(r.stderr[-1500:])

    emit('')
    emit('=== 验证 ===')
    fav = subprocess.run([CLI, 'favorites', '--limit', '5'],
                         capture_output=True, text=True, encoding='utf-8', errors='replace')
    if fav.returncode == 0 and fav.stdout.strip():
        emit(fav.stdout[:2000])
        return 0
    emit('读取失败: ' + (fav.stdout + fav.stderr)[:600])
    return 1


if __name__ == '__main__':
    sys.exit(main())
