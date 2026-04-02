from __future__ import annotations

from pathlib import Path
from typing import Optional

from .models import (
    MODE_AUTO,
    RESUME_DEVELOPER,
    RESUME_REVIEWER,
    RESUME_TEST,
    STATUS_APPROVED,
    STATUS_CANCELLED,
    STATUS_CHANGES_REQUESTED,
    STATUS_DEVELOPER_COMPLETED,
    STATUS_DEVELOPER_RUNNING,
    STATUS_FAILED,
    STATUS_INITIALIZED,
    STATUS_REVIEWER_RUNNING,
    STATUS_TESTING_RUNNING,
    STATUS_WAITING_USER,
    RoundRecord,
    TaskConfig,
    TaskState,
)
from .paths import PairPaths
from .patches import git_diff_text, is_git_repo, write_patch
from .prompts import render_prompt_to_file
from .review_parser import ReviewProtocolError, parse_review_file
from .runner import run_opencode, run_test_command
from .storage import load_config, load_state, save_config, save_state
from .utils import ensure_parent, relative_to, slugify_task_id, utc_now


def default_focus_for_round(
    round_number: int,
    last_review_status: Optional[str],
    focus_only_blocking: bool = False,
) -> str:
    if focus_only_blocking:
        return "focus only on blocking issues and make the smallest safe changes"
    if round_number == 1:
        return "implement the task with minimal necessary changes"
    if last_review_status == "CHANGES_REQUESTED":
        return "fix blocking issues first and keep changes narrow"
    return "make the smallest changes needed to move the task forward"


def ensure_prompt_templates(paths: PairPaths) -> None:
    paths.ensure_root()
    missing = []
    if not paths.developer_template_path().exists():
        missing.append(str(paths.developer_template_path()))
    if not paths.reviewer_template_path().exists():
        missing.append(str(paths.reviewer_template_path()))
    if missing:
        raise FileNotFoundError("missing prompt templates: " + ", ".join(missing))


def init_task(paths: PairPaths, config: TaskConfig) -> TaskState:
    ensure_prompt_templates(paths)
    task_id = slugify_task_id()
    rounds_dir = paths.rounds_dir(task_id)
    rounds_dir.mkdir(parents=True, exist_ok=True)

    created_at = utc_now()
    state = TaskState(
        version=1,
        task_id=task_id,
        goal=config.goal,
        status=STATUS_INITIALIZED,
        mode=config.mode,
        current_round=1,
        max_rounds=config.max_rounds,
        developer_model=config.developer_model,
        reviewer_model=config.reviewer_model,
        test_command=config.test_command,
        opencode_agent=config.opencode_agent,
        workdir=str(paths.workdir),
        protocol_version=config.protocol_version,
        prompt_version=config.prompt_version,
        created_at=created_at,
        updated_at=created_at,
        resume_from=RESUME_DEVELOPER,
    )
    save_config(paths.config_path(task_id), config)
    paths.goal_path(task_id).write_text(config.goal + "\n", encoding="utf-8")
    save_state(paths.state_path(task_id), state)
    ensure_parent(paths.current_task_file)
    paths.current_task_file.write_text(task_id + "\n", encoding="utf-8")
    return state


def load_current_task(paths: PairPaths) -> tuple[TaskConfig, TaskState]:
    task_id = paths.current_task_file.read_text(encoding="utf-8").strip()
    return load_config(paths.config_path(task_id)), load_state(
        paths.state_path(task_id)
    )


def load_task_by_id(paths: PairPaths, task_id: str) -> tuple[TaskConfig, TaskState]:
    return load_config(paths.config_path(task_id)), load_state(
        paths.state_path(task_id)
    )


def save_task(paths: PairPaths, state: TaskState) -> None:
    state.updated_at = utc_now()
    save_state(paths.state_path(state.task_id), state)


def ensure_round_record(state: TaskState) -> RoundRecord:
    record = state.current_round_record()
    if record:
        return record
    record = RoundRecord(
        round=state.current_round, status=state.status, started_at=utc_now()
    )
    state.rounds.append(record)
    return record


def previous_round_record(state: TaskState) -> Optional[RoundRecord]:
    target = state.current_round - 1
    for record in state.rounds:
        if record.round == target:
            return record
    return None


def detect_progress_issues(
    state: TaskState, record: RoundRecord, patch_text: str
) -> list[str]:
    issues: list[str] = []
    previous = previous_round_record(state)
    record.patch_changed = bool(patch_text.strip())

    if not record.patch_changed:
        issues.append("current round produced an empty patch")

    if previous and previous.patch_path:
        prev_patch_path = Path(state.workdir) / previous.patch_path
        if prev_patch_path.exists():
            prev_patch_text = prev_patch_path.read_text(encoding="utf-8")
            if patch_text == prev_patch_text:
                issues.append(
                    "current round patch is unchanged from the previous round"
                )

    if previous and previous.review_status == "CHANGES_REQUESTED":
        if (
            record.blocking_count >= previous.blocking_count
            and record.blocking_count > 0
        ):
            issues.append(
                "blocking issue count did not decrease from the previous round"
            )

    return issues


def write_fallback_developer_note(path: Path, focus: str) -> None:
    if path.exists():
        return
    path.write_text(
        "# Developer Note\n\n"
        "## Goal\n"
        f"{focus}\n\n"
        "## Changes Made\n"
        "- The developer session did not write a note; inspect the patch and logs for details.\n\n"
        "## Tests\n"
        "- Passed: not recorded\n"
        "- Failed: not recorded\n"
        "- Not run: unknown\n\n"
        "## Notes For Reviewer\n"
        "- This note was auto-generated by the orchestrator.\n",
        encoding="utf-8",
    )


def write_test_summary(
    path: Path, command_text: str, returncode: int, log_rel_path: str
) -> None:
    result = "PASSED" if returncode == 0 else "FAILED"
    path.write_text(
        "# Test Summary\n\n"
        "## Command\n"
        f"{command_text}\n\n"
        "## Result\n"
        f"{result}\n\n"
        "## Notes\n"
        f"- Exit code: {returncode}\n"
        f"- Log: `{log_rel_path}`\n",
        encoding="utf-8",
    )


def _developer_context(
    paths: PairPaths, config: TaskConfig, state: TaskState, round_dir: Path
) -> dict[str, str]:
    previous_review = "No previous review. Implement the task from scratch."
    if state.current_round > 1:
        prev_round_dir = paths.round_dir(state.task_id, state.current_round - 1)
        prev_review_path = prev_round_dir / "review.md"
        if prev_review_path.exists():
            previous_review = prev_review_path.read_text(encoding="utf-8")
    developer_note_path = round_dir / "developer-note.md"
    return {
        "goal": state.goal,
        "task_id": state.task_id,
        "round": str(state.current_round),
        "max_rounds": str(state.max_rounds),
        "focus": default_focus_for_round(
            state.current_round,
            state.last_review_status,
            config.focus_only_blocking,
        ),
        "workdir": str(paths.workdir),
        "previous_review": previous_review,
        "relevant_context": "Read the repository as needed. Keep changes narrow and task-focused.",
        "developer_note_path": relative_to(developer_note_path, paths.workdir),
    }


def _reviewer_context(
    paths: PairPaths, state: TaskState, round_dir: Path
) -> dict[str, str]:
    test_summary_path = round_dir / "test-summary.md"
    if test_summary_path.exists():
        test_summary_section = (
            f"Read `{relative_to(test_summary_path, paths.workdir)}` before reviewing."
        )
    else:
        test_summary_section = "No test summary is available for this round."
    return {
        "goal": state.goal,
        "workdir": str(paths.workdir),
        "developer_note_path": relative_to(
            round_dir / "developer-note.md", paths.workdir
        ),
        "test_summary_section": test_summary_section,
        "patch_path": relative_to(round_dir / "patch.diff", paths.workdir),
        "review_path": relative_to(round_dir / "review.md", paths.workdir),
    }


def run_developer_round(paths: PairPaths, config: TaskConfig, state: TaskState) -> None:
    round_dir = paths.round_dir(state.task_id, state.current_round)
    round_dir.mkdir(parents=True, exist_ok=True)
    record = ensure_round_record(state)
    record.status = STATUS_DEVELOPER_RUNNING
    state.status = STATUS_DEVELOPER_RUNNING
    state.resume_from = RESUME_DEVELOPER
    save_task(paths, state)

    developer_prompt_path = round_dir / "developer-input.md"
    render_prompt_to_file(
        paths.developer_template_path(),
        developer_prompt_path,
        _developer_context(paths, config, state, round_dir),
    )
    record.developer_prompt_path = relative_to(developer_prompt_path, paths.workdir)

    developer_log_path = round_dir / "developer.log"
    record.developer_log_path = relative_to(developer_log_path, paths.workdir)
    result = run_opencode(
        prompt_file=developer_prompt_path,
        workdir=paths.workdir,
        log_path=developer_log_path,
        model=config.developer_model,
        agent=config.opencode_agent,
        title=f"{state.task_id} developer round {state.current_round}",
        dry_run=config.dry_run,
    )
    if result.returncode != 0:
        state.status = STATUS_FAILED
        state.last_error = (
            f"developer session failed with exit code {result.returncode}"
        )
        save_task(paths, state)
        raise RuntimeError(state.last_error)

    developer_note_path = round_dir / "developer-note.md"
    write_fallback_developer_note(
        developer_note_path,
        default_focus_for_round(state.current_round, state.last_review_status),
    )
    record.developer_note_path = relative_to(developer_note_path, paths.workdir)

    patch_path = round_dir / "patch.diff"
    if is_git_repo(paths.workdir):
        patch_text = git_diff_text(paths.workdir)
    else:
        patch_text = ""
    write_patch(patch_path, patch_text)
    record.patch_path = relative_to(patch_path, paths.workdir)
    record.patch_changed = bool(patch_text.strip())

    state.status = STATUS_DEVELOPER_COMPLETED
    state.resume_from = RESUME_TEST if config.test_command else RESUME_REVIEWER
    record.status = STATUS_DEVELOPER_COMPLETED
    save_task(paths, state)


def run_tests(paths: PairPaths, config: TaskConfig, state: TaskState) -> None:
    if not config.test_command:
        return
    round_dir = paths.round_dir(state.task_id, state.current_round)
    record = ensure_round_record(state)
    state.status = STATUS_TESTING_RUNNING
    state.resume_from = RESUME_TEST
    save_task(paths, state)

    test_log_path = round_dir / "test.log"
    record.test_log_path = relative_to(test_log_path, paths.workdir)
    result = run_test_command(
        config.test_command, paths.workdir, test_log_path, dry_run=config.dry_run
    )
    test_summary_path = round_dir / "test-summary.md"
    record.test_summary_path = relative_to(test_summary_path, paths.workdir)
    write_test_summary(
        test_summary_path, config.test_command, result.returncode, record.test_log_path
    )
    state.resume_from = RESUME_REVIEWER
    save_task(paths, state)


def run_reviewer_round(paths: PairPaths, config: TaskConfig, state: TaskState) -> None:
    round_dir = paths.round_dir(state.task_id, state.current_round)
    record = ensure_round_record(state)
    state.status = STATUS_REVIEWER_RUNNING
    state.resume_from = RESUME_REVIEWER
    save_task(paths, state)

    parsed = None
    review_path = round_dir / "review.md"
    last_protocol_error = None

    for attempt in range(1, config.reviewer_retry_limit + 2):
        prompt_name = (
            "reviewer-input.md"
            if attempt == 1
            else f"reviewer-input.retry-{attempt}.md"
        )
        log_name = "reviewer.log" if attempt == 1 else f"reviewer.retry-{attempt}.log"
        reviewer_prompt_path = round_dir / prompt_name
        reviewer_log_path = round_dir / log_name
        render_prompt_to_file(
            paths.reviewer_template_path(),
            reviewer_prompt_path,
            _reviewer_context(paths, state, round_dir),
        )
        record.reviewer_prompt_path = relative_to(reviewer_prompt_path, paths.workdir)
        record.reviewer_log_path = relative_to(reviewer_log_path, paths.workdir)
        record.reviewer_attempts = attempt

        result = run_opencode(
            prompt_file=reviewer_prompt_path,
            workdir=paths.workdir,
            log_path=reviewer_log_path,
            model=config.reviewer_model,
            agent=config.opencode_agent,
            title=f"{state.task_id} reviewer round {state.current_round} attempt {attempt}",
            dry_run=config.dry_run,
        )
        if result.returncode != 0:
            state.status = STATUS_FAILED
            state.last_error = (
                f"reviewer session failed with exit code {result.returncode}"
            )
            save_task(paths, state)
            raise RuntimeError(state.last_error)

        if not review_path.exists() and config.dry_run:
            review_path.write_text(
                "# Review Result\nStatus: CHANGES_REQUESTED\n\n## Blocking\n- Dry run placeholder.\n\n## Non-blocking\n- None.\n\n## Suggested Fix Plan\n1. Run without --dry-run to produce a real review.\n\n## Summary\nDry run mode generated a placeholder review.\n",
                encoding="utf-8",
            )
        if not review_path.exists():
            last_protocol_error = "reviewer did not write review.md"
            if attempt <= config.reviewer_retry_limit:
                continue
            state.status = STATUS_FAILED
            state.last_error = f"review protocol error: {last_protocol_error}"
            save_task(paths, state)
            raise RuntimeError(state.last_error)

        try:
            parsed = parse_review_file(review_path)
            break
        except ReviewProtocolError as exc:
            last_protocol_error = str(exc)
            if attempt <= config.reviewer_retry_limit:
                continue
            state.status = STATUS_FAILED
            state.last_error = f"review protocol error: {last_protocol_error}"
            save_task(paths, state)
            raise RuntimeError(state.last_error) from exc

    if parsed is None:
        state.status = STATUS_FAILED
        state.last_error = f"review protocol error: {last_protocol_error or 'unknown review parse failure'}"
        save_task(paths, state)
        raise RuntimeError(state.last_error)

    record.review_path = relative_to(review_path, paths.workdir)
    record.review_status = parsed.status
    record.blocking_count = parsed.blocking_count
    record.completed_at = utc_now()
    state.last_review_status = parsed.status
    progress_issues = detect_progress_issues(
        state,
        record,
        review_path.parent.joinpath("patch.diff").read_text(encoding="utf-8"),
    )
    record.progress_notes = progress_issues

    if parsed.status == "APPROVED":
        state.status = STATUS_APPROVED
        state.completed_at = utc_now()
        state.resume_from = RESUME_REVIEWER
        record.status = STATUS_APPROVED
    else:
        record.status = STATUS_CHANGES_REQUESTED
        if progress_issues:
            state.status = STATUS_WAITING_USER
            state.resume_from = RESUME_DEVELOPER
            state.last_warning = "; ".join(progress_issues)
        elif state.current_round >= state.max_rounds:
            state.status = STATUS_WAITING_USER
            state.resume_from = RESUME_DEVELOPER
        elif state.mode == MODE_AUTO:
            state.status = STATUS_CHANGES_REQUESTED
            state.resume_from = RESUME_DEVELOPER
        else:
            state.status = STATUS_WAITING_USER
            state.resume_from = RESUME_DEVELOPER
    save_task(paths, state)


def advance_task(paths: PairPaths, config: TaskConfig, state: TaskState) -> TaskState:
    while True:
        if state.status in {STATUS_APPROVED, STATUS_FAILED, STATUS_CANCELLED}:  # type: ignore[name-defined]
            return state
        if state.resume_from == RESUME_DEVELOPER:
            run_developer_round(paths, config, state)
        if state.resume_from == RESUME_TEST:
            run_tests(paths, config, state)
        if state.resume_from == RESUME_REVIEWER:
            run_reviewer_round(paths, config, state)
        if state.status == STATUS_APPROVED:
            return state
        if (
            state.status == STATUS_CHANGES_REQUESTED
            and state.mode == MODE_AUTO
            and state.current_round < state.max_rounds
        ):
            state.current_round += 1
            state.resume_from = RESUME_DEVELOPER
            save_task(paths, state)
            continue
        if (
            state.status == STATUS_WAITING_USER
            and state.current_round < state.max_rounds
        ):
            return state
        if state.status == STATUS_CHANGES_REQUESTED:
            return state
        if state.status == STATUS_WAITING_USER:
            return state


def resume_task(paths: PairPaths) -> TaskState:
    config, state = load_current_task(paths)
    if (
        state.status == STATUS_WAITING_USER
        and state.last_review_status == "CHANGES_REQUESTED"
        and state.current_round < state.max_rounds
    ):
        state.current_round += 1
        state.resume_from = RESUME_DEVELOPER
        save_task(paths, state)
    return advance_task(paths, config, state)


def resume_task_from(paths: PairPaths, from_phase: str) -> TaskState:
    config, state = load_current_task(paths)
    state.resume_from = from_phase
    save_task(paths, state)
    return advance_task(paths, config, state)


def cancel_task(paths: PairPaths, reason: str | None = None) -> TaskState:
    config, state = load_current_task(paths)
    state.status = STATUS_CANCELLED
    state.cancelled_at = utc_now()
    state.cancellation_reason = reason or "cancelled by user"
    save_task(paths, state)
    return state


def intervene_task(
    paths: PairPaths,
    *,
    note: str | None = None,
    focus_only_blocking: bool | None = None,
    developer_model: str | None = None,
    reviewer_model: str | None = None,
    max_rounds: int | None = None,
) -> tuple[TaskConfig, TaskState]:
    config, state = load_current_task(paths)
    if focus_only_blocking is not None:
        config.focus_only_blocking = focus_only_blocking
    if developer_model is not None:
        config.developer_model = developer_model
    if reviewer_model is not None:
        config.reviewer_model = reviewer_model
    if max_rounds is not None:
        config.max_rounds = max_rounds
        state.max_rounds = max_rounds
    state.intervention_note = note or "manual intervention applied"
    state.intervention_count += 1
    save_config(paths.config_path(state.task_id), config)
    save_task(paths, state)
    return config, state
