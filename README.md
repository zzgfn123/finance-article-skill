# loan-article-skill

> 聚融网贷款文章生成器 · 可复用于任何 AI agent

## 简介

按城市(北上深一线 / 强二线 / 其他覆盖城市)与受众(企业主、上班族、房产持有者)
生成 **1800-2500 字** 的 SEO 友好型贷款科普 / 获客文章,严格遵守中国金融营销合规:
不写具体银行名、不用绝对词、关键字强相关、生成后字数自动审核。

## 6 条铁律

1. **不写具体银行名** → 用「五大行 / 股份制银行 / 地方性商业银行」
2. **不用绝对词** → 禁用「最好 / 第一 / 100% / 稳过」
3. **关键字强相关** → 主题核心词植入标题 / 首段 / H2 / 末段
4. **城市定制** → 城市名必出现 3+ 次,受众痛点从城市画像推导
5. **1800-2500 字硬约束** → 自动重写,严格审核
6. **合规立场** → 始终是「咨询服务方」,不直接放贷;略向助贷行业倾斜,不硬广

## 触发

```
/loan-article-skill 帮我写贷款文章,关于北京房产抵押
/loan-article-skill 帮我写关于上海企业贷款的文章,要 3 篇
/loan-article-skill 帮我写发布文章,主题:深圳上班族信用贷
/loan-article-skill 主题:武汉房产二抵,城市:武汉,篇数:3
```

完整触发词见 [`references/triggers.md`](references/triggers.md)。

## 安装

### Claude Code

```bash
# 从 git 仓库安装
git clone <repo-url> ~/.claude/skills/loan-article-skill

# 或从本地复制
cp -R ./loan-article-skill ~/.claude/skills/

# 或跑 install.sh
./install.sh
```

### GitHub Copilot CLI

```bash
./install.sh --platform copilot
# 装到 ~/.copilot/skills/loan-article-skill
```

### Cursor(项目级,无全局路径)

```bash
./install.sh --platform cursor
# 装到 .cursor/skills/loan-article-skill
```

### Codex CLI / OpenCode / Goose / Cline(通用路径)

```bash
./install.sh --platform codex
# 装到 ~/.agents/skills/loan-article-skill
```

### 全部平台

```bash
./install.sh --platform all
```

## 目录结构

```
loan-article-skill/
├── SKILL.md                 # 主入口(必读)
├── AGENTS.md                # AAIF 格式,跨平台 reach
├── README.md                # 本文件
├── install.sh               # 跨平台安装脚本
├── references/
│   ├── company-profile.md   # 聚融网公司档案(可替换)
│   ├── writing-data.md      # 利率/额度/审批数据
│   ├── city-profiles.md     # 32 城画像与受众痛点
│   └── triggers.md          # 触发词与意图识别
├── assets/
│   ├── title-patterns.md    # 5 大角度标题模板
│   └── article-template.md  # 6 段式骨架模板
├── scripts/
│   ├── count_words.py       # 中文字数统计
│   ├── validate_article.py  # 8 项综合校验
│   └── run_evals.py         # 跑评估
└── evals/
    └── loan-article.eval.md # 评估规格(10 BCs + 5 golden cases)
```

## 复用为其他助贷平台

1. 替换 `references/company-profile.md` 里的公司信息
2. 按需更新 `references/writing-data.md` 的利率/额度
3. 调整 `references/city-profiles.md` 的覆盖城市
4. SKILL.md / scripts / assets 不用改

## 跑评估

```bash
python3 scripts/run_evals.py
# 期望输出: ALL PASS: 10/10  VALID
```

## 跑一次完整校验

```bash
# 1. 字数
python3 scripts/count_words.py --file article.md

# 2. 8 项综合
python3 scripts/validate_article.py \
  --file article.md \
  --city 北京 \
  --topic 房产抵押
```

## License

MIT
