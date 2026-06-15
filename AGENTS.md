# AGENTS.md — loan-article-skill (AAIF format)

> Companion instruction file for tools that read `AGENTS.md` over `SKILL.md`
> (Codex CLI, Augment, Continue.dev, Zed, Goose, OpenCode, etc.).

## Purpose

Generate 1800-2500 word SEO articles for a Chinese loan-consulting platform
(brand-agnostic — `references/company-profile.md` holds the brand profile;
the [BRAND_NAME] placeholder in code/docs is to be replaced by the actual
brand name), targeted at city-specific audiences (一线 vs 二线 vs 其他), on
topics like:

- 房产抵押贷款 / 房产二次抵押
- 企业经营贷 / 开票贷 / 纳税贷
- 上班族信用贷
- 商业房产抵押(商铺/写字楼/厂房)

## Activation Triggers

Activate this skill when the user says any of:

- 「帮我写贷款文章」
- 「帮我写关于 [城市] 的文章」
- 「帮我写发布文章」
- 「/loan-article-skill ...」

If only a topic or city is provided, ask for the missing one with a 5-item
quick-pick menu (city list in `references/city-profiles.md`, topics in
`assets/title-patterns.md`).

## Required Reading Before Generating

1. `references/company-profile.md` — current company profile (replaceable)
2. `references/writing-data.md` — rate/LTV rules by city tier
3. `references/city-profiles.md` — 32-city audience profiles
4. `references/model-config.md` — writing model config (model name + switch command placeholders)
5. `assets/title-patterns.md` — 5-angle title patterns
6. `assets/article-template.md` — 6-section article skeleton

## Hard Constraints (any violation = rewrite)

1. **No specific bank names** — use 「五大行」「股份制银行」「地方性商业银行」 etc.
2. **No absolute words** — 「最好 / 第一 / 唯一 / 100% / 绝对下款」 are banned.
3. **Strong keyword relevance** — core topic keyword must appear in title,
   opening sentence, an H2, and the closing paragraph.
4. **City-specific** — city name must appear in title, opening, and closing;
   audience pain points must be derived from city tier.
5. **1800-2500 words** — verified by `scripts/count_words.py` per article.
6. **Compliance** — writer is a 「咨询服务方」, never a 「放贷方」.
   Soft CTA at the end of every article.

## Workflow (per invocation)

1. Parse input → ask for missing city/topic with quick-pick menus.
2. If no title provided → generate 5 title candidates across 5 angles, ask user to pick.
3. **Writing-model confirmation (run once before the writing loop):**
   - Read `references/model-config.md`.
   - **Not configured** (still contains `[WRITING_MODEL]` or `[MODEL_SWITCH_COMMAND]`
     placeholder): output a first-time setup hint (replace both placeholders in
     `model-config.md`, then reply "已配置"), and offer a "skip, keep current model"
     option. Do **not** start writing until the user responds.
   - **Configured**: output "Switch to `[WRITING_MODEL]` for writing? 1) switch —
     please run `[MODEL_SWITCH_COMMAND]` and reply '已切换'; 2) keep current model."
     Do **not** start writing until the user responds.
   - The model switch is executed by the user in their current platform; the skill only
     emits the explicit instruction and waits for confirmation. Skipping or declining
     never blocks the flow. Remember whether a switch happened in this invocation.
4. For each of N articles (N=5 default, or user-specified):
   a. Build 6-section outline using `assets/article-template.md`.
   b. Write 1820-2500 Chinese characters following the skeleton.
   c. Run `python3 scripts/count_words.py` → must be in [1800, 2500].
   d. Run `python3 scripts/validate_article.py --file <path> --city <X> --topic <Y>` → all 8 checks must pass.
   e. If any check fails → rewrite that section (max 3 rounds), then escalate to user.
   The whole writing loop + validation/rewrite (steps 4a–4e) runs under whichever model
   was selected in step 3; do not switch again mid-loop.
5. **Before output:** if a model switch happened in step 3, emit a switch-back prompt
   ("All articles done. Please switch back to the model you used before writing.").
   The skill does not record the original model name, so it can only prompt the user to
   switch back manually.
6. Deliver as a single markdown bundle with per-article metadata header.

## Output Format

Each article must include a header line:

```
## 第 N 篇 · 《<标题>》
字数: <N> 字 | 关键词: <3 个> | 合规: ✅
---
<正文 markdown>
---
```

Final bundle includes a summary block (total words, keyword coverage,
compliance status, recommended publishing platforms).

## Cross-Platform Compatibility

This skill is invoked the same way on:
- Claude Code (`/loan-article-skill`)
- GitHub Copilot
- Cursor / Windsurf / Trae (via format-adapted `.mdc`/`.md` rules)
- Gemini CLI / Codex CLI / OpenCode / Goose / Cline / Roo Code
- Universal agents reading `~/.agents/skills/`

See `README.md` for installation paths per platform.

## Customization

To repurpose for another loan-consulting platform:

1. Replace `references/company-profile.md` with the new platform's profile.
2. Update `references/writing-data.md` if rate ranges differ (keep relative wording).
3. Update `references/city-profiles.md` if coverage is different.
4. The `SKILL.md` body and `scripts/` do not need to change — they reference
   the references/ files dynamically.
