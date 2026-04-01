# AI Pair Programming Workflow UX

## 目标

- 让用户用最少的指令启动一轮 "开发 - 审查 - 修复" 协作流程。
- 让每一轮的状态、产出和下一步动作都清晰可见。
- 降低多 agent 工作流的不确定感，避免用户不知道当前是谁在执行、为什么卡住、下一步会发生什么。

## 核心体验原则

### 1. 单线程协作，状态明确

虽然底层由两个 session 交替执行，但界面上始终只突出一个当前角色：

- `Developer running`
- `Reviewer running`
- `Waiting for user`
- `Completed`

用户不需要理解底层调度细节，只需要知道当前是谁在工作、已经产出了什么。

### 2. 以工件为中心，而不是以对话为中心

用户看到的核心不应是两段很长的 agent 对话，而应是每一轮稳定产生的工件：

- 本轮目标
- 代码改动摘要
- reviewer 的 `review.md`
- 当前结论：`APPROVED` 或 `CHANGES_REQUESTED`

这样更接近工程协作，也更方便回溯。

### 3. 默认自动推进，必要时人工介入

默认情况下，工作流自动从开发进入审查，再进入下一轮修复。只有在以下场景才打断用户：

- reviewer 连续多轮无法通过
- 测试持续失败
- 出现冲突、权限问题或缺少关键信息
- 达到最大轮次

### 4. 审查意见必须可执行

reviewer 输出不能只是泛泛而谈的风格建议，而要优先给出：

- 明确的问题位置
- 问题级别（blocking / non-blocking）
- 建议修复方向
- 是否需要补测试

developer 下一轮应能直接依据 `review.md` 行动。

## 主要用户场景

### 场景 1：从一个任务启动完整协作

用户输入一个任务，例如：

```text
实现一个 AI pair programming 工作流，使用 developer 和 reviewer 两个 session 交替完成开发和审查。
```

系统反馈：

- 已创建任务
- 已选择 developer / reviewer 模型
- 正在执行第 1 轮开发

用户可以持续看到：

- 当前轮次
- 当前角色
- 最近产出文件
- 是否需要用户介入

### 场景 2：查看 reviewer 意见并继续

当 reviewer 完成后，系统应给出简洁摘要，例如：

```text
Round 2 review complete
Status: CHANGES_REQUESTED
Blocking issues: 2
Review file: .opencode/pair/rounds/002/review.md
```

如果流程为自动推进，则 developer 直接读取该文件继续修复；如果流程为半自动，则给用户一个明确入口，例如：

```text
Run next round with: opencode pair resume
```

### 场景 3：用户中途介入

用户可能在任一轮后希望：

- 查看当前 diff
- 编辑 `review.md`
- 跳过非阻塞问题
- 终止自动循环
- 指定下一轮只修复 blocking issues

因此 UX 上需要允许用户在轮次之间安全暂停，而不是只能一口气跑到底。

## 交互模型

## 启动

建议支持一个高层命令，例如：

```bash
opencode pair start
```

启动阶段建议让用户显式或隐式确认这些信息：

- 任务目标
- developer 使用的模型
- reviewer 使用的模型
- 最大轮次
- 是否自动执行测试

但默认值应足够好，让用户在多数情况下无需填写长参数。

### 运行中反馈

运行期间的输出应短、稳定、可扫描，避免长篇 agent 思维过程。建议聚焦以下信息：

- 当前轮次：`Round 1/3`
- 当前角色：`Developer` / `Reviewer`
- 当前动作：`editing files` / `running tests` / `writing review`
- 最近工件：`developer-note.md` / `review.md`
- 当前结果：`approved` / `changes requested`

### 结束态

工作流结束后，至少需要给用户一个明确总结：

- 最终状态：成功 / 未通过 / 人工中断
- 总轮次
- 最终审查结论
- 关键产出位置

例如：

```text
Pair workflow completed in 3 rounds
Final status: APPROVED
Final review: .opencode/pair/rounds/003/review.md
```

## 信息架构

建议把用户可感知的信息分为四层：

### 1. 任务层

- 用户原始目标
- 任务当前状态
- 当前轮次

### 2. 执行层

- 当前是 developer 还是 reviewer 在运行
- 当前执行到了哪一步
- 是否在跑测试

### 3. 工件层

- `developer-note.md`
- `review.md`
- `patch.diff`
- 测试结果摘要

### 4. 决策层

- reviewer 是否通过
- 是否进入下一轮
- 是否需要用户介入

这样用户无需读完整日志，也能快速理解系统状态。

## reviewer markdown 的 UX 要求

`review.md` 既要适合人读，也要适合程序解析。

推荐结构：

```md
# Review Result
Status: CHANGES_REQUESTED

## Blocking
- `src/foo.ts:42` 空值分支会抛错

## Non-blocking
- 变量名可更清晰

## Suggested Fix Plan
1. 处理空输入
2. 增加对应测试
```

UX 上要保证：

- 顶部状态字段稳定，便于自动判断
- Blocking 和 Non-blocking 分离，便于 developer 聚焦
- 问题尽量绑定文件位置，减少来回查找

## 失败与异常体验

需要为以下异常提供明确提示，而不是只暴露底层错误：

- developer 执行失败
- reviewer 无法生成有效 markdown
- 测试命令失败
- 工作区脏且可能影响判断
- 达到最大轮次仍未通过

对应提示应回答三个问题：

- 发生了什么
- 对当前流程有什么影响
- 用户现在可以做什么

## 后续可扩展的 UX 方向

- 支持在 TUI 中直接展开查看 `review.md`
- 支持 reviewer 意见筛选，只看 blocking
- 支持 `approve and stop` / `continue fixing` 快捷动作
- 支持多 reviewer 结果聚合
- 支持按轮次回放整个协作过程
