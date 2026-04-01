# AI Pair Programming Workflow Architecture

## 目标

本方案希望在 `opencode` 之上构建一个可重复执行的双角色协作机制：

- `developer` 负责实现和修改代码
- `reviewer` 负责审查本轮改动并输出结构化意见
- `orchestrator` 负责轮次调度、上下文组装、工件落盘和状态推进

系统目标不是模拟两个人持续对话，而是建立一个稳定的工程回路：实现、审查、修复、收敛。

## 非目标

- 不追求两个 session 实时并发协作
- 不要求 reviewer 直接修改代码
- 不在第一版解决多 reviewer 共识、复杂分支管理或远程协作
- 不依赖长上下文记忆作为工作流正确性的基础

## 架构总览

```text
User
  |
  v
Orchestrator
  |-- prepares context
  |-- launches developer session
  |-- captures artifacts and diff
  |-- launches reviewer session
  |-- parses review status
  `-- decides continue / stop / ask user

Shared Workspace
  |-- source files
  |-- git diff
  `-- .opencode/pair artifacts

Developer Session
  |-- reads task + review feedback
  |-- edits code
  `-- writes developer-note.md

Reviewer Session
  |-- reads task + diff + developer note
  `-- writes review.md
```

## 核心组件

### Orchestrator

orchestrator 是整个系统的控制平面，负责：

- 创建任务目录和轮次目录
- 保存运行时配置和状态
- 为 developer 和 reviewer 构造输入上下文
- 串行启动两个 session
- 收集代码差异、测试结果和产出文件
- 解析 `review.md` 顶部状态字段
- 决定继续下一轮、结束，或进入人工介入状态

第一版建议把 orchestrator 实现成一个本地 CLI 子命令，而不是常驻服务。

### Developer Session

developer session 的职责是面向当前任务做实现，不做最终审批。

输入应包括：

- 用户目标
- 当前代码工作区
- 上一轮 reviewer 意见
- 本轮执行约束
- 需要关注的文件或 diff

输出应包括：

- 实际代码修改
- `developer-note.md`
- 可选的测试结果摘要

### Reviewer Session

reviewer session 的职责是只读审查，不改代码。

输入应包括：

- 用户目标
- 本轮代码 diff
- `developer-note.md`
- 审查约束和输出模板

输出应包括：

- `review.md`
- 顶部稳定的 `Status` 字段
- blocking / non-blocking 分类意见

### Shared Workspace

developer 和 reviewer 共用同一份工作区，但需要满足以下约束：

- 任一时刻只允许一个 session 写入
- reviewer 默认只读
- orchestrator 负责在角色切换时采样 diff 和工件

第一版最简单可靠的方式是：所有角色都运行在同一工作区，依赖串行调度避免冲突。

## 数据与工件设计

建议在仓库内维护统一工作流目录：

```text
.opencode/
  pair/
    state.json
    config.json
    prompts/
      developer.md
      reviewer.md
    rounds/
      001/
        developer-note.md
        review.md
        patch.diff
        test-summary.md
      002/
        ...
```

### `state.json`

记录运行态信息，便于恢复和 TUI 展示。建议字段：

```json
{
  "taskId": "pair-20260331-001",
  "goal": "...",
  "status": "review_running",
  "currentRound": 2,
  "maxRounds": 4,
  "developerModel": "...",
  "reviewerModel": "...",
  "lastReviewStatus": "CHANGES_REQUESTED"
}
```

### `config.json`

记录任务静态配置，避免恢复时丢失策略参数：

- 模型选择
- 是否自动运行测试
- 最大轮次
- 是否只修复 blocking issues
- reviewer 每轮最多输出几个 blocking issues

### 轮次目录

每一轮目录是最重要的可审计单元，应尽量完整保存：

- 输入摘要
- 代码差异
- developer 说明
- reviewer 结论
- 测试摘要

## 控制流设计

整体控制流为严格串行：

1. orchestrator 准备 round 上下文
2. 启动 developer session
3. 收集代码变更和开发说明
4. 可选执行测试
5. 启动 reviewer session
6. 解析 `review.md`
7. 决定结束、下一轮，或等待用户

这种设计牺牲了一部分速度，但换来：

- 更简单的并发模型
- 更稳定的工件边界
- 更易恢复和调试

## 为什么采用工件驱动架构

相比让两个 session 直接互相传递自然语言上下文，工件驱动方案有几个优势：

- 结果可追踪，便于复盘
- 角色边界更清晰
- 上下文长度可控
- 失败后更容易恢复到最近一轮
- 更适合后续接入自动测试、策略引擎和 UI 展示

## 模型角色分工

系统允许 developer 和 reviewer 使用不同模型，原因包括：

- developer 更适合代码生成和局部推理能力强的模型
- reviewer 更适合稳定、保守、擅长结构化输出的模型
- 可通过角色分工降低单一模型同时充当作者和裁判带来的偏差

第一版无需做复杂的模型仲裁，只需要在配置层支持按角色分别指定模型。

## 约束与安全边界

### 写入边界

- developer 可以修改代码和工作流工件
- reviewer 只允许写 `review.md` 及可选审查摘要文件
- orchestrator 负责写状态文件

### 审查边界

- reviewer 默认只审查本轮 diff 和相关文件
- reviewer 不应对整个仓库发散式点评
- reviewer 需要优先指出 correctness、test coverage 和 requirement fit 问题

### 停机边界

当出现以下情况时，orchestrator 应停止自动推进：

- reviewer 输出无法解析
- developer 未产生有效修改但 reviewer 仍请求修复
- 连续多轮重复同类 blocking issue
- 达到最大轮次
- 测试或权限错误导致流程无法自动恢复

## 可扩展点

该架构后续可以平滑扩展：

- 增加 `tester` 角色
- 增加多个 reviewer 并做结果聚合
- 把 `state.json` 接入 TUI 实时展示
- 支持从特定 round 恢复
- 支持将 `review.md` 自动转成结构化 JSON

## 第一版实现建议

建议按以下顺序落地：

1. 单仓库本地运行
2. 单 developer + 单 reviewer + 单 orchestrator
3. 轮次目录落盘
4. 固定 `review.md` 协议
5. 可选测试命令
6. `resume` 和 `status` 能力

这样可以先验证核心闭环是否收敛，再继续增强体验与策略能力。
