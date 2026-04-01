# AI Pair Programming Workflow Protocol

## 目标

本文定义 developer、reviewer 和 orchestrator 之间的最小交互协议，重点覆盖：

- prompt 结构
- 工件格式
- `review.md` 解析规则
- 角色约束

协议的目标是降低多模型协作中的歧义，避免 session 间依赖隐式上下文。

## 设计原则

- 协议优先于自由对话
- 工件优先于长上下文
- 人类可读，同时便于程序解析
- 约束 reviewer 输出，降低噪声和发散

## 工件清单

每一轮建议至少产生以下文件：

- `developer-note.md`
- `patch.diff`
- `review.md`
- `test-summary.md`（可选）

这些文件构成下一轮输入的最小闭环。

## developer 输入协议

developer 每轮应收到结构化输入，而不是单段自然语言。建议组织为以下部分：

```md
# Task
<user goal>

# Round Context
- Round: 2
- Max rounds: 4
- Focus: fix blocking issues first

# Previous Review
<contents of last review.md>

# Relevant Diff Or Files
<selected diff or file list>

# Constraints
- You are the developer.
- Modify code and related artifacts only.
- Do not approve your own work.
- Write developer-note.md at the end.
```

### developer 角色约束

developer prompt 应明确约束：

- 负责实现，不负责最终裁决
- 优先修复 blocking issues
- 不要引入与目标无关的大范围重构
- 若 reviewer 的意见不合理，可以在 `developer-note.md` 说明，但仍需尽量回应
- 若需要补测试，应优先补与本轮改动相关的测试

## developer-note.md 规范

建议格式：

```md
# Developer Note

## Goal
<what this round tried to achieve>

## Changes Made
- ...
- ...

## Tests
- Passed: ...
- Failed: ...
- Not run: ...

## Notes For Reviewer
- ...
```

该文件的用途：

- 给 reviewer 快速建立本轮修改意图
- 帮助 orchestrator 向用户展示摘要
- 为后续 round 保留解释链路

## reviewer 输入协议

reviewer 输入建议采用如下结构：

```md
# Task
<user goal>

# Review Scope
- Review only the current round diff and directly related files.
- Prioritize correctness, regressions, test coverage, and requirement fit.

# Developer Note
<contents of developer-note.md>

# Test Summary
<contents of test-summary.md if any>

# Patch Diff
<contents of patch.diff>

# Constraints
- You are the reviewer.
- Do not edit code.
- Output only the review markdown file in the required format.
- Limit blocking issues to the most important ones.
```

### reviewer 审查优先级

reviewer 应优先关注：

1. 需求是否真正满足
2. 是否引入明显 bug 或回归
3. 边界条件是否未覆盖
4. 测试是否缺失或无效
5. 可维护性问题是否会影响后续演进

reviewer 不应把主要篇幅花在低价值风格建议上。

## review.md 规范

`review.md` 是整个工作流最关键的协议文件，必须同时满足：

- 人可读
- 机可解析
- 对下一轮 developer 可执行

建议格式：

```md
# Review Result
Status: CHANGES_REQUESTED

## Blocking
- `src/foo.ts:42` Null input crashes the command path.

## Non-blocking
- Consider renaming `x` to `sessionState` for clarity.

## Suggested Fix Plan
1. Guard against null input before calling `parseTask()`.
2. Add a regression test for the empty input path.

## Summary
The implementation is close, but one correctness issue and one missing regression test still block approval.
```

通过时：

```md
# Review Result
Status: APPROVED

## Blocking
- None.

## Non-blocking
- None.

## Summary
The implementation matches the goal and the current test coverage is sufficient for this scope.
```

## `review.md` 解析规则

orchestrator 第一版只需要解析最少字段：

- 顶部一级标题存在
- `Status:` 存在且值为 `APPROVED` 或 `CHANGES_REQUESTED`
- `## Blocking` 存在
- `## Summary` 存在

### 状态解析建议

可采用宽松策略：

- 忽略大小写与前后空格
- 只取第一处 `Status:`
- 如果 status 非法，则视为解析失败

### 解析失败处理

若 `review.md` 缺少必要字段：

1. reviewer 阶段自动重试一次
2. 若仍失败，任务进入 `waiting_user` 或 `failed`

## patch.diff 规范

`patch.diff` 推荐由 orchestrator 统一生成，而不是让 developer 自己描述，原因是：

- 可减少模型遗漏
- diff 来源更稳定
- reviewer 输入更客观

推荐内容：

- 当前 round 相对于上一稳定点的 diff
- 若 round 过大，可做裁剪，但应保留完整文件路径和上下文

## test-summary.md 规范

建议采用简洁格式：

```md
# Test Summary

## Command
pnpm test

## Result
FAILED

## Notes
- 2 tests failed
- 1 new test added in `src/foo.test.ts`
```

该文件主要服务 reviewer 和用户，而不是严格机读。

## Prompt 模板管理

建议将 prompt 模板文件化保存在：

```text
.opencode/pair/prompts/developer.md
.opencode/pair/prompts/reviewer.md
```

好处包括：

- 便于版本管理
- 便于按项目定制
- 便于后续 A/B 测试不同 prompt 策略

## 版本化建议

建议在协议文档和状态文件中引入简单版本号，例如：

- `protocolVersion: 1`
- `promptVersion: 1`

这样后续修改 `review.md` 格式或 prompt 结构时，可以逐步兼容旧任务。

## 第一版协议边界

第一版不需要：

- 复杂 JSON schema 输出
- 多文件多格式审查报告
- reviewer 与 developer 直接消息互发
- 过度严格的 AST 级验证

先保证 markdown 协议稳定，再考虑更强的结构化输出。
