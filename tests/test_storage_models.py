import tempfile
import unittest
from pathlib import Path

from opencode_pair.models import MODE_SEMI_AUTO, TaskConfig, TaskState
from opencode_pair.storage import load_config, load_state, save_config, save_state


class StorageModelTests(unittest.TestCase):
    def test_config_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            config = TaskConfig(goal="Test goal", mode=MODE_SEMI_AUTO, max_rounds=4)
            save_config(path, config)
            loaded = load_config(path)
            self.assertEqual(loaded.goal, "Test goal")
            self.assertEqual(loaded.max_rounds, 4)

    def test_state_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            state = TaskState(
                version=1,
                task_id="pair-1",
                goal="Goal",
                status="initialized",
                mode=MODE_SEMI_AUTO,
                current_round=1,
                max_rounds=3,
                developer_model=None,
                reviewer_model=None,
                test_command=None,
                opencode_agent=None,
                workdir="/tmp/repo",
                protocol_version=1,
                prompt_version=1,
                created_at="2026-04-01T00:00:00Z",
                updated_at="2026-04-01T00:00:00Z",
            )
            save_state(path, state)
            loaded = load_state(path)
            self.assertEqual(loaded.task_id, "pair-1")
            self.assertEqual(loaded.goal, "Goal")
            self.assertEqual(loaded.current_round, 1)
            self.assertIsNone(loaded.last_warning)
