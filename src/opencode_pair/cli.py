from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import (
    MODE_AUTO,
    MODE_SEMI_AUTO,
    STATUS_APPROVED,
    STATUS_WAITING_USER,
    TaskConfig,
)
from .paths import PairPaths
from .review_parser import parse_review_file
from .workflow import advance_task, init_task, load_current_task, resume_task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="opencode-pair", description="MVP pair programming orchestrator"
    )
    parser.add_argument("--workdir", default=".", help="repository root to run in")

    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="start a new pair task")
    start.add_argument("--workdir", default=".", help="repository root to run in")
    start.add_argument("--goal", required=True, help="task goal")
    start.add_argument("--developer-model", default=None)
    start.add_argument("--reviewer-model", default=None)
    start.add_argument("--test-command", default=None)
    start.add_argument("--agent", default=None)
    start.add_argument("--max-rounds", type=int, default=3)
    start.add_argument(
        "--mode", choices=[MODE_AUTO, MODE_SEMI_AUTO], default=MODE_SEMI_AUTO
    )
    start.add_argument("--dry-run", action="store_true")

    status = subparsers.add_parser("status", help="show current task status")
    status.add_argument("--workdir", default=".", help="repository root to run in")

    resume = subparsers.add_parser("resume", help="resume the current task")
    resume.add_argument("--workdir", default=".", help="repository root to run in")

    review = subparsers.add_parser("review", help="show latest review summary")
    review.add_argument("--workdir", default=".", help="repository root to run in")
    review.add_argument("--round", type=int, default=None, dest="round_number")

    return parser


def print_status(paths: PairPaths) -> int:
    config, state = load_current_task(paths)
    print(f"Task: {state.task_id}")
    print(f"Status: {state.status}")
    print(f"Round: {state.current_round}/{state.max_rounds}")
    print(f"Mode: {state.mode}")
    print(f"Developer model: {state.developer_model or '-'}")
    print(f"Reviewer model: {state.reviewer_model or '-'}")
    print(f"Test command: {state.test_command or '-'}")
    print(f"Last review status: {state.last_review_status or '-'}")
    print(f"Resume from: {state.resume_from}")
    if state.last_error:
        print(f"Last error: {state.last_error}")
    if state.rounds:
        latest = state.rounds[-1]
        print(
            f"Latest round dir: .opencode/pair/tasks/{state.task_id}/rounds/{latest.round:03d}"
        )
        if latest.review_path:
            print(f"Latest review: {latest.review_path}")
    if config.dry_run:
        print("Dry run: enabled")
    return 0


def print_review(paths: PairPaths, round_number: int | None) -> int:
    _, state = load_current_task(paths)
    target = None
    if round_number is None:
        for record in reversed(state.rounds):
            if record.review_path:
                target = record
                break
    else:
        for record in state.rounds:
            if record.round == round_number:
                target = record
                break
    if target is None or not target.review_path:
        print("No review found.", file=sys.stderr)
        return 1
    review_path = paths.workdir / target.review_path
    parsed = parse_review_file(review_path)
    print(f"Round: {target.round}")
    print(f"Status: {parsed.status}")
    print(f"Blocking issues: {parsed.blocking_count}")
    print(f"Review path: {target.review_path}")
    if parsed.summary:
        print(f"Summary: {parsed.summary}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = PairPaths(Path(args.workdir))

    if args.command == "start":
        config = TaskConfig(
            goal=args.goal,
            developer_model=args.developer_model,
            reviewer_model=args.reviewer_model,
            max_rounds=args.max_rounds,
            mode=args.mode,
            test_command=args.test_command,
            opencode_agent=args.agent,
            dry_run=args.dry_run,
        )
        state = init_task(paths, config)
        state = advance_task(paths, config, state)
        print(f"Task created: {state.task_id}")
        print(f"Status: {state.status}")
        print(f"Round: {state.current_round}/{state.max_rounds}")
        if state.status == STATUS_APPROVED:
            print("Result: approved")
            return 0
        if state.status == STATUS_WAITING_USER:
            print("Next action: opencode-pair resume")
            return 3
        return 0

    if args.command == "status":
        return print_status(paths)

    if args.command == "resume":
        state = resume_task(paths)
        print(f"Task: {state.task_id}")
        print(f"Status: {state.status}")
        print(f"Round: {state.current_round}/{state.max_rounds}")
        if state.status == STATUS_APPROVED:
            print("Result: approved")
            return 0
        if state.status == STATUS_WAITING_USER:
            print("Next action: inspect review and resume again")
            return 3
        return 0

    if args.command == "review":
        return print_review(paths, args.round_number)

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
