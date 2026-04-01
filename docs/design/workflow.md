# AI Pair Programming Workflow And State Machine

## 目标

本文定义 pair programming 工作流的轮次流转、状态机、停止条件和恢复策略，保证 orchestrator 的行为可预测、可恢复、可解释。

## 顶层流程

单次任务的主流程如下：

```text
start
  -> initialize task
  -> run developer
  -> capture diff and artifacts
  -> run tests (optional)
  -> run reviewer
  -> parse review result
  -> approved ? finish : next round
```

工作流必须满足两个原则：

- 严格串行，避免 developer 和 reviewer 同时写工作区
- 每个阶段完成后立即落盘，保证中断后可恢复

## 轮次定义

一个 round 由以下步骤构成：

1. 组装 developer 输入
2. developer 修改代码并输出 `developer-note.md`
3. orchestrator 采集 `patch.diff`
4. 可选运行测试并保存 `test-summary.md`
5. 组装 reviewer 输入
6. reviewer 输出 `review.md`
7. orchestrator 解析状态并决定下一步

一个 round 的结束标志是：`review.md` 已成功生成并被解析。

## 状态机

建议维护如下任务状态：

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

推荐状态流转：

```text
initialized
  -> developer_running
  -> developer_completed
  -> testing_running
  -> reviewer_running
  -> changes_requested -> developer_running
  -> approved
```

异常路径：

- 任一步骤遇到不可恢复错误，可进入 `failed`
- 需要人工决定时进入 `waiting_user`
- 用户主动停止时进入 `cancelled`

## 状态转移条件

### `initialized -> developer_running`

条件：

- 配置完成
- 工作目录可访问
- 所需 prompt 已准备

### `developer_running -> developer_completed`

条件：

- developer session 正常结束
- `developer-note.md` 存在

如果 developer 没写 note，但产生了修改，第一版可以允许 orchestrator 自动补一份最小摘要；长期仍建议保持 note 必填。

### `developer_completed -> testing_running`

条件：

- 任务配置启用了自动测试
- 存在可执行测试命令

若未启用测试，可直接进入 `reviewer_running`。

### `testing_running -> reviewer_running`

条件：

- 测试执行结束，无论成功或失败，都要保留摘要并进入 reviewer 阶段

原因是 reviewer 需要感知测试结果，判断失败是否来自合理改动、环境问题或真实缺陷。

### `reviewer_running -> approved`

条件：

- 成功解析 `review.md`
- `Status: APPROVED`

### `reviewer_running -> changes_requested`

条件：

- 成功解析 `review.md`
- `Status: CHANGES_REQUESTED`

### `changes_requested -> developer_running`

条件：

- 当前轮次未达上限
- review 可解析
- 未触发人工介入策略

### `changes_requested -> waiting_user`

建议触发条件：

- 达到最大轮次
- reviewer 连续两轮提出相同 blocking issue
- developer 本轮没有有效改动
- review 内容无法映射到明确修复动作

### 任意状态 -> `failed`

建议触发条件：

- session 启动失败
- 工作区不可写
- 状态文件损坏且无法恢复
- reviewer markdown 无法生成或无法解析且重试失败

## 停止条件

系统应在以下任一条件满足时结束自动循环：

- reviewer 返回 `APPROVED`
- 达到最大轮次
- 用户取消
- 出现不可恢复错误

为了避免无意义循环，建议增加两个保护条件：

- 相同 blocking issue 连续出现阈值
- 最小进展检测失败阈值

## 最小进展检测

为防止 developer 在多轮中重复提交低价值修改，orchestrator 可以维护简单的进展指标：

- 本轮是否产生新的 diff
- blocking issue 数量是否下降
- 测试失败数量是否下降
- reviewer 是否认可上轮问题已解决

如果连续两轮没有明显进展，应切到 `waiting_user`。

## 恢复策略

恢复能力是该工作流的关键设计点。建议支持：

- 从任务级恢复：`resume current task`
- 从轮次级恢复：`resume from round N`
- 从状态级恢复：例如重新执行 reviewer 阶段

恢复时，orchestrator 应：

1. 读取 `state.json`
2. 校验 round 目录和关键工件是否存在
3. 判断最近已完成的稳定阶段
4. 从最近一个可重入阶段继续

可重入性建议如下：

- developer 阶段可重跑，但需要提醒可能覆盖新改动
- reviewer 阶段天然更适合重跑
- 测试阶段可安全重跑

## 用户介入点

系统至少应支持以下介入点：

- 在 round 之间暂停
- 修改 `review.md` 后再继续
- 更换下一轮 developer 或 reviewer 模型
- 调整最大轮次
- 跳过 non-blocking issues

因此 orchestrator 不应把状态推进完全写死成黑盒，而要保留显式的暂停和恢复命令。

## 推荐策略参数

第一版建议默认参数：

- 最大轮次：`3`
- reviewer 每轮最多 blocking issue：`3`
- 连续无进展阈值：`2`
- review 解析失败重试：`1`
- 默认自动测试：开启，但允许关闭

这些参数的目标是让流程尽快收敛，而不是追求无限自动化。

## 一个完整轮次示例

```text
Task initialized
Round 1: developer_running
Round 1: developer_completed
Round 1: testing_running
Round 1: reviewer_running
Round 1: changes_requested
Round 2: developer_running
Round 2: developer_completed
Round 2: reviewer_running
Round 2: approved
Task completed
```

这个流程体现了该状态机的核心特性：每一步都可追踪，每一轮都有明确产物，每次转移都有稳定依据。
