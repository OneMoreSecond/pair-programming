# Opencode Pair MVP

`opencode-pair` 是一个面向终端用户的 AI pair programming 工作流原型。

它会在本地仓库里串行调度两个角色：

- developer：负责实现或修改代码
- reviewer：负责审查当前 round 改动并输出结构化 `review.md`

当前版本是一个可运行的 MVP，适合先验证小到中等规模的任务闭环。

## 你可以用它做什么

- 启动一个 developer -> reviewer 的工作流
- 让每一轮工件自动落盘
- 查看当前任务状态和最近 review
- 在 `waiting_user` 状态下继续下一轮
- 用 `--dry-run` 先验证流程是否能跑通

## 安装

要求：

- Python 3.9+
- 本机可用的 `opencode` CLI

在仓库根目录安装当前项目：

```bash
python3 -m pip install -e .
```

安装后可以直接使用：

```bash
opencode-pair --help
```

如果你只是开发这个项目本身，也可以继续用模块方式运行，但这属于开发者用法，不是推荐的终端用户入口。

## 快速开始

### 1. 先做一次 dry-run

```bash
opencode-pair start \
  --goal "Create a small sample artifact for the pair workflow" \
  --dry-run
```

如果任务描述比较长，也可以从文件读取：

```bash
opencode-pair start --goal-file ./task.md --dry-run
```

启动前会执行轻量 preflight，提前提示常见问题，例如：

- prompt 模板缺失
- `opencode` 不在 PATH 中
- git 工作区已有未提交改动
- 配置的测试命令可能不可执行

### 2. 查看状态和 review

```bash
opencode-pair status
opencode-pair review
opencode-pair artifacts
```

如果当前没有活动任务，CLI 会直接告诉你下一步该执行什么。

更深入的查询方式：

```bash
opencode-pair status --json
opencode-pair status --verbose
opencode-pair config
opencode-pair metrics
opencode-pair review --round 2
opencode-pair artifacts --round 2
opencode-pair history
opencode-pair resume --from reviewer
opencode-pair stop --reason "pause for manual review"
opencode-pair intervene --focus-only-blocking --note "ignore non-blocking for now"
```

如果你想在 round 之间人工介入，可以：

- 先手动编辑当前 `review.md`
- 或者用 `opencode-pair intervene` 调整下一轮策略
- 然后再执行 `opencode-pair resume`

### 3. 继续下一轮

```bash
opencode-pair resume
```

## 真实运行示例

```bash
opencode-pair start \
  --goal "Add a small markdown file documenting the pair workflow" \
  --mode semi_auto
```

可选参数：

- `--workdir <path>`
- `--goal-file <path>`
- `--developer-model <provider/model>`
- `--reviewer-model <provider/model>`
- `--test-command "pytest -q"`
- `--agent <agent-name>`
- `--max-rounds 3`
- `--mode auto|semi_auto`

默认情况下，`--workdir` 使用当前目录。

如果你想给当前仓库配置项目级默认值，可以放一个可选文件：

```text
.opencode/pair/config.json
```

例如：

```json
{
  "mode": "auto",
  "max_rounds": 5,
  "test_command": "python3 -m unittest discover -s tests -p \"test_*.py\""
}
```

然后可以用下面命令查看当前生效的项目默认值：

```bash
opencode-pair config
opencode-pair config --json
```

配置优先级为：

```text
CLI flags > task config > project config > built-in defaults
```

## 运行后会生成什么

任务工件会写到：

```text
.opencode/pair/tasks/<task-id>/
```

每个 round 通常包含：

- `developer-input.md`
- `developer.log`
- `developer-note.md`
- `patch.diff`
- `tester-note.md`
- `test.log` / `test-summary.md`
- `reviewer-input.md`
- `reviewer.log`
- `review.md`

如果你想快速列出当前 round 的这些文件：

```bash
opencode-pair artifacts
opencode-pair artifacts --round 2
```

## 当前限制

- 还不是原生 `opencode pair` 子命令
- review 协议和恢复策略还在持续增强
- 更复杂的多轮真实代码任务还需要更多回归验证

## 开发者说明

如果你在开发这个项目本身：

- 设计文档在 `docs/design/`
- ticket 流程在 `AGENTS.md`
- backlog 在 `tickets/`

运行测试：

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
