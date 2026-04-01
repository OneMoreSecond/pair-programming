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
from .preflight import run_preflight
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
    goal_group = start.add_mutually_exclusive_group(required=True)
    goal_group.add_argument("--goal", help="task goal")
    goal_group.add_argument(
        "--goal-file", help="path to a file containing the task goal"
    )
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

    artifacts = subparsers.add_parser("artifacts", help="list task artifacts")
    artifacts.add_argument("--workdir", default=".", help="repository root to run in")
    artifacts.add_argument("--round", type=int, default=None, dest="round_number")

    return parser


def print_status(paths: PairPaths) -> int:
    try:
        config, state = load_current_task(paths)
    except FileNotFoundError:
        print("No active task found.", file=sys.stderr)
        print('Next action: run `opencode-pair start --goal "..."`', file=sys.stderr)
        return 1
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
    if state.last_warning:
        print(f"Last warning: {state.last_warning}")
    if state.rounds:
        latest = state.rounds[-1]
        print(
            f"Latest round dir: .opencode/pair/tasks/{state.task_id}/rounds/{latest.round:03d}"
        )
        if latest.review_path:
            print(f"Latest review: {latest.review_path}")
        if latest.progress_notes:
            print("Progress notes:")
            for note in latest.progress_notes:
                print(f"- {note}")
    if config.dry_run:
        print("Dry run: enabled")
    return 0


def print_review(paths: PairPaths, round_number: int | None) -> int:
    try:
        _, state = load_current_task(paths)
    except FileNotFoundError:
        print("No active task found.", file=sys.stderr)
        print('Next action: run `opencode-pair start --goal "..."`', file=sys.stderr)
        return 1
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
        if round_number is None:
            print("No review found for the current task.", file=sys.stderr)
        else:
            print(f"No review found for round {round_number}.", file=sys.stderr)
        print(
            "Next action: run `opencode-pair status` to inspect task progress",
            file=sys.stderr,
        )
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


def print_artifacts(paths: PairPaths, round_number: int | None) -> int:
    try:
        _, state = load_current_task(paths)
    except FileNotFoundError:
        print("No active task found.", file=sys.stderr)
        print('Next action: run `opencode-pair start --goal "..."`', file=sys.stderr)
        return 1
    target = None
    if round_number is None:
        if state.rounds:
            target = state.rounds[-1]
    else:
        for record in state.rounds:
            if record.round == round_number:
                target = record
                break

    if target is None:
        if round_number is None:
            print("No round artifacts found for the current task.", file=sys.stderr)
        else:
            print(f"No artifacts found for round {round_number}.", file=sys.stderr)
        print(
            "Next action: run `opencode-pair status` to inspect available rounds",
            file=sys.stderr,
        )
        return 1

    paths_to_print = [
        target.developer_prompt_path,
        target.developer_log_path,
        target.developer_note_path,
        target.patch_path,
        target.test_log_path,
        target.test_summary_path,
        target.reviewer_prompt_path,
        target.reviewer_log_path,
        target.review_path,
    ]
    print(f"Round: {target.round}")
    for item in paths_to_print:
        if item:
            print(item)
    return 0


def print_preflight(report) -> None:
    if report.errors:
        print("Preflight errors:", file=sys.stderr)
        for item in report.errors:
            print(f"- {item}", file=sys.stderr)
    if report.warnings:
        print("Preflight warnings:")
        for item in report.warnings:
            print(f"- {item}")


def load_goal(goal: str | None, goal_file: str | None) -> str:
    if goal is not None:
        return goal
    if goal_file is None:
        raise ValueError("either --goal or --goal-file is required")
    path = Path(goal_file)
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise ValueError(f"goal file not found: {goal_file}") from exc
    except OSError as exc:
        raise ValueError(f"could not read goal file: {goal_file}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = PairPaths(Path(args.workdir))

    if args.command == "start":
        try:
            goal_text = load_goal(args.goal, args.goal_file)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        config = TaskConfig(
            goal=goal_text,
            developer_model=args.developer_model,
            reviewer_model=args.reviewer_model,
            max_rounds=args.max_rounds,
            mode=args.mode,
            test_command=args.test_command,
            opencode_agent=args.agent,
            dry_run=args.dry_run,
        )
        preflight = run_preflight(paths, config)
        print_preflight(preflight)
        if not preflight.ok:
            return 2
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
        try:
            state = resume_task(paths)
        except FileNotFoundError:
            print("No active task found.", file=sys.stderr)
            print(
                'Next action: run `opencode-pair start --goal "..."`', file=sys.stderr
            )
            return 1
        print(f"Task: {state.task_id}")
        print(f"Status: {state.status}")
        print(f"Round: {state.current_round}/{state.max_rounds}")
        if state.status == STATUS_APPROVED:
            print("Result: approved")
            return 0
        if state.status == STATUS_WAITING_USER:
            print("Next action: inspect review or artifacts, then resume again")
            return 3
        return 0

    if args.command == "review":
        return print_review(paths, args.round_number)

    if args.command == "artifacts":
        return print_artifacts(paths, args.round_number)

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
