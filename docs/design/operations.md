# AI Pair Programming Workflow Operations And Rollout

## 目标

本文定义该工作流的运行策略、失败处理、指标、发布顺序和后续演进建议，帮助第一版从设计走向稳定可用。

## 运行模式

建议支持三种模式：

### 1. Auto

系统自动推进完整回路：developer -> reviewer -> next round。

适合：

- 小到中等规模任务
- 用户希望最少交互
- 本地开发环境已准备好

### 2. Semi-auto

每轮结束后暂停，等待用户确认继续。

适合：

- 早期试点阶段
- reviewer 输出策略仍在调优
- 任务风险较高

### 3. Manual Recovery

发生失败或超出最大轮次后，用户手动修订工件并恢复流程。

适合：

- prompt 需要人工修正
- reviewer 出现误判
- 环境问题导致自动化不稳定

## 默认运行策略

第一版推荐默认策略：

- 模式：`Semi-auto` 或保守的 `Auto`
- 最大轮次：`3`
- 自动测试：开启
- reviewer blocking issue 上限：`3`
- 遇到解析失败时自动重试一次

原因是第一版最重要的是可控和可解释，而不是极限自动化。

## 失败处理策略

### Session 失败

若 developer 或 reviewer session 无法启动或中途崩溃：

- 保存当前日志和状态
- 标记任务进入 `failed` 或 `waiting_user`
- 提示用户可执行的恢复动作

### 审查协议失败

若 reviewer 没有输出合法 `review.md`：

- 自动重试一次 reviewer
- 若仍失败，提示用户检查 prompt 或手工修订 markdown

### 测试失败

测试失败不一定意味着流程终止。建议策略：

- 先记录测试摘要
- 让 reviewer 感知测试失败
- 由 reviewer 判断是否构成 blocking issue

### 无进展循环

如果 developer 多轮无法真正推进：

- 提示用户当前卡住点
- 展示最近两轮 blocking issue 对比
- 建议人工接管或更换模型

## 可观测性

至少应记录以下运行信息：

- 任务 ID
- 每轮开始和结束时间
- 每个 session 的退出状态
- review 结果状态
- blocking issue 数量
- 测试命令与结果

第一版无需引入复杂监控平台，将这些信息写入本地日志或状态文件即可。

## 成功指标

可以用以下指标评估该工作流是否值得继续投入：

- 平均多少轮通过
- 首轮通过率
- 需要人工介入的比例
- reviewer 误报率
- 任务完成时间
- 用户是否愿意再次使用

这些指标比单纯统计 token 或调用次数更能反映真实产品价值。

## 风险点

### reviewer 过严

如果 reviewer 总是在提低价值问题，开发效率会明显下降。

缓解手段：

- 限制 blocking issue 数量
- 强化审查优先级 prompt
- 允许用户跳过 non-blocking issues

### developer 过度发散

如果 developer 不聚焦当前 review，可能越改越偏离目标。

缓解手段：

- 下一轮 prompt 中强调只修复 blocking issues
- 显式传入 review 摘要
- 对超大 diff 给出告警

### 环境噪声影响判断

例如仓库已有脏改动、测试本身不稳定、依赖未安装。

缓解手段：

- 启动前做预检
- 把环境问题与代码问题区分呈现
- 允许跳过测试但记录原因

## 预检建议

在 `pair start` 前可以执行轻量预检：

- 工作目录是否存在
- 是否存在未提交改动
- 测试命令是否可执行
- prompt 模板是否存在
- 输出目录是否可写

预检的目标不是阻止一切风险，而是尽早把问题暴露给用户。

## 发布计划

### Phase 1: Closed Loop MVP

范围：

- 单 developer / 单 reviewer
- markdown 工件
- 单一状态文件
- 手动或半自动推进

成功标准：

- 能稳定完成至少一个真实编码任务
- 能在 1 到 3 轮内收敛

### Phase 2: Better Recovery

范围：

- `resume`
- `status`
- 更清晰的失败提示
- 更稳定的测试摘要

### Phase 3: Better UX

范围：

- TUI 状态视图
- 工件快速打开
- 按轮次浏览历史
- 快捷动作

### Phase 4: Advanced Policies

范围：

- 多 reviewer
- tester 角色
- 策略化路由不同模型
- 结构化评分

## 实现建议

第一版落地时，优先顺序建议为：

1. 协议稳定
2. 状态机稳定
3. 工件落盘稳定
4. 恢复能力
5. UX 打磨

不要一开始就加入太多智能策略，否则问题会难以定位。

## 团队协作建议

如果后续有多人参与完善该工作流，建议明确这些边界：

- 产品设计维护 `docs/design/`
- 平台实现维护 orchestrator
- prompt 策略独立版本管理
- 通过真实任务回放验证修改效果

这样可以避免把产品、协议、实现和 prompt 逻辑混在一起。
