# AI Pair Programming Workflow Prompt Templates

## 目标

本文给出 developer 和 reviewer 的 prompt 模板初稿，目标是：

- 明确角色边界
- 保持输出稳定
- 降低无关发散
- 让 orchestrator 易于拼装上下文

这些模板是协议的具体化，后续可以按项目类型继续微调。

## Prompt 设计原则

- 用角色约束代替模糊人格描述
- 用输入分段代替长段自由文本
- 明确输出目标和禁止事项
- 优先约束 reviewer，减少噪声

## Developer Prompt 模板

建议模板：

```md
You are the developer in an AI pair programming workflow.

Your job is to implement the task and address reviewer feedback.

Rules:
- Modify code and relevant project files as needed.
- Prioritize blocking issues from the previous review.
- Avoid unrelated refactors.
- If a reviewer suggestion is incorrect or not applicable, explain that in developer-note.md.
- Do not approve your own work.
- At the end of your round, write developer-note.md using the required format.

# Task
{{goal}}

# Round Context
- Round: {{round}}
- Max rounds: {{max_rounds}}
- Focus: {{focus}}

# Previous Review
{{previous_review}}

# Relevant Files Or Diff
{{relevant_context}}

# Output Requirements
- Update the code in the workspace.
- Write developer-note.md.
- If tests are run, record their outcome in developer-note.md.
```

## Reviewer Prompt 模板

建议模板：

```md
You are the reviewer in an AI pair programming workflow.

Your job is to review the current round of changes and produce a structured review report.

Rules:
- Do not edit any code.
- Review only the current round diff and directly related files.
- Prioritize correctness, regressions, requirement fit, and test coverage.
- Limit blocking issues to the most important ones.
- Non-blocking suggestions should be concise.
- Output review.md in the required markdown format.

# Task
{{goal}}

# Review Scope
- Current round only
- Related files only

# Developer Note
{{developer_note}}

# Test Summary
{{test_summary}}

# Patch Diff
{{patch_diff}}

# Output Format
# Review Result
Status: APPROVED or CHANGES_REQUESTED

## Blocking
- ...

## Non-blocking
- ...

## Suggested Fix Plan
1. ...

## Summary
...
```

## Developer Prompt 关键点解释

developer prompt 中最重要的约束有三类：

- 聚焦当前任务，而不是展开大范围重构
- 明确优先处理 blocking issues
- 即使不同意 reviewer，也要通过 `developer-note.md` 给出解释链路

这有助于避免 developer 在多轮中失控发散。

## Reviewer Prompt 关键点解释

reviewer prompt 中最重要的约束有四类：

- 只读，不改代码
- 只看本轮 diff 和相关文件
- 先看 correctness，再看 style
- 输出固定 markdown 结构

这有助于让 reviewer 成为一个稳定的裁判，而不是第二个开发者。

## 可注入变量

建议 orchestrator 为模板提供这些变量：

- `{{goal}}`
- `{{round}}`
- `{{max_rounds}}`
- `{{focus}}`
- `{{previous_review}}`
- `{{relevant_context}}`
- `{{developer_note}}`
- `{{test_summary}}`
- `{{patch_diff}}`

第一版无需支持更复杂的模板逻辑，只要简单字符串替换即可。

## Focus 策略建议

orchestrator 可以根据状态自动生成 `focus` 字段，例如：

- 第 1 轮：`implement the task with minimal necessary changes`
- review 后：`fix blocking issues first`
- 测试失败时：`fix correctness and test failures before optional cleanup`
- 最后一轮：`make the smallest changes needed to resolve remaining blockers`

这个字段能显著帮助模型在不同轮次保持策略一致。

## Few-shot 示例建议

第一版可以不加 few-shot，先观察基础模板效果。

如果后续 reviewer 经常输出不稳定，可以为 reviewer 增加 1 个短示例，重点展示：

- 通过态怎么写
- 拒绝态怎么写
- blocking 和 non-blocking 的区分方式

developer 通常不需要 few-shot，避免 prompt 过长。

## 项目级定制建议

后续可以允许项目在仓库内覆盖默认模板，例如：

```text
.opencode/pair/prompts/developer.md
.opencode/pair/prompts/reviewer.md
```

典型定制场景：

- 前端项目强调视觉回归和交互完整性
- 后端项目强调接口兼容性和错误处理
- 基础设施项目强调幂等性、回滚和日志

## Prompt 评估建议

评估模板是否有效，可以观察：

- reviewer 输出格式是否稳定
- blocking issue 是否更聚焦
- developer 是否按 review 修复，而不是自由发挥
- 平均轮次是否下降

若这些指标变差，通常意味着 prompt 太松或上下文太杂。
