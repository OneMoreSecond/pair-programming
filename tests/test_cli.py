import unittest

from opencode_pair.cli import build_parser, load_goal


class CliTests(unittest.TestCase):
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

    def test_goal_file_argument_parses(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["start", "--goal-file", "task.md"])
        self.assertEqual(args.command, "start")
        self.assertEqual(args.goal_file, "task.md")

    def test_load_goal_prefers_inline_goal(self) -> None:
        self.assertEqual(load_goal("Inline goal", None), "Inline goal")
