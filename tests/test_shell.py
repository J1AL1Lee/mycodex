import json
import tempfile
import unittest
from pathlib import Path

from mycodex.models import ExecutionContext
from mycodex.tools.shell import execute_shell


class ShellToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.context = ExecutionContext(
            workspace_root=self.root,
            cwd=self.root,
            command_approval=lambda command: True,
        )

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

    def test_shell_does_not_execute_a_rejected_command(self) -> None:
        target = self.root / "should-not-exist.txt"
        denied_context = ExecutionContext(
            workspace_root=self.root,
            cwd=self.root,
            command_approval=lambda command: False,
        )

        result = execute_shell(
            {
                "type": "function_call",
                "call_id": "shell_3",
                "name": "shell",
                "arguments": json.dumps(
                    {"command": "echo blocked > should-not-exist.txt"}
                ),
            },
            denied_context,
        )

        self.assertEqual(result, "Command denied by user")
        self.assertFalse(target.exists())

    def test_shell_blocks_commands_without_an_approval_handler(self) -> None:
        context_without_approval = ExecutionContext(
            workspace_root=self.root,
            cwd=self.root,
        )

        result = execute_shell(
            {
                "type": "function_call",
                "call_id": "shell_4",
                "name": "shell",
                "arguments": json.dumps({"command": "echo blocked"}),
            },
            context_without_approval,
        )

        self.assertEqual(
            result,
            "Command blocked: no approval handler is configured.",
        )


if __name__ == "__main__":
    unittest.main()
