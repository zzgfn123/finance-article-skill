## 改了什么

<!-- 用一句话说清楚这个 PR 改了什么 -->

## 为什么改

<!-- 解决了什么问题 / 加了什么能力 / 修了什么 bug -->

## 怎么测

<!-- 让 reviewer 能验证你的改动是可工作的 -->

- [ ] 本地跑了 `python3 scripts/run_evals.py`,结果 10/10 通过
- [ ] 如果改了 `references/` 下的数据,跑了 `python3 scripts/validate_article.py --file <新文章> --city <城市> --topic <主题>` 8/8 通过
- [ ] 如果改了 `SKILL.md` / `AGENTS.md`,本地试了一次 `/loan-article-skill ...` 触发词

## Checklist

- [ ] 没用绝对词(最好 / 第一 / 100% / 唯一 / 稳过 / 包过)
- [ ] 没出现具体银行名(中国银行 / 招商银行 / 工商银行 ...)
- [ ] 没在 SKILL.md / AGENTS.md / README.md 出现具体公司名(品牌用 `[BRAND_NAME]`)
- [ ] 没引入新的 Python 依赖(如有,加到 README 的依赖说明里)
- [ ] 没删除任何 references/ 下文件
- [ ] 改了文档(README / SKILL.md / AGENTS.md),对应章节同步更新

## 关联 Issue

<!-- 关闭 / 关联哪个 issue,如 Closes #12 / Refs #34 -->

## 影响范围

<!-- 哪些文件被改了,改的程度(新增/修改/删除) -->

## 截图 / 示例输出(如有)

<!-- 如果改了 UX 或新增了 eval case,贴一张截图或示例输出 -->
