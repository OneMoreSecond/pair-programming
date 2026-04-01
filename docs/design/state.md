# AI Pair Programming Workflow State Schema

## 目标

本文定义 pair workflow 的状态文件结构，重点服务以下目标：

- 支持任务恢复
- 支持 CLI 查询
- 支持后续 TUI 展示
- 让 orchestrator 的状态推进有统一存储

第一版建议采用 JSON 文件：`.opencode/pair/state.json`。

## 状态文件职责

状态文件应只记录运行态事实和少量派生信息，不应存储大块日志或完整工件内容。

它主要回答这些问题：

- 当前任务是什么
- 现在执行到哪一轮、哪一个阶段
- 最近一次 review 是什么结论
- 是否可以恢复
- 下一步应做什么

## 顶层结构建议

```json
{
  "version": 1,
  "taskId": "pair-20260401-001",
  "goal": "Implement an AI pair programming workflow",
  "status": "reviewer_running",
  "mode": "semi_auto",
  "currentRound": 2,
  "maxRounds": 3,
  "developerModel": "model-a",
  "reviewerModel": "model-b",
  "testCommand": "pnpm test",
  "createdAt": "2026-04-01T10:00:00Z",
  "updatedAt": "2026-04-01T10:08:00Z",
  "lastReviewStatus": "CHANGES_REQUESTED",
  "resumeFrom": "reviewer",
  "rounds": []
}
```

## 字段说明

### 基础字段

- `version`：状态 schema 版本
- `taskId`：任务唯一标识
- `goal`：用户目标文本
- `status`：当前任务状态
- `mode`：运行模式，如 `auto`、`semi_auto`

### 执行字段

- `currentRound`：当前轮次，从 1 开始
- `maxRounds`：最大轮次
- `developerModel`：developer 使用的模型 ID
- `reviewerModel`：reviewer 使用的模型 ID
- `testCommand`：测试命令，可为空

### 时间字段

- `createdAt`
- `updatedAt`
- 可选增加 `completedAt`

### 派生字段

- `lastReviewStatus`：最近一次 review 结果
- `resumeFrom`：建议恢复起点，如 `developer`、`reviewer`、`test`

## `status` 枚举建议

建议与 `docs/design/workflow.md` 保持一致：

- `initialized`
- `developer_running`
- `developer_completed`
- `testing_running`
- `testing_failed`
- `reviewer_running`
- `changes_requested`
- `approved`
- `waiting_user`
- `failed`
- `cancelled`

## `rounds` 数组结构

建议每个 round 记录最小元数据，而不是整个文件内容：

```json
{
  "round": 1,
  "status": "changes_requested",
  "startedAt": "2026-04-01T10:00:00Z",
  "completedAt": "2026-04-01T10:03:00Z",
  "developerNotePath": ".opencode/pair/rounds/001/developer-note.md",
  "patchPath": ".opencode/pair/rounds/001/patch.diff",
  "testSummaryPath": ".opencode/pair/rounds/001/test-summary.md",
  "reviewPath": ".opencode/pair/rounds/001/review.md",
  "reviewStatus": "CHANGES_REQUESTED",
  "blockingCount": 2
}
```

## 可选增强字段

如果后续需要更强分析能力，可以逐步加入：

- `error`: 最近一次错误摘要
- `warnings`: 非阻塞系统告警
- `environment`: 项目语言、包管理器、仓库信息
- `metrics`: 用于统计轮次耗时、测试次数等

第一版无需一次性全部引入。

## 更新原则

状态文件更新应满足：

- 每次状态变化后立即写盘
- 写入应尽量原子，避免中断导致损坏
- 不要在高频输出中反复写无意义字段

建议 orchestrator 在这些节点更新状态：

- 任务初始化后
- 进入 developer 前后
- 进入测试前后
- 进入 reviewer 前后
- 解析 review 完成后
- 任务结束时

## 恢复时的使用方式

恢复流程可以依赖这些字段：

- `status`
- `currentRound`
- `resumeFrom`
- `rounds`

orchestrator 恢复时需要将状态文件与工件目录交叉校验，不能只相信 `state.json`。

## 示例

一个等待用户介入的状态文件示例：

```json
{
  "version": 1,
  "taskId": "pair-20260401-001",
  "goal": "Implement an AI pair programming workflow",
  "status": "waiting_user",
  "mode": "semi_auto",
  "currentRound": 3,
  "maxRounds": 3,
  "developerModel": "model-a",
  "reviewerModel": "model-b",
  "testCommand": "pnpm test",
  "createdAt": "2026-04-01T10:00:00Z",
  "updatedAt": "2026-04-01T10:12:00Z",
  "lastReviewStatus": "CHANGES_REQUESTED",
  "resumeFrom": "developer",
  "rounds": [
    {
      "round": 1,
      "status": "changes_requested",
      "reviewStatus": "CHANGES_REQUESTED",
      "blockingCount": 2,
      "reviewPath": ".opencode/pair/rounds/001/review.md"
    },
    {
      "round": 2,
      "status": "changes_requested",
      "reviewStatus": "CHANGES_REQUESTED",
      "blockingCount": 1,
      "reviewPath": ".opencode/pair/rounds/002/review.md"
    },
    {
      "round": 3,
      "status": "waiting_user",
      "reviewStatus": "CHANGES_REQUESTED",
      "blockingCount": 1,
      "reviewPath": ".opencode/pair/rounds/003/review.md"
    }
  ]
}
```

该结构已经足以支撑 `status`、`resume` 和简单的历史查看。
