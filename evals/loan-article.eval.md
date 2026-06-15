# Loan Article Generation — Eval Spec

> 为 `loan-article-skill` 设计的回归测试集。
> 二元检查(binary checks) + 5 个 golden cases。
> 可被 `autoresearch-universal` 直接消费(rule 18)。

## 1. 元数据

- **skill**: `loan-article-skill`
- **version**: 1.0.0
- **created**: 2026-06-01
- **loss_function**: 8 项硬性合规 + 字数

## 2. Binary Checks(bash 可执行)

每条检查用 `command` 字段执行,exit 0 = 通过,非 0 = 失败。

| id | description | command |
|----|-------------|---------|
| BC-01 | SKILL.md 存在且含 frontmatter | `[ -f SKILL.md ] && head -1 SKILL.md \| grep -q "^---"` |
| BC-02 | 含 references/company-profile.md | `[ -f references/company-profile.md ]` |
| BC-03 | 含 references/writing-data.md | `[ -f references/writing-data.md ]` |
| BC-04 | 含 references/city-profiles.md | `[ -f references/city-profiles.md ]` |
| BC-05 | 含 assets/title-patterns.md | `[ -f assets/title-patterns.md ]` |
| BC-06 | 含 assets/article-template.md | `[ -f assets/article-template.md ]` |
| BC-07 | count_words.py 可执行 | `python3 scripts/count_words.py --file /dev/null 2>&1; [ $? -ne 2 ]` |
| BC-08 | validate_article.py 可执行 | `python3 scripts/validate_article.py --help 2>&1 \| grep -q "city"` |
| BC-09 | 触发词出现在 SKILL.md | `grep -q "帮我写贷款文章" SKILL.md` |
| BC-10 | 6 段式骨架在 assets | `grep -q "6 段" assets/article-template.md` |
| BC-11 | 含 references/model-config.md 且 SKILL.md 含写作模型确认 | `[ -f references/model-config.md ] && grep -q "写作模型确认" SKILL.md` |

## 3. Golden Cases(input-only,pending-first-green)

每条 golden case 是一个**输入**,配一组**预期输出属性**。
agent 生成文章 → 跑 `validate_article.py` → 全部通过 = case 1 green。

### GC-01 · 北京房产一抵(企业主受众)

- **input**:
  - 主题:房产抵押
  - 城市:北京
  - 受众:企业主
  - 篇数:1
- **expected_output_properties**:
  - 字数 ∈ [1800, 2500]
  - 含「北京」3 次以上
  - 含「房产抵押」≥ 4 次
  - 含 H2 ≥ 3 个
  - 不含任何具体银行名
  - 不含绝对词
  - 末段含 CTA
  - 利率数据使用相对词

### GC-02 · 上海企业转贷(中小企业主)

- **input**:
  - 主题:企业转贷
  - 城市:上海
  - 受众:中小企业主
  - 篇数:1
- **expected_output_properties**:
  - 字数 ∈ [1800, 2500]
  - 含「上海」≥ 3 次
  - 含「转贷」≥ 5 次
  - 出现"高利息换低利息"或"等额本息换先息后本"中的至少 1 个
  - 数据范围在 3%-5% 区间(前几年利率)
  - 不含具体银行名 / 绝对词
  - 末段含 CTA

### GC-03 · 武汉上班族信用贷(年轻白领)

- **input**:
  - 主题:上班族信用贷
  - 城市:武汉
  - 受众:年轻白领
  - 篇数:1
- **expected_output_properties**:
  - 字数 ∈ [1800, 2500]
  - 含「武汉」≥ 3 次
  - 含「信用贷」≥ 4 次
  - 提到"征信"或"查询"
  - 不含具体银行名 / 绝对词
  - 末段含 CTA

### GC-04 · 难批情况(房产证有老人 / 房龄老 / 征信花)

- **input**:
  - 主题:房产抵押
  - 城市:苏州
  - 受众:老房产持有者
  - 篇数:1
- **expected_output_properties**:
  - 字数 ∈ [1800, 2500]
  - 叙事化提到"房龄" / "产权人" / "征信" 中至少 2 个
  - **不**直接列 5 条注意事项(以小标题形式)
  - 不含具体银行名 / 绝对词
  - 末段含 CTA

### GC-05 · 商业房产抵押(商铺)

- **input**:
  - 主题:商业房产抵押
  - 城市:重庆
  - 受众:商铺持有者
  - 篇数:1
- **expected_output_properties**:
  - 字数 ∈ [1800, 2500]
  - 含「重庆」≥ 3 次
  - 提到"商铺"或"商业房产"
  - 利率区间提到 2.7%-3.6%
  - 提到"额度"通常 5-7 成
  - 不含具体银行名 / 绝对词
  - 末段含 CTA

## 4. 评估流程

1. 加载 SKILL.md,按工作流生成 1 篇文章
2. 保存到 `evals/tmp/article_<case_id>.md`
3. 跑:
   ```bash
   python3 scripts/validate_article.py \
     --file evals/tmp/article_<case_id>.md \
     --city <城市> \
     --topic <主题>
   ```
4. 全部 8 项 ✅ → case 1 green
5. 任意 1 项 ❌ → rewrite(最多 3 轮),仍失败 → case 标 red

## 5. 跑 evals

```bash
python3 scripts/run_evals.py
```

脚本会:
- 跑全部 10 条 binary checks
- 对每个 golden case:模拟输入 → 加载 SKILL.md → 生成文章(实际由 agent 执行,脚本只校验产物)
- 输出报告:每条 check 的 pass/fail + 失败原因

## 6. Optimize 提示

跑通全部 evals 后,可用 `autoresearch-universal` 进一步调优:

```bash
autoresearch-universal \
  --skill ~/.claude/skills/loan-article-skill \
  --eval evals/loan-article.eval.md \
  --goal "minimize word_count_violation_rate while keeping compliance > 95%"
```

## 7. 维护

- 利率数据每季度 review 一次(数据可能调整)
- 城市画像随公司覆盖范围变化而更新
- 触发词随用户实际话语习惯调整
