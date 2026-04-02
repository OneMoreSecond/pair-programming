import unittest

from opencode_pair.cli import build_parser, load_goal


class CliTests(unittest.TestCase):
    def test_parser_accepts_custom_prog_name(self) -> None:
        parser = build_parser("opencode pair")
        self.assertEqual(parser.prog, "opencode pair")

    def test_start_command_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["start", "--goal", "Build something"])
        self.assertEqual(args.command, "start")
        self.assertEqual(args.goal, "Build something")

    def test_start_command_accepts_workdir_after_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["start", "--workdir", ".", "--goal", "Build something"]
        )
        self.assertEqual(args.command, "start")
        self.assertEqual(args.workdir, ".")

    def test_review_round_argument_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["review", "--round", "2"])
        self.assertEqual(args.command, "review")
        self.assertEqual(args.round_number, 2)

    def test_artifacts_round_argument_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["artifacts", "--round", "2"])
        self.assertEqual(args.command, "artifacts")
        self.assertEqual(args.round_number, 2)

    def test_status_json_and_verbose_parse(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["status", "--json", "--verbose", "--task-id", "pair-1"]
        )
        self.assertEqual(args.command, "status")
        self.assertTrue(args.as_json)
        self.assertTrue(args.verbose)
        self.assertEqual(args.task_id, "pair-1")

    def test_resume_from_phase_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["resume", "--from", "reviewer"])
        self.assertEqual(args.command, "resume")
        self.assertEqual(args.from_phase, "reviewer")

    def test_config_json_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["config", "--json"])
        self.assertEqual(args.command, "config")
        self.assertTrue(args.as_json)

    def test_stop_reason_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["stop", "--reason", "user requested stop"])
        self.assertEqual(args.command, "stop")
        self.assertEqual(args.reason, "user requested stop")

    def test_intervene_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "intervene",
                "--focus-only-blocking",
                "--developer-model",
                "model-a",
                "--max-rounds",
                "5",
            ]
        )
        self.assertEqual(args.command, "intervene")
        self.assertTrue(args.focus_only_blocking)
        self.assertEqual(args.developer_model, "model-a")
        self.assertEqual(args.max_rounds, 5)

    def test_history_json_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["history", "--json", "--task-id", "pair-1"])
        self.assertEqual(args.command, "history")
        self.assertTrue(args.as_json)
        self.assertEqual(args.task_id, "pair-1")

    def test_metrics_json_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["metrics", "--json", "--task-id", "pair-1"])
        self.assertEqual(args.command, "metrics")
        self.assertTrue(args.as_json)
        self.assertEqual(args.task_id, "pair-1")

    def test_eval_parses_multiple_task_files(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["eval", "--task-file", "one.md", "--task-file", "two.md", "--json"]
        )
        self.assertEqual(args.command, "eval")
        self.assertEqual(args.task_files, ["one.md", "two.md"])
        self.assertTrue(args.as_json)

    def test_prompt_profile_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["start", "--goal", "Build", "--prompt-profile", "frontend"]
        )
        self.assertEqual(args.command, "start")
        self.assertEqual(args.prompt_profile, "frontend")

    def test_goal_file_argument_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["start", "--goal-file", "task.md"])
        self.assertEqual(args.command, "start")
        self.assertEqual(args.goal_file, "task.md")

    def test_load_goal_prefers_inline_goal(self) -> None:
        self.assertEqual(load_goal("Inline goal", None), "Inline goal")
