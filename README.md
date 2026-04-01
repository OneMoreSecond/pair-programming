# Opencode Pair MVP

`opencode-pair` 是一个基于 `opencode` 的最小可运行 AI pair programming 工作流原型。

它通过三个角色协作完成一轮或多轮开发闭环：

- `orchestrator`：调度轮次、落盘状态、组装 prompt
- `developer`：实现需求或根据 review 修改代码
- `reviewer`：只读审查当前 round 改动，并输出结构化 `review.md`

当前版本的目标是验证流程，而不是提供完整产品能力。

## 当前能力

- 初始化 pair task 并保存任务状态
- 生成 developer / reviewer prompt 文件
- 调用 `opencode run` 启动两个角色的 session
- 生成 round 级工件目录
- 解析 `review.md` 的 `Status`
- 支持 `start` / `status` / `review` / `resume`
- 支持 `--dry-run` 验证状态流转

## 目录结构

```text
src/opencode_pair/          Python MVP 代码
.opencode/pair/prompts/     默认 prompt 模板
docs/design/                设计文档
examples/                   示例任务
tests/                      基础测试
```

运行中的任务工件会生成到：

```text
.opencode/pair/tasks/<task-id>/
```

## 环境要求

- Python 3.9+
- 本机可用的 `opencode` CLI

## 快速开始

### 1. 查看 CLI

```bash
PYTHONPATH=src python3 -m opencode_pair --help
```

### 2. 先用 dry-run 验证流程

```bash
PYTHONPATH=src python3 -m opencode_pair start \
  --workdir . \
  --goal "Create a small sample artifact for the pair workflow" \
  --dry-run
```

### 3. 查看状态和 review

```bash
PYTHONPATH=src python3 -m opencode_pair status --workdir .
PYTHONPATH=src python3 -m opencode_pair review --workdir .
```

### 4. 继续下一轮

```bash
PYTHONPATH=src python3 -m opencode_pair resume --workdir .
```

## 真实运行示例

只要本机 `opencode` 可用，就可以去掉 `--dry-run`：

```bash
PYTHONPATH=src python3 -m opencode_pair start \
  --workdir . \
  --goal "Add a small markdown file documenting the pair workflow" \
  --mode semi_auto
```

可选参数：

- `--developer-model <provider/model>`
- `--reviewer-model <provider/model>`
- `--test-command "pytest -q"`
- `--agent <agent-name>`
- `--max-rounds 3`
- `--mode auto|semi_auto`

## Prompt 模板

默认模板在：

- `.opencode/pair/prompts/developer.md`
- `.opencode/pair/prompts/reviewer.md`

MVP 直接读取这两个文件并注入变量，因此你可以先从这里调 prompt。

## 工件说明

每个 round 目录通常包含：

- `developer-input.md`
- `developer.log`
- `developer-note.md`
- `patch.diff`
- `test.log` / `test-summary.md`（如果配置了测试）
- `reviewer-input.md`
- `reviewer.log`
- `review.md`

## 测试

运行基础测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```

## 当前限制

- 仍是独立 MVP，还没有接入 `opencode pair` 官方子命令
- `patch.diff` 目前来自快照比较，不是 git diff
- review 解析器目前只覆盖最小协议
- 真实运行效果依赖 `opencode` 模型行为和 prompt 稳定性

## 真实运行结果

已经在当前仓库完成过一次真实非 dry-run 验证：

- 任务创建成功
- developer 成功写入目标 markdown 文件和 `developer-note.md`
- reviewer 成功写入结构化 `review.md`
- 工作流在第 1 轮直接 `APPROVED`

示例产物可参考：

- `examples/real-run-artifact.md`
- `.opencode/pair/tasks/pair-20260401-103928/rounds/001/developer-note.md`
- `.opencode/pair/tasks/pair-20260401-103928/rounds/001/review.md`

## 相关文档

- `docs/design/README.md`
- `docs/design/mvp-code-overview.md`
