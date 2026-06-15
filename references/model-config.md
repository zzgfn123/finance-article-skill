# 写作模型配置(Writing Model Config)

> **重要**:本文件里的 `[WRITING_MODEL]` 和 `[MODEL_SWITCH_COMMAND]` 是占位符。
> clone 后请按下方「四、配置步骤」把它们替换成你实际使用的模型与切换指令(各平台速查见第三节)。
> 这个文件可被任意平台/模型替换 —— SKILL.md 在文章写作前(第 1.5 步)读取本文件,
> 决定是提示用户配置(首次)、还是提示是否切换模型(已配置),并在写完后提示切回原模型。

## 一、配置字段

| 字段 | 占位符 | 含义 | 示例 |
|------|--------|------|------|
| 写作模型名 | `[WRITING_MODEL]` | 用于写文章的指定模型名称 | glm-5.2 / gpt-4o / claude-3.7-sonnet 等 |
| 切换指令 | `[MODEL_SWITCH_COMMAND]` | 在当前平台切换到该模型需执行的指令 | `/model glm-5.2` / `/model gpt-4o` 等 |

## 二、配置检测规则(SKILL.md 据此判定「首次/已配置」)

- 两个字段**仍为占位符**(即文件中仍出现 `[WRITING_MODEL]` 或 `[MODEL_SWITCH_COMMAND]`)→ **视为「未配置」**:
  - 文章写作前会给出**首次配置提示**,并允许用户选择「跳过,用当前模型继续」。
- 两个字段**均已替换**(文件中不再出现上述任一占位符)→ **视为「已配置」**:
  - 文章写作前只提示「是否切换到 `{写作模型名}` 写作?」,不再重复配置流程。

## 三、各平台模型切换指令速查(参考,按你实际使用的平台填写)

| 平台 | 切换指令格式 | 示例 |
|------|------------|------|
| Claude Code / ZCode | `/model <模型名>` | `/model glm-5.2` |
| Cursor | 设置面板 → Models → 选择模型(或命令面板搜 `Model`) | GUI 操作 |
| GitHub Copilot CLI | `gh copilot` 会话内通过配置指定 | 见官方文档 |
| Codex CLI / OpenCode | `config set model <模型名>` 或启动参数 | `config set model gpt-4o` |
| Goose | `~/.config/goose/config.yaml` 中 `GOOSE_MODEL` 字段 | `GOOSE_MODEL: gpt-4o` |
| Cline / Roo Code | 插件顶部模型下拉框 | GUI 操作 |

> 若你的平台不在表中,请填入该平台实际可用的切换方式(GUI 操作也可直接文字描述,如「右上角模型下拉框选 glm-5.2」)。

## 四、配置步骤(首次)

1. 确定你要用于文章写作的模型名(如 `glm-5.2`)。
2. 确定在当前平台切换到该模型的指令(参考第三节速查)。
3. 把本文件中:
   - `[WRITING_MODEL]` 全局替换为你的模型名;
   - `[MODEL_SWITCH_COMMAND]` 全局替换为对应的切换指令。
   - 例如(Linux/macOS):
     ```bash
     sed -i 's/\[WRITING_MODEL\]/glm-5.2/g; s/\[MODEL_SWITCH_COMMAND\]/\/model glm-5.2/g' references/model-config.md
     ```
     或 Windows PowerShell:
     ```powershell
     (Get-Content references/model-config.md) -replace '\[WRITING_MODEL\]','glm-5.2' -replace '\[MODEL_SWITCH_COMMAND\]','/model glm-5.2' | Set-Content references/model-config.md
     ```
4. 替换后回到 agent,回复「已配置」即可继续。

## 五、写作流程中的模型切换行为(由 SKILL.md 执行)

```
[标题阶段完成后 · 第 1.5 步]
├─ 读取本文件,检测占位符
├─ 未配置? → 输出首次配置提示 + 「跳过/已配置」二选一
│    └─ 用户「跳过」→ 直接进写作循环(当前模型)
│    └─ 用户「已配置」→ 重新读取本文件,走已配置分支
└─ 已配置? → 输出「是否切换到 [WRITING_MODEL]?1)切换 2)继续」
     └─ 选 1 → 提示执行 [MODEL_SWITCH_COMMAND],等用户回复「已切换」→ 进写作循环
     └─ 选 2 → 直接进写作循环(当前模型)

[写作循环 + 字数/合规校验(含失败重写)全程在选定模型下完成,不重复切换]

[第 4 步输出前] → 若此前执行过切换,输出「写作完成,请切回写作前使用的模型」提示
```

## 六、注意事项

- 模型切换**由用户手动执行**,skill 只负责给出明确的指令提示并等待确认。
- 若用户选择跳过(未配置)或选择「继续」(不切换),**不阻塞流程**,用当前模型写作。
- skill 不记录「原模型名」,故写完后只能提示「请切回写作前使用的模型」,不能给出具体的切回指令。
- 本文件是手填配置,需纳入版本控制作为模板,**不要**加入 `.gitignore`。
