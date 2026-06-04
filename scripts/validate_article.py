#!/usr/bin/env python3
"""
validate_article.py — 文章综合校验(loan-article-skill 专用)

8 项检查:
  1. 字数 1800-2500
  2. 含城市名(标题 / 首段 / 末段)
  3. 含主题核心搜索词
  4. 包含至少 1 个长尾搜索词(主题+城市 / 主题+流程 / 主题+条件 / 主题+怎么办)
  5. 无绝对词(最好 / 第一 / 唯一 / 100% / 绝对下款 / 稳过 / 包过 / 最低)
  6. 无具体银行名(中国银行 / 工商银行 / 招商银行 等)
  7. 末段含 CTA 元素(咨询 / 留资 / 扫码 / 留言 / 联系)
  8. 段落数 >= 6

用法:
  python3 validate_article.py --file article.md --city 北京 --topic 房产抵押
  python3 validate_article.py --file article.md --city 北京 --topic 房产抵押 --json
"""
import argparse
import json
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

# 复用 count_words
sys.path.insert(0, str(Path(__file__).parent))
from count_words import count  # type: ignore

# === 检查规则定义 ===

# 绝对词(出现即报错)
ABSOLUTE_WORDS = [
    r"最好", r"最佳", r"第一(?![步阶段])",  # 允许"第一步"
    r"唯一", r"独家", r"100%", r"绝对下款", r"绝对通过",
    r"最低利率", r"利率最低", r"最快", r"最强", r"稳过", r"包过",
    r"必下款", r"必批", r"躺着也赚", r"稳赚不赔",
]

# 禁用的具体银行名(正则,支持前后标点)
BANK_NAMES = [
    r"中国银行", r"工商银行", r"农业银行", r"建设银行", r"交通银行",
    r"招商银行", r"浦发银行", r"中信银行", r"光大银行", r"华夏银行",
    r"民生银行", r"兴业银行", r"平安银行", r"广发银行", r"浙商银行",
    r"恒丰银行", r"渤海银行", r"邮政储蓄银行", r"邮储银行",
    r"北京银行", r"上海银行", r"南京银行", r"宁波银行", r"江苏银行",
    r"杭州银行", r"盛京银行", r"哈尔滨银行", r"锦州银行",
    r"农商银行", r"农村商业银行", r"信用合作社", r"信用社",
]

# 长尾搜索词后缀
LONG_TAIL_SUFFIXES = [
    "流程", "条件", "怎么办", "怎么选", "怎么申请",
    "哪家好", "利率", "额度", "多久", "需要什么",
    "注意事项", "靠谱", "正规", "哪个银行好", "能贷多少",
    "怎么操作", "攻略", "一文看懂", "需要哪些资料",
]


def make_absolute_pattern() -> re.Pattern:
    return re.compile("|".join(f"(?:{p})" for p in ABSOLUTE_WORDS))


def make_bank_pattern() -> re.Pattern:
    return re.compile("|".join(f"(?:{p})" for p in BANK_NAMES))


def check_word_count(text: str) -> dict:
    stats = count(text)
    n = stats["total"]
    ok = 1800 <= n <= 2500
    return {
        "check": "字数 1800-2500",
        "pass": ok,
        "detail": f"实际 {n} 字,要求 [1800, 2500]",
        "actual": n,
    }


def check_city_in_sections(text: str, city: str) -> dict:
    """城市名必须在标题、首段、末段。"""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return {"check": "城市名分布", "pass": False, "detail": "文章为空"}
    # 标题:首个 H1 / H2 / 加粗 / 第一个非空行
    title_line = lines[0]
    # 首段:正文段
    body_start = next(
        (i for i, l in enumerate(lines) if not l.startswith(("#", ">", "-"))),
        0,
    )
    opening = "\n".join(lines[body_start:body_start + 10])
    # 末段
    closing = "\n".join(lines[-10:])

    in_title = city in title_line
    in_opening = city in opening
    in_closing = city in closing
    ok = in_title and in_opening and in_closing
    return {
        "check": f"城市名({city})在标题/首段/末段",
        "pass": ok,
        "detail": f"标题={'✅' if in_title else '❌'} 首段={'✅' if in_opening else '❌'} 末段={'✅' if in_closing else '❌'}",
    }


def check_topic_keyword(text: str, topic: str) -> dict:
    """主题核心词在标题 / 首段 / H2 / 末段。"""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return {"check": "主题核心词分布", "pass": False, "detail": "文章为空"}
    title = lines[0]
    body_start = next(
        (i for i, l in enumerate(lines) if not l.startswith(("#", ">", "-"))), 0
    )
    opening = "\n".join(lines[body_start:body_start + 8])
    h2_lines = [l for l in lines if l.startswith("##")]
    closing = "\n".join(lines[-8:])

    in_title = topic in title
    in_opening = topic in opening
    in_h2 = any(topic in h for h in h2_lines)
    in_closing = topic in closing
    ok = in_title and in_opening and (in_h2 or in_closing)
    return {
        "check": f"主题词({topic})分布",
        "pass": ok,
        "detail": f"标题={'✅' if in_title else '❌'} 首段={'✅' if in_opening else '❌'} H2={'✅' if in_h2 else '❌'} 末段={'✅' if in_closing else '❌'}",
    }


def check_long_tail(text: str, topic: str, city: str) -> dict:
    """至少 1 个长尾词(主题+城市 / 主题+流程 等)。"""
    candidates = [f"{topic}{city}", f"{city}{topic}"]
    candidates += [f"{topic}{s}" for s in LONG_TAIL_SUFFIXES]
    candidates += [f"{topic}的{s}" for s in ["流程", "条件", "利率"]]
    found = [c for c in candidates if c in text]
    ok = len(found) >= 1
    return {
        "check": "长尾搜索词覆盖",
        "pass": ok,
        "detail": f"命中 {len(found)} 个:{', '.join(found[:5])}",
    }


def check_no_absolute_words(text: str) -> dict:
    pat = make_absolute_pattern()
    matches = pat.findall(text)
    ok = len(matches) == 0
    return {
        "check": "无绝对词",
        "pass": ok,
        "detail": f"命中 {len(matches)} 处:{', '.join(matches[:5])}" if matches else "未发现绝对词 ✅",
    }


def check_no_bank_names(text: str) -> dict:
    pat = make_bank_pattern()
    matches = pat.findall(text)
    ok = len(matches) == 0
    return {
        "check": "无具体银行名",
        "pass": ok,
        "detail": f"命中 {len(matches)} 处:{', '.join(set(matches))}" if matches else "未发现具体银行名 ✅",
    }


def check_cta_in_closing(text: str) -> dict:
    cta_keywords = ["咨询", "留言", "扫码", "联系", "留资", "获取", "定制", "添加", "微信", "电话"]
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    closing = "\n".join(lines[-15:])
    found = [k for k in cta_keywords if k in closing]
    ok = len(found) >= 1
    return {
        "check": "末段含 CTA 元素",
        "pass": ok,
        "detail": f"命中关键词:{', '.join(found) if found else '无'}",
    }


def check_paragraphs(text: str) -> dict:
    """段落数 >= 6(按空行 / H2 划分)。"""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    n = len([p for p in paragraphs if p.strip()])
    ok = n >= 6
    return {
        "check": "段落数 >= 6",
        "pass": ok,
        "detail": f"实际 {n} 段",
    }


def validate(text: str, city: str, topic: str) -> dict:
    checks = [
        check_word_count(text),
        check_city_in_sections(text, city),
        check_topic_keyword(text, topic),
        check_long_tail(text, topic, city),
        check_no_absolute_words(text),
        check_no_bank_names(text),
        check_cta_in_closing(text),
        check_paragraphs(text),
    ]
    passed = sum(1 for c in checks if c["pass"])
    return {
        "city": city,
        "topic": topic,
        "total_checks": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "all_pass": passed == len(checks),
        "checks": checks,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="文章综合校验")
    p.add_argument("--file", required=True, help="文章文件路径")
    p.add_argument("--city", required=True, help="目标城市(如:北京)")
    p.add_argument("--topic", required=True, help="主题核心词(如:房产抵押)")
    p.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = p.parse_args()

    text = Path(args.file).read_text(encoding="utf-8")
    result = validate(text, args.city, args.topic)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print(f"Article validation: {args.file}")
        print(f"City: {args.city} | Topic: {args.topic}")
        print("=" * 60)
        for c in result["checks"]:
            mark = "[OK]" if c["pass"] else "[FAIL]"
            print(f"{mark} {c['check']}: {c['detail']}")
        print("=" * 60)
        passed = result["passed"]
        total = result["total_checks"]
        if result["all_pass"]:
            print(f"ALL PASS: {passed}/{total}")
            return 0
        else:
            print(f"FAILED: {passed}/{total} checks")
            return 1


if __name__ == "__main__":
    sys.exit(main())
