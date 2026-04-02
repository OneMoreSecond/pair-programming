from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .models import (
    MODE_AUTO,
    MODE_SEMI_AUTO,
    RESUME_DEVELOPER,
    RESUME_REVIEWER,
    RESUME_TEST,
    STATUS_APPROVED,
    STATUS_WAITING_USER,
    TaskConfig,
)
from .paths import PairPaths
from .preflight import run_preflight
from .review_parser import parse_review_file
from .storage import load_optional_project_config
from .workflow import (
    advance_task,
    cancel_task,
    init_task,
    intervene_task,
    load_current_task,
    load_task_by_id,
    resume_task,
    resume_task_from,
)


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
    start.add_argument("--prompt-profile", default=None)
    start.add_argument("--test-command", default=None)
    start.add_argument("--agent", default=None)
    start.add_argument("--max-rounds", type=int, default=None)
    start.add_argument("--mode", choices=[MODE_AUTO, MODE_SEMI_AUTO], default=None)
    start.add_argument("--dry-run", action="store_true", default=None)

    status = subparsers.add_parser("status", help="show current task status")
    status.add_argument("--workdir", default=".", help="repository root to run in")
    status.add_argument("--task-id", default=None, help="inspect a specific task")
    status.add_argument("--json", action="store_true", dest="as_json")
    status.add_argument("--verbose", action="store_true")

    resume = subparsers.add_parser("resume", help="resume the current task")
    resume.add_argument("--workdir", default=".", help="repository root to run in")
    resume.add_argument(
        "--from",
        dest="from_phase",
        choices=[RESUME_DEVELOPER, RESUME_REVIEWER, RESUME_TEST],
        default=None,
        help="resume from a specific safe phase",
    )

    stop = subparsers.add_parser("stop", help="cancel the current task")
    stop.add_argument("--workdir", default=".", help="repository root to run in")
    stop.add_argument("--reason", default=None, help="optional cancellation reason")

    intervene = subparsers.add_parser(
        "intervene", help="adjust the next round before resuming"
    )
    intervene.add_argument("--workdir", default=".", help="repository root to run in")
    intervene.add_argument(
        "--note", default=None, help="record a manual intervention note"
    )
    intervene.add_argument(
        "--focus-only-blocking",
        action="store_true",
        help="tell the next round to focus only on blocking issues",
    )
    intervene.add_argument("--developer-model", default=None)
    intervene.add_argument("--reviewer-model", default=None)
    intervene.add_argument("--max-rounds", type=int, default=None)

    review = subparsers.add_parser("review", help="show latest review summary")
    review.add_argument("--workdir", default=".", help="repository root to run in")
    review.add_argument("--task-id", default=None, help="inspect a specific task")
    review.add_argument("--round", type=int, default=None, dest="round_number")

    artifacts = subparsers.add_parser("artifacts", help="list task artifacts")
    artifacts.add_argument("--workdir", default=".", help="repository root to run in")
    artifacts.add_argument("--task-id", default=None, help="inspect a specific task")
    artifacts.add_argument("--round", type=int, default=None, dest="round_number")

    history = subparsers.add_parser("history", help="show round-by-round task history")
    history.add_argument("--workdir", default=".", help="repository root to run in")
    history.add_argument("--task-id", default=None, help="inspect a specific task")
    history.add_argument("--json", action="store_true", dest="as_json")

    config_cmd = subparsers.add_parser("config", help="show workflow configuration")
    config_cmd.add_argument("--workdir", default=".", help="repository root to run in")
    config_cmd.add_argument("--json", action="store_true", dest="as_json")

    metrics = subparsers.add_parser("metrics", help="show local workflow metrics")
    metrics.add_argument("--workdir", default=".", help="repository root to run in")
    metrics.add_argument("--task-id", default=None, help="inspect a specific task")
    metrics.add_argument("--json", action="store_true", dest="as_json")

    return parser


def _load_state_for_query(paths: PairPaths, task_id: str | None):
    if task_id:
        return load_task_by_id(paths, task_id)
    return load_current_task(paths)


def print_status(
    paths: PairPaths,
    task_id: str | None = None,
    as_json: bool = False,
    verbose: bool = False,
) -> int:
    try:
        config, state = _load_state_for_query(paths, task_id)
    except FileNotFoundError:
        print("No active task found.", file=sys.stderr)
        print('Next action: run `opencode-pair start --goal "..."`', file=sys.stderr)
        return 1
    if as_json:
        payload = state.to_dict()
        payload["config"] = config.to_dict()
        print(json.dumps(payload, indent=2))
        return 0
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
    if state.intervention_note:
        print(f"Intervention note: {state.intervention_note}")
    if state.intervention_count:
        print(f"Intervention count: {state.intervention_count}")
    if state.cancelled_at:
        print(f"Cancelled at: {state.cancelled_at}")
    if state.cancellation_reason:
        print(f"Cancellation reason: {state.cancellation_reason}")
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
    if verbose and state.rounds:
        print("Rounds:")
        for record in state.rounds:
            print(
                f"- round {record.round}: status={record.status}, review_status={record.review_status or '-'}, blocking={record.blocking_count}"
            )
    return 0


def print_review(
    paths: PairPaths, task_id: str | None = None, round_number: int | None = None
) -> int:
    try:
        _, state = _load_state_for_query(paths, task_id)
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


def print_artifacts(
    paths: PairPaths, task_id: str | None = None, round_number: int | None = None
) -> int:
    try:
        _, state = _load_state_for_query(paths, task_id)
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


def print_history(
    paths: PairPaths, task_id: str | None = None, as_json: bool = False
) -> int:
    try:
        _, state = _load_state_for_query(paths, task_id)
    except FileNotFoundError:
        print("No active task found.", file=sys.stderr)
        print('Next action: run `opencode-pair start --goal "..."`', file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps([record.to_dict() for record in state.rounds], indent=2))
        return 0

    print(f"Task: {state.task_id}")
    if not state.rounds:
        print("No round history available yet.")
        return 0
    print("Rounds:")
    for record in state.rounds:
        print(
            f"- round {record.round}: status={record.status}, review_status={record.review_status or '-'}, blocking={record.blocking_count}"
        )
        if record.developer_note_path:
            print(f"  developer_note: {record.developer_note_path}")
        if record.patch_path:
            print(f"  patch: {record.patch_path}")
        if record.review_path:
            print(f"  review: {record.review_path}")
    return 0


def print_metrics(
    paths: PairPaths, task_id: str | None = None, as_json: bool = False
) -> int:
    try:
        _, state = _load_state_for_query(paths, task_id)
    except FileNotFoundError:
        print("No active task found.", file=sys.stderr)
        print('Next action: run `opencode-pair start --goal "..."`', file=sys.stderr)
        return 1

    rounds = state.rounds
    payload = {
        "task_id": state.task_id,
        "status": state.status,
        "round_count": len(rounds),
        "current_round": state.current_round,
        "approved_rounds": sum(1 for r in rounds if r.review_status == "APPROVED"),
        "changes_requested_rounds": sum(
            1 for r in rounds if r.review_status == "CHANGES_REQUESTED"
        ),
        "max_blocking_count": max((r.blocking_count for r in rounds), default=0),
        "latest_blocking_count": rounds[-1].blocking_count if rounds else 0,
        "reviewer_attempts_total": sum(r.reviewer_attempts for r in rounds),
        "intervention_count": state.intervention_count,
        "has_failures": bool(state.last_error),
        "has_warnings": bool(state.last_warning),
    }

    if as_json:
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Task: {payload['task_id']}")
    print(f"Status: {payload['status']}")
    print(f"Round count: {payload['round_count']}")
    print(f"Approved rounds: {payload['approved_rounds']}")
    print(f"Changes requested rounds: {payload['changes_requested_rounds']}")
    print(f"Max blocking count: {payload['max_blocking_count']}")
    print(f"Latest blocking count: {payload['latest_blocking_count']}")
    print(f"Reviewer attempts total: {payload['reviewer_attempts_total']}")
    print(f"Intervention count: {payload['intervention_count']}")
    print(f"Has failures: {payload['has_failures']}")
    print(f"Has warnings: {payload['has_warnings']}")
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


def build_effective_defaults(paths: PairPaths) -> dict:
    defaults = TaskConfig(goal="<required at runtime>").to_dict()
    project_config = load_optional_project_config(paths.project_config_path())
    merged = dict(defaults)
    for key in [
        "developer_model",
        "reviewer_model",
        "prompt_profile",
        "max_rounds",
        "mode",
        "test_command",
        "opencode_agent",
        "reviewer_retry_limit",
        "protocol_version",
        "prompt_version",
        "dry_run",
    ]:
        if key in project_config:
            merged[key] = project_config[key]
    return merged


def build_task_config_from_args(paths: PairPaths, args, goal_text: str) -> TaskConfig:
    defaults = build_effective_defaults(paths)
    return TaskConfig(
        goal=goal_text,
        prompt_profile=args.prompt_profile
        if args.prompt_profile is not None
        else defaults["prompt_profile"],
        developer_model=args.developer_model
        if args.developer_model is not None
        else defaults["developer_model"],
        reviewer_model=args.reviewer_model
        if args.reviewer_model is not None
        else defaults["reviewer_model"],
        max_rounds=args.max_rounds
        if args.max_rounds is not None
        else defaults["max_rounds"],
        mode=args.mode if args.mode is not None else defaults["mode"],
        test_command=args.test_command
        if args.test_command is not None
        else defaults["test_command"],
        opencode_agent=args.agent
        if args.agent is not None
        else defaults["opencode_agent"],
        protocol_version=defaults["protocol_version"],
        prompt_version=defaults["prompt_version"],
        reviewer_retry_limit=defaults["reviewer_retry_limit"],
        focus_only_blocking=defaults["focus_only_blocking"],
        dry_run=args.dry_run if args.dry_run is not None else defaults["dry_run"],
    )


def print_config(paths: PairPaths, as_json: bool) -> int:
    payload = build_effective_defaults(paths)
    payload["project_config_path"] = str(paths.project_config_path())
    payload["project_config_present"] = paths.project_config_path().exists()
    if as_json:
        print(json.dumps(payload, indent=2))
        return 0

    print("Pair workflow defaults:")
    print(f"- mode: {payload['mode']}")
    print(f"- prompt_profile: {payload['prompt_profile']}")
    print(f"- max_rounds: {payload['max_rounds']}")
    print(f"- developer_model: {payload['developer_model'] or '-'}")
    print(f"- reviewer_model: {payload['reviewer_model'] or '-'}")
    print(f"- test_command: {payload['test_command'] or '-'}")
    print(f"- reviewer_retry_limit: {payload['reviewer_retry_limit']}")
    print(f"- protocol_version: {payload['protocol_version']}")
    print(f"- prompt_version: {payload['prompt_version']}")
    print(f"- project_config_present: {payload['project_config_present']}")
    print(f"- project_config_path: {payload['project_config_path']}")
    return 0


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
        config = build_task_config_from_args(paths, args, goal_text)
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
        return print_status(paths, args.task_id, args.as_json, args.verbose)

    if args.command == "resume":
        try:
            state = (
                resume_task_from(paths, args.from_phase)
                if args.from_phase
                else resume_task(paths)
            )
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

    if args.command == "stop":
        try:
            state = cancel_task(paths, args.reason)
        except FileNotFoundError:
            print("No active task found.", file=sys.stderr)
            print(
                'Next action: run `opencode-pair start --goal "..."`', file=sys.stderr
            )
            return 1
        print(f"Task: {state.task_id}")
        print("Status: cancelled")
        print(f"Cancellation reason: {state.cancellation_reason}")
        return 0

    if args.command == "intervene":
        try:
            config, state = intervene_task(
                paths,
                note=args.note,
                focus_only_blocking=True if args.focus_only_blocking else None,
                developer_model=args.developer_model,
                reviewer_model=args.reviewer_model,
                max_rounds=args.max_rounds,
            )
        except FileNotFoundError:
            print("No active task found.", file=sys.stderr)
            print(
                'Next action: run `opencode-pair start --goal "..."`', file=sys.stderr
            )
            return 1
        print(f"Task: {state.task_id}")
        print("Status: intervention recorded")
        print(f"Intervention count: {state.intervention_count}")
        if state.intervention_note:
            print(f"Intervention note: {state.intervention_note}")
        print(f"Focus only blocking: {config.focus_only_blocking}")
        print(
            "Next action: edit review artifacts if needed, then run `opencode-pair resume`"
        )
        return 0

    if args.command == "review":
        return print_review(paths, args.task_id, args.round_number)

    if args.command == "artifacts":
        return print_artifacts(paths, args.task_id, args.round_number)

    if args.command == "history":
        return print_history(paths, args.task_id, args.as_json)

    if args.command == "config":
        return print_config(paths, args.as_json)

    if args.command == "metrics":
        return print_metrics(paths, args.task_id, args.as_json)

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
