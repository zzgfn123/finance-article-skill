#!/usr/bin/env python3
"""
count_words.py — 中文字数统计(loan-article-skill 专用)

行为:
- 剔除 Markdown 标记(# / * / - / > / [ ] / ( ) / ` 等)
- 剔除 URL、邮箱、HTML 标签
- 剔除所有 ASCII 标点与空白
- 保留中文字符 + 中文标点(只用于显示,不计入字数)
- 只统计:汉字 + 中文数字 + 英文字母(用于术语)
- 输出:总字符数(用于合规判断),汉字数(用于硬约束 1800-2500)

用法:
  echo "<文章全文>" | python3 count_words.py
  python3 count_words.py < article.md
  python3 count_words.py --file article.md
  python3 count_words.py --check-min 1800 --check-max 2500 --file article.md
"""
import argparse
import re
import sys
from pathlib import Path

# Force UTF-8 output for Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 中文字符(含基本汉字 + 扩展 A 区)
HAN_PATTERN = re.compile(r"[一-鿿\U00010000-\U0001afff]")
# 英文字母(术语用,纳入字数)
ASCII_WORD_PATTERN = re.compile(r"[A-Za-z]+")
# 中文数字
CN_NUM_PATTERN = re.compile(r"[〇零一二三四五六七八九十百千万亿]+")

# 剔除规则
MD_FENCE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]+`")
URL_PATTERN = re.compile(r"https?://[^\s)]+")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
HTML_TAG = re.compile(r"<[^>]+>")
MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")  # 保留 [] 内容
MD_HEADING = re.compile(r"^#{1,6}\s+", re.MULTILINE)
MD_BOLD = re.compile(r"\*\*([^*]+)\*\*|__([^_]+)__")
MD_ITALIC = re.compile(r"\*([^*]+)\*|_([^_]+)_")


def strip_markdown(text: str) -> str:
    """剥除 Markdown 标记,保留正文。"""
    text = MD_FENCE.sub(" ", text)
    text = INLINE_CODE.sub(" ", text)
    text = URL_PATTERN.sub(" ", text)
    text = EMAIL_PATTERN.sub(" ", text)
    text = HTML_TAG.sub(" ", text)
    text = MD_LINK.sub(r"\1", text)  # 链接保留文字
    text = MD_HEADING.sub("", text)
    text = MD_BOLD.sub(r"\1\2", text)
    text = MD_ITALIC.sub(r"\1\2", text)
    return text


def count(text: str) -> dict:
    """统计字数。"""
    cleaned = strip_markdown(text)
    han = HAN_PATTERN.findall(cleaned)
    ascii_words = ASCII_WORD_PATTERN.findall(cleaned)
    cn_nums = CN_NUM_PATTERN.findall(cleaned)
    han_count = len(han)
    ascii_count = sum(len(w) for w in ascii_words)
    cn_num_count = sum(len(n) for n in cn_nums)
    # 总字数:汉字 + ASCII 字母 + 中文数字(汉字与中文数字不会重复计)
    # 汉字和中文数字可能有交叠,实际去重后更准
    return {
        "han": han_count,
        "ascii": ascii_count,
        "cn_num": cn_num_count,
        "total": han_count + ascii_count,  # 主指标
        "raw_chars": len(cleaned),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="中文字数统计(loan-article-skill)")
    p.add_argument("--file", help="文章文件路径(也可走 stdin)")
    p.add_argument("--check-min", type=int, default=0, help="最小字数阈值,低于则 exit 1")
    p.add_argument("--check-max", type=int, default=0, help="最大字数阈值,高于则 exit 1")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    args = p.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("用法: echo '<text>' | python3 count_words.py", file=sys.stderr)
        print("      python3 count_words.py --file article.md", file=sys.stderr)
        return 2

    stats = count(text)

    if args.json:
        import json

        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print(f"Chinese: {stats['han']}")
        print(f"ASCII letters: {stats['ascii']}")
        print(f"Chinese numerals: {stats['cn_num']}")
        print(f"Total (primary): {stats['total']}")
        print(f"Raw chars (after stripping): {stats['raw_chars']}")

    # 阈值检查
    if args.check_min and stats["total"] < args.check_min:
        print(f"❌ 字数 {stats['total']} 低于最小值 {args.check_min}", file=sys.stderr)
        return 1
    if args.check_max and stats["total"] > args.check_max:
        print(f"❌ 字数 {stats['total']} 超过最大值 {args.check_max}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
