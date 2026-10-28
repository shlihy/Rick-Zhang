"""Collect WeChat local files (documents / videos) into a Markdown knowledge base.

This path needs NO database decryption and NO process injection:
  msg\file    -> received documents, plain text (pdf/xlsx/docx/...)
  msg\video   -> received videos + thumbnails, plain text
  msg\attach  -> received images, AES-encrypted .dat (skipped by default)

Usage:
    python collect_wechat_files.py --out E:/WorkBuddy/kb
    python collect_wechat_files.py --out E:/WorkBuddy/kb --include-encrypted-images
"""
import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

DOC_EXT = {'.pdf', '.xlsx', '.xls', '.docx', '.doc', '.pptx', '.ppt', '.md',
           '.txt', '.csv', '.json', '.yaml', '.yml', '.html', '.htm', '.py',
           '.js', '.ts', '.java', '.go', '.rs', '.sql', '.sh'}
MEDIA_EXT = {'.mp4', '.mov', '.avi', '.mkv', '.jpg', '.jpeg', '.png', '.gif',
             '.webp', '.mp3', '.wav', '.m4a', '.aac', '.flac', '.zip', '.rar',
             '.7z', '.epub'}

# Files worth indexing as text content (WorkBuddy can read these)
TEXTUAL = DOC_EXT

ACCOUNTS = [
    'shlihy0730_b54d',
    'wxid_q33w51eblhqz22_ae9c',
    'wxid_vpv25cmc8axy22_0148',
]

ROOTS = [
    Path(r'E:/Documents/xwechat_files'),
    Path.home() / 'Documents' / 'xwechat_files',
    Path.home() / 'xwechat_files',
]


def find_msg_roots():
    out = []
    for root in ROOTS:
        if not root.exists():
            continue
        for acc in ACCOUNTS:
            p = root / acc / 'msg'
            if p.exists():
                out.append((acc, p))
    return out


def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_name(s, limit=80):
    s = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', s).strip()
    return (s[:limit] or 'untitled')


def collect(out_root, include_encrypted_images=False, copy_files=True):
    msg_roots = find_msg_roots()
    if not msg_roots:
        print('未找到微信 msg 目录。搜索位置:')
        for r in ROOTS:
            print('  ', r)
        return []

    out_root = Path(out_root)
    vault = out_root / 'vault'
    vault.mkdir(parents=True, exist_ok=True)
    index = []
    seen = set()

    for account, msg_root in msg_roots:
        for sub in ('file', 'video'):
            src_dir = msg_root / sub
            if not src_dir.exists():
                continue
            for root, dirs, files in os.walk(src_dir):
                for fn in files:
                    src = Path(root) / fn
                    ext = src.suffix.lower()
                    if ext not in DOC_EXT and ext not in MEDIA_EXT:
                        continue
                    try:
                        st = src.stat()
                    except OSError:
                        continue
                    # month folder encodes the receive time: file\2026-10\xxx.pdf
                    rel = src.relative_to(src_dir)
                    month = rel.parts[0] if len(rel.parts) > 1 else 'unknown'
                    try:
                        digest = sha1(src)
                    except OSError:
                        continue
                    if digest in seen:
                        continue
                    seen.add(digest)

                    record = {
                        'account': account,
                        'source': str(src),
                        'rel': str(rel).replace('\\', '/'),
                        'month': month,
                        'ext': ext,
                        'size': st.st_size,
                        'mtime': datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
                        'sha1': digest,
                    }

                    if ext in TEXTUAL:
                        dest = vault / 'docs' / account / month / safe_name(rel.name)
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        if copy_files:
                            shutil.copy2(src, dest)
                            record['vault_path'] = str(dest.relative_to(out_root)).replace('\\', '/')
                    else:
                        record['kind'] = 'media'

                    index.append(record)

    if include_encrypted_images:
        for account, msg_root in msg_roots:
            src_dir = msg_root / 'attach'
            if not src_dir.exists():
                continue
            for root, dirs, files in os.walk(src_dir):
                for fn in files:
                    src = Path(root) / fn
                    if src.suffix.lower() != '.dat':
                        continue
                    try:
                        st = src.stat()
                        digest = sha1(src)
                    except OSError:
                        continue
                    if digest in seen:
                        continue
                    seen.add(digest)
                    rel = src.relative_to(src_dir)
                    index.append({
                        'account': account,
                        'source': str(src),
                        'rel': str(rel).replace('\\', '/'),
                        'month': rel.parts[0] if len(rel.parts) > 1 else 'unknown',
                        'ext': '.dat',
                        'size': st.st_size,
                        'mtime': datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
                        'sha1': digest,
                        'kind': 'encrypted-image',
                    })

    (out_root / 'index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding='utf-8')
    return index


def write_manifest(out_root, index):
    out_root = Path(out_root)
    lines = ['# 微信本地文件知识库', '',
             f'采集时间：{datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")}',
             f'条目数：{len(index)}', '']
    by_month = {}
    for r in index:
        by_month.setdefault((r['account'], r['month']), []).append(r)
    for (acc, month) in sorted(by_month, reverse=True):
        rows = by_month[(acc, month)]
        total = sum(r['size'] for r in rows)
        lines.append(f'## {acc} · {month}  ({len(rows)} 个, {total/1048576:.1f} MB)')
        lines.append('')
        lines.append('| 类型 | 大小 | 原始路径 |')
        lines.append('|---|---|---|')
        for r in sorted(rows, key=lambda x: x['mtime'], reverse=True)[:80]:
            kind = '文档' if r['ext'] in DOC_EXT else ('图片(加密)' if r['kind'] == 'encrypted-image' else '媒体')
            lines.append(f"| {kind} `{r['ext']}` | {r['size']//1024} KB | `{r['rel']}` |")
        if len(rows) > 80:
            lines.append(f'| … | | 其余 {len(rows)-80} 个见 index.json |')
        lines.append('')
    (out_root / 'MANIFEST.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='E:/WorkBuddy/kb')
    ap.add_argument('--include-encrypted-images', action='store_true')
    ap.add_argument('--no-copy', action='store_true', help='只建索引,不复制文件')
    args = ap.parse_args()

    index = collect(args.out, args.include_encrypted_images, copy_files=not args.no_copy)
    write_manifest(args.out, index)

    docs = sum(1 for r in index if r['ext'] in DOC_EXT)
    media = sum(1 for r in index if r.get('kind') == 'media')
    enc = sum(1 for r in index if r.get('kind') == 'encrypted-image')
    total = sum(r['size'] for r in index)
    print(f'采集完成: {len(index)} 条 | 文档 {docs} | 媒体 {media} | 加密图片 {enc} | 合计 {total/1073741824:.2f} GB')
    print(f'清单: {Path(args.out) / "MANIFEST.md"}')
    print(f'索引: {Path(args.out) / "index.json"}')


if __name__ == '__main__':
    main()
