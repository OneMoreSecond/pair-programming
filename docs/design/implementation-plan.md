# AI Pair Programming Workflow MVP Implementation Plan

## 目标

本文将前面的设计文档收敛为一个可执行的 MVP 实施计划，帮助尽快从方案进入实现。

MVP 的目标不是一次性做完整产品，而是验证以下假设：

- 双角色交替比单角色一次性生成更稳
- `review.md` 驱动的修复回路可以在少数轮次内收敛
- 本地 CLI 方式足以支撑早期验证

## MVP 范围

MVP 只包含以下能力：

- 创建 pair task
- 运行 developer -> reviewer 的基本闭环
- 保存 round 工件
- 解析 `review.md` 状态
- 支持 `status` 和 `resume`

MVP 不包含：

- 多 reviewer
- tester 独立角色
- 复杂 TUI
- 远程协作
- 高级策略路由

## 建议实现顺序

### Phase 1: Skeleton

产出目标：

- `opencode pair start`
- 初始化 `.opencode/pair/`
- 生成 `config.json` 和 `state.json`
- 创建 prompt 模板文件

完成标准：

- 用户可以成功启动一个任务
- 目录结构稳定生成

### Phase 2: Developer Loop

产出目标：

- orchestrator 能启动 developer session
- 保存 `developer-note.md`
- 采集 `patch.diff`

完成标准：

- 一轮开发后能稳定得到代码修改和说明文件

### Phase 3: Reviewer Loop

产出目标：

- orchestrator 能启动 reviewer session
- reviewer 输出 `review.md`
- 能解析 `Status`

完成标准：

- 系统可以判断 `APPROVED` 或 `CHANGES_REQUESTED`

### Phase 4: Multi-round Control

产出目标：

- 根据 review 自动或半自动进入下一轮
- 支持最大轮次控制
- 支持 `waiting_user`

完成标准：

- 任务可以在多轮中稳定推进，不会死循环

### Phase 5: Status And Resume

产出目标：

- `opencode pair status`
- `opencode pair resume`
- 基于 `state.json` 恢复执行

完成标准：

- 中途中断后可以继续运行

## 实现模块拆分

建议拆成这些模块：

- `task-init`：创建目录和默认配置
- `state-store`：读写 `state.json`
- `prompt-builder`：拼装 developer / reviewer prompt
- `session-runner`：启动具体模型 session
- `artifact-store`：保存 round 文件
- `review-parser`：解析 `review.md`
- `workflow-engine`：状态推进逻辑
- `cli`：命令入口

这样可以把 prompt、状态机和调用执行解耦，后续更容易替换实现。

## 建议验收用例

MVP 至少要跑通这些用例：

### 用例 1：单轮通过

- developer 完成小修改
- reviewer 直接返回 `APPROVED`
- 任务结束

### 用例 2：两轮收敛

- reviewer 第 1 轮提出 1 到 2 个 blocking issue
- developer 第 2 轮修复
- reviewer 通过

### 用例 3：达到最大轮次

- reviewer 连续要求修改
- 达到轮次上限
- 任务进入 `waiting_user`

### 用例 4：review 格式错误

- reviewer 输出不合法 markdown
- orchestrator 自动重试
- 再失败则进入异常状态

### 用例 5：中断恢复

- 在 reviewer 前或 reviewer 后中断
- 使用 `resume` 成功继续

## 开发节奏建议

建议每个 phase 都带着一个真实任务做回归，而不是只写单元测试。

原因是这个工作流的核心价值在于：

- prompt 是否有效
- 工件是否足够支撑下一轮
- 状态机是否真的可恢复

这些问题只有放到真实任务里才容易暴露。

## 最低技术要求

无论最终使用什么语言实现，MVP 至少需要具备：

- 文件系统读写
- 进程启动与退出码处理
- 模板变量替换
- markdown 文本解析
- 稳定的状态持久化

因此 Node.js 或 Python 都很适合做第一版。

## 风险控制建议

在 MVP 阶段，建议故意保守：

- 不做并发 session
- 不做复杂上下文裁剪
- 不做多角色仲裁
- 不做自动提交 git commit

先保证闭环能稳定收敛，再逐步扩展能力。

## MVP 完成定义

可以用以下标准判断 MVP 是否完成：

- 用户能一条命令启动任务
- 至少一个真实编码任务能在 1 到 3 轮内收敛
- review 结果可稳定解析
- 任务中断后可恢复
- 用户能从 CLI 明确知道当前状态和下一步动作

满足以上标准后，再继续做 TUI、策略优化和高级角色扩展，成功概率会更高。
