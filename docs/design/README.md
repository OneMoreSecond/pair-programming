# AI Pair Programming Workflow Design

本目录用于沉淀基于 `opencode` 的 AI pair programming 工作流设计文档。

## 文档列表

- `docs/design/ux.md`：用户体验设计，定义启动、运行中反馈、结束态和异常体验
- `docs/design/architecture.md`：系统架构设计，定义 orchestrator、developer、reviewer 和工件结构
- `docs/design/workflow.md`：状态机与轮次流转，定义状态、转移、停止条件和恢复策略
- `docs/design/protocol.md`：角色协议与 markdown 规范，定义 prompt 输入、工件格式和 `review.md` 解析规则
- `docs/design/operations.md`：运行策略与发布计划，定义失败处理、指标、预检和 rollout 路线
- `docs/design/cli.md`：CLI 命令设计，定义启动、状态查看、恢复和工件访问入口
- `docs/design/prompts.md`：prompt 模板设计，提供 developer 和 reviewer 的模板初稿
- `docs/design/state.md`：状态文件 schema，定义 `state.json` 的结构与字段语义
- `docs/design/implementation-plan.md`：MVP 实施计划，定义实现阶段、模块拆分和验收用例
- `docs/design/mvp-code-overview.md`：当前代码骨架说明，概览已落地的 Python MVP 模块和限制

## 推荐阅读顺序

1. `docs/design/ux.md`
2. `docs/design/architecture.md`
3. `docs/design/workflow.md`
4. `docs/design/protocol.md`
5. `docs/design/cli.md`
6. `docs/design/prompts.md`
7. `docs/design/state.md`
8. `docs/design/implementation-plan.md`
9. `docs/design/mvp-code-overview.md`
10. `docs/design/operations.md`

## 当前设计结论

第一版推荐采用以下原则：

- 用 orchestrator 串行调度 developer 和 reviewer
- 以工件交接为核心，而不是依赖长对话上下文
- reviewer 只输出 `review.md`，不直接改代码
- 每轮都保存 diff、说明和审查结果，保证可追踪和可恢复
- 先做闭环 MVP，再增强恢复能力、UX 和策略层

## 后续衔接

设计文档稳定后，可以继续产出：

- CLI 命令设计
- prompt 模板初稿
- 状态文件 schema
- MVP 实现计划

以上文档现已补齐，下一步可以进入具体实现设计或直接开始 MVP 开发。
