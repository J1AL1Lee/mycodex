import json
import tempfile
import unittest
from pathlib import Path

from mycodex.models import ExecutionContext
from mycodex.tools.shell import execute_shell


class ShellToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.context = ExecutionContext(workspace_root=root, cwd=root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_shell_executes_a_command(self) -> None:
        result = execute_shell(
            {
                "type": "function_call",
                "call_id": "shell_1",
                "name": "shell",
                "arguments": json.dumps({"command": "echo hello-from-shell"}),
            },
            self.context,
        )

        self.assertIn("exit_code: 0", result)
        self.assertIn("hello-from-shell", result)

    def test_shell_rejects_unexpected_arguments(self) -> None:
        result = execute_shell(
            {
                "type": "function_call",
                "call_id": "shell_2",
                "name": "shell",
                "arguments": json.dumps({"command": "echo hello", "extra": True}),
            },
            self.context,
        )

        self.assertEqual(
            result,
            "Invalid arguments: expected only 'command'.",
        )


if __name__ == "__main__":
    unittest.main()
