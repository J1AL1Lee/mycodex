import tempfile
import unittest
from pathlib import Path

from mycodex.models import ExecutionContext
from mycodex.tools.apply_patch import execute_apply_patch


class ApplyPatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.context = ExecutionContext(
            workspace_root=self.root,
            cwd=self.root,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_patch(self, patch: str) -> str:
        return execute_apply_patch(
            {
                "type": "custom_tool_call",
                "call_id": "test_call",
                "name": "apply_patch",
                "input": patch,
            },
            self.context,
        )

    def test_add_file_creates_parent_directories(self) -> None:
        result = self.run_patch(
            "*** Begin Patch\n"
            "*** Add File: nested/hello.txt\n"
            "+hello\n"
            "+world\n"
            "*** End Patch"
        )

        self.assertEqual(result, "add: nested/hello.txt")
        self.assertEqual(
            (self.root / "nested" / "hello.txt").read_text(encoding="utf-8"),
            "hello\nworld\n",
        )

    def test_delete_file_removes_an_existing_file(self) -> None:
        target = self.root / "remove.txt"
        target.write_text("remove me\n", encoding="utf-8")

        result = self.run_patch(
            "*** Begin Patch\n"
            "*** Delete File: remove.txt\n"
            "*** End Patch"
        )

        self.assertEqual(result, "delete: remove.txt")
        self.assertFalse(target.exists())

    def test_update_file_replaces_multiple_chunks(self) -> None:
        target = self.root / "sample.txt"
        target.write_text("first\nold one\nmiddle\nold two\nlast\n", encoding="utf-8")

        result = self.run_patch(
            "*** Begin Patch\n"
            "*** Update File: sample.txt\n"
            "@@\n"
            "-old one\n"
            "+new one\n"
            "@@\n"
            "-old two\n"
            "+new two\n"
            "*** End Patch"
        )

        self.assertEqual(result, "update: sample.txt")
        self.assertEqual(
            target.read_text(encoding="utf-8"),
            "first\nnew one\nmiddle\nnew two\nlast\n",
        )

    def test_invalid_later_operation_does_not_apply_earlier_add(self) -> None:
        result = self.run_patch(
            "*** Begin Patch\n"
            "*** Add File: created.txt\n"
            "+created\n"
            "*** Update File: missing.txt\n"
            "@@\n"
            "-old\n"
            "+new\n"
            "*** End Patch"
        )

        self.assertIn("file does not exist: missing.txt", result)
        self.assertFalse((self.root / "created.txt").exists())

    def test_path_cannot_escape_workspace(self) -> None:
        result = self.run_patch(
            "*** Begin Patch\n"
            "*** Add File: ../outside.txt\n"
            "+nope\n"
            "*** End Patch"
        )

        self.assertIn("patch path is outside of workspace", result)


if __name__ == "__main__":
    unittest.main()
