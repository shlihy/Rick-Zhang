# 微信知识库

本地微信文件与收藏的结构化知识库。

## 目录结构

| 路径 | 内容 |
|---|---|
| `notes/` | 整理后的笔记（Markdown，WorkBuddy 可直接检索问答） |
| `collections/` | 收藏与文件索引（按月/主题） |
| `vault/` | 原始文档副本（PDF/Word/Excel 等，按账号+月份归档） |
| `scripts/` | 采集与整理脚本 |
| `logs/` | 同步日志 |

## 数据来源

- `E:/Documents/xwechat_files/<账号>/msg/file` — 收到的文档（明文）
- `E:/Documents/xwechat_files/<账号>/msg/video` — 收到的视频（明文）
- `E:/Documents/xwechat_files/<账号>/db_storage/favorite/favorite.db` — 收藏（SQLCipher 4 加密，需管理员权限提取密钥）

## 隐私

本仓库为 **private**。内容来自个人微信，仅供个人检索使用。
