# AI Pair Programming Workflow CLI Design

## 目标

本文定义基于 `opencode` 的 pair programming 工作流 CLI 设计，覆盖：

- 顶层命令结构
- 核心命令语义
- 参数设计
- 输出行为
- 失败与恢复入口

CLI 的目标是让用户用少量命令完成启动、观察、恢复和终止整个工作流。

## 设计原则

- 高层命令优先，避免用户拼装复杂参数
- 默认值足够好，常见任务一条命令可启动
- 输出短且稳定，适合终端和后续 TUI 演进
- 命令语义清晰，对应明确状态变化

## 命令总览

建议采用如下命令结构：

```bash
opencode pair start
opencode pair status
opencode pair resume
opencode pair review
opencode pair artifacts
opencode pair stop
opencode pair config
```

第一版不必全部实现，但建议按这个形态设计，避免后续扩展时命名混乱。

## `opencode pair start`

### 作用

创建一个新的 pair task，初始化状态、配置、提示模板，并启动第一轮 developer。

### 典型用法

```bash
opencode pair start --goal "实现一个双 session 的开发-审查工作流"
```

也建议支持从文件读取任务描述：

```bash
opencode pair start --goal-file ./task.md
```

### 推荐参数

- `--goal <text>`：任务目标文本
- `--goal-file <path>`：从文件读取目标
- `--developer-model <id>`：developer 使用的模型
- `--reviewer-model <id>`：reviewer 使用的模型
- `--max-rounds <n>`：最大轮次
- `--test-command <cmd>`：测试命令
- `--auto`：自动推进直到完成或失败
- `--semi-auto`：每轮结束暂停
- `--workdir <path>`：指定工作目录

### 默认行为

若用户只提供 goal，系统应尽量使用默认配置直接启动：

- 使用默认 developer / reviewer 模型
- 最大轮次为 3
- 自动测试开启，如果项目配置可推断测试命令
- 以半自动或保守自动模式运行

## `opencode pair status`

### 作用

展示当前任务状态和最近一轮信息。

### 输出建议

```text
Task: pair-20260401-001
Status: reviewer_running
Round: 2/3
Developer model: model-a
Reviewer model: model-b
Last review status: CHANGES_REQUESTED
Artifacts: .opencode/pair/rounds/002/
```

### 可选参数

- `--json`：结构化输出，便于脚本使用
- `--task-id <id>`：查看指定任务
- `--verbose`：显示更多运行细节

## `opencode pair resume`

### 作用

从当前任务的可恢复状态继续执行。

### 用法示例

```bash
opencode pair resume
opencode pair resume --task-id pair-20260401-001
opencode pair resume --from reviewer
```

### 语义建议

- 默认从 `state.json` 推断最近可恢复阶段
- `--from` 可显式指定从 `developer`、`reviewer` 或 `test` 开始
- 若当前状态不是可恢复状态，应直接提示原因

## `opencode pair review`

### 作用

快速查看最新 `review.md` 或指定轮次的 review。

### 用法示例

```bash
opencode pair review
opencode pair review --round 2
```

### 输出行为

第一版可以直接打印 `review.md` 内容摘要，而不是完整长文。

推荐至少展示：

- `Status`
- blocking issue 数量
- blocking issue 列表
- review 文件路径

## `opencode pair artifacts`

### 作用

列出当前任务或某一轮的工件文件，帮助用户快速定位。

### 用法示例

```bash
opencode pair artifacts
opencode pair artifacts --round 1
```

### 输出建议

```text
rounds/002/developer-note.md
rounds/002/patch.diff
rounds/002/test-summary.md
rounds/002/review.md
```

后续也可以扩展为 `--open review` 之类的快捷能力，但第一版不是必需。

## `opencode pair stop`

### 作用

停止当前任务并将状态设置为 `cancelled`。

### 语义建议

- 不删除任何已有工件
- 明确记录终止原因和终止时间
- 后续允许用户重新 `resume` 或基于该任务新开分支任务

## `opencode pair config`

### 作用

查看或调整 pair 工作流默认配置。

### 可管理项

- developer 默认模型
- reviewer 默认模型
- 默认最大轮次
- 默认测试命令
- 默认运行模式
- review 协议版本

第一版可以只支持查看，不急于支持复杂的交互式编辑。

## 参数优先级

配置来源建议按以下优先级覆盖：

1. 命令行参数
2. 任务级 `config.json`
3. 项目级默认配置
4. 系统默认值

这样可以保证单次任务的临时需求不会污染全局默认行为。

## 输出风格建议

CLI 输出应区分三类：

### 1. 进度输出

例如：

```text
Initializing pair task...
Round 1: Developer running
Round 1: Tests passed
Round 1: Reviewer complete (CHANGES_REQUESTED)
```

### 2. 状态输出

例如：

```text
Status: waiting_user
Reason: repeated blocking issue
Next action: opencode pair review
```

### 3. 摘要输出

例如：

```text
Pair workflow completed in 2 rounds
Final status: APPROVED
Final review: .opencode/pair/rounds/002/review.md
```

## 退出码建议

为了后续脚本化集成，建议使用稳定退出码：

- `0`：成功完成或成功执行查询命令
- `1`：通用错误
- `2`：配置错误或参数非法
- `3`：任务进入 `waiting_user`
- `4`：任务失败且不可自动恢复

第一版不一定全部对外公开，但内部实现应尽量稳定。

## 第一版优先实现建议

最小可用命令集建议为：

1. `opencode pair start`
2. `opencode pair status`
3. `opencode pair resume`
4. `opencode pair review`

只要这四个命令稳定，用户就能完成完整闭环。
