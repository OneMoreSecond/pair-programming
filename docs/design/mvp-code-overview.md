# MVP Code Overview

## 当前实现范围

仓库中已经补入一个最小可运行的 Python MVP 骨架，用于验证 pair programming 工作流的核心闭环。

代码入口位于：

- `src/opencode_pair/cli.py`
- `src/opencode_pair/workflow.py`

默认 prompt 模板位于：

- `.opencode/pair/prompts/developer.md`
- `.opencode/pair/prompts/reviewer.md`

## 主要模块

- `src/opencode_pair/models.py`：状态、配置和 round 数据结构
- `src/opencode_pair/paths.py`：工作流目录和文件路径管理
- `src/opencode_pair/storage.py`：`config.json` / `state.json` 读写
- `src/opencode_pair/prompts.py`：prompt 模板渲染
- `src/opencode_pair/review_parser.py`：`review.md` 状态解析
- `src/opencode_pair/snapshot.py`：工作区快照和 patch 生成
- `src/opencode_pair/runner.py`：调用 `opencode run` 和测试命令
- `src/opencode_pair/workflow.py`：任务初始化、轮次推进、resume 逻辑

## 当前支持的 CLI

可以这样运行：

```bash
PYTHONPATH=src python3 -m opencode_pair --help
PYTHONPATH=src python3 -m opencode_pair start --goal "your task" --dry-run
PYTHONPATH=src python3 -m opencode_pair status
PYTHONPATH=src python3 -m opencode_pair review
PYTHONPATH=src python3 -m opencode_pair resume
```

## 当前行为说明

- `start` 会初始化 `.opencode/pair/tasks/<task-id>/`
- developer 和 reviewer 各自生成一份输入 prompt 文件
- dry-run 模式下不会真正调用模型执行修改，而是验证状态流转和工件落盘
- reviewer 在 dry-run 下会写一个占位 `review.md`
- 非 dry-run 模式下依赖本机可用的 `opencode run`

## 已验证内容

- Python 模块可编译
- CLI 可正常显示帮助
- dry-run 模式可完成一轮并进入 `waiting_user`
- `state.json`、round 目录和 prompt 工件可正常生成

## 当前已知限制

- 还没有把它集成为 `opencode pair` 子命令，而是独立的 `opencode-pair`/Python 入口
- developer / reviewer 真实执行效果依赖 prompt 约束和本机 `opencode` 能力
- `patch.diff` 目前基于工作区快照比较，不是 git diff
- 还没有实现 `artifacts`、`stop`、`config` 等扩展命令
- review 解析目前只做最小字段解析

## 下一步建议

- 优先跑一次非 dry-run 的真实任务，观察 prompt 是否足够稳定
- 如果 reviewer 格式波动较大，先加强 reviewer prompt 和解析器
- 如果 developer 经常不写 note，可以把 note 写入改为更强约束或显式脚本化生成
