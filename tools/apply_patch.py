from ..models import ExecutionContext, ToolCall, ToolSpec
from dataclasses import dataclass
from typing import Literal
from pathlib import Path

apply_patch_spec: ToolSpec = {
    "type": "custom",
    "name": "apply_patch",
    "description": (
        "Modify files using a patch. "
        "Input must start with '*** Begin Patch' and end with "
        "'*** End Patch'. Supports Add File, Delete File, and Update File."
    )
}

@dataclass(frozen=True, slots=True)
class UpdateChunk:
    old_lines: list[str]
    new_lines: list[str]

def execute_apply_patch(
    call: ToolCall,
    context: ExecutionContext,
) -> str:
    if call["type"] != "custom_tool_call":
        return "Invalid tool call: apply_patch requires a custom_tool_call."

    patch = call["input"]

    if not patch.startswith("*** Begin Patch"):
        return "Invalid patch format: missing '*** Begin Patch' header."
    if not patch.rstrip().endswith("*** End Patch"):
        return "Invalid patch format: missing '*** End Patch' footer."

    try:
        operations = parse_patch(patch)
        targets = [
            resolve_patch_path(operation.path, context) for operation in operations
        ]
        # Prepare updated file contents before writing anything.
        if len(set(targets)) != len(targets):
            raise ValueError(
                "multiple operations on the same file are not allowed"
            )

        prepared_updates: dict[Path, str] = {}

        # Validate every operation before mutating the workspace.
        for operation, target in zip(operations, targets, strict=True):
            if operation.kind == "add":
                if target.exists():
                    raise ValueError(f"file already exists: {operation.path}")

            elif operation.kind == "delete":
                if not target.exists():
                    raise ValueError(f"file does not exist: {operation.path}")
                if not target.is_file():
                    raise ValueError(f"target is not a file: {operation.path}")

            elif operation.kind == "update":
                if not target.exists():
                    raise ValueError(f"file does not exist: {operation.path}")
                if not target.is_file():
                    raise ValueError(f"target is not a file: {operation.path}")

                source_text = target.read_text(encoding="utf-8")
                source_lines = source_text.splitlines()

                chunks = parse_update_chunks(operation.body)
                updated_lines = apply_update_chunks(source_lines, chunks)
                updated_text = "\n".join(updated_lines)

                # Preserve whether the original file ended with a newline.
                if source_text.endswith(("\n", "\r")):
                    updated_text += "\n"

                prepared_updates[target] = updated_text

            else:
                raise ValueError(f"operation is not implemented yet: {operation.kind}")

        # All checks passed; now mutate the workspace.
        for operation, target in zip(operations, targets, strict=True):
            if operation.kind == "add":
                target.parent.mkdir(parents=True, exist_ok=True)
                content = "\n".join(line[1:] for line in operation.body) + "\n"

                target.write_text(
                    content,
                    encoding="utf-8",
                    newline="\n",
                )
            elif operation.kind == "delete":
                target.unlink()
            elif operation.kind == "update":
                target.write_text(
                    prepared_updates[target],
                    encoding="utf-8",
                    newline="\n",
                )
    except (ValueError, OSError) as e:
        return f"Apply patch failed: {e}"

    return "\n".join(f"{operation.kind}: {operation.path}" for operation in operations)


@dataclass(frozen=True, slots=True)
class PatchOperation:
    kind: Literal["add", "update", "delete"]
    path: str
    body: list[str]


def parse_patch(patch: str) -> list[PatchOperation]:
    lines = patch.rstrip("\r\n").splitlines()

    body = lines[1:-1]  # Exclude the first and last lines (headers)
    operations: list[PatchOperation] = []
    index = 0

    headers = {
        "*** Add File:": "add",
        "*** Update File:": "update",
        "*** Delete File:": "delete",
    }

    while index < len(body):
        header = body[index]

        kind = None
        path = None

        for prefix, operation_kind in headers.items():
            if header.startswith(prefix):
                kind = operation_kind
                path = header[len(prefix) :].strip()
                break

        if kind is None:
            raise ValueError(f"expected file operation, got: {header}")

        if not path:
            raise ValueError("file path cannot be empty")

        index += 1
        operation_body: list[str] = []

        # Read until the next file header or the end of the patch.
        while index < len(body):
            if any(body[index].startswith(prefix) for prefix in headers):
                break

            operation_body.append(body[index])
            index += 1

        if kind == "add":
            if not operation_body:
                raise ValueError(f"add file has no content: {path}")

            if any(not line.startswith("+") for line in operation_body):
                raise ValueError(f"add file lines must start with '+': {path}")

        elif kind == "delete":
            if operation_body:
                raise ValueError(f"delete file must not have a body: {path}")

        elif kind == "update":
            if not operation_body:
                raise ValueError(f"update file has no changes: {path}")

        operations.append(PatchOperation(kind=kind, path=path, body=operation_body))

    if not operations:
        raise ValueError("patch must contain at least one operation")

    return operations


def resolve_patch_path(
    path: str,
    context: ExecutionContext,
) -> Path:
    raw_path = Path(path)

    if raw_path.is_absolute():
        raise ValueError(f"absolute path is not allowed: {path}")

    workspace_root = context.workspace_root.resolve()
    target_path = (context.cwd / raw_path).resolve()

    if not target_path.is_relative_to(workspace_root):
        raise ValueError(f"patch path is outside of workspace: {path}")

    return target_path

def parse_update_chunks(body: list[str]) -> list[UpdateChunk]:
    chunks: list[UpdateChunk] = []

    old_lines: list[str] | None = None
    new_lines: list[str] | None = None
    has_changes = False

    for line in body:
        if line == "@@":
            # 保存上一个区块
            if old_lines is not None and new_lines is not None:
                if not has_changes:
                    raise ValueError("update chunk has no changes")

                if not old_lines:
                    raise ValueError("update chunk must contain an old or context line")

                chunks.append(
                    UpdateChunk(
                        old_lines=old_lines,
                        new_lines=new_lines,
                    )
                )

            # Start a new update chunk.
            old_lines = []
            new_lines = []
            has_changes = False
            continue

        if old_lines is None or new_lines is None:
            raise ValueError("update body must start with '@@'")

        if not line:
            raise ValueError("update line is missing a prefix")

        prefix = line[0]
        text = line[1:]

        if prefix == " ":
            old_lines.append(text)
            new_lines.append(text)

        elif prefix == "-":
            old_lines.append(text)
            has_changes = True

        elif prefix == "+":
            new_lines.append(text)
            has_changes = True

        else:
            raise ValueError(f"update line has invalid prefix: {line}")

    if old_lines is None or new_lines is None:
        raise ValueError("update body must contain at least one '@@'")

    if not has_changes:
        raise ValueError("update chunk has no changes")

    if not old_lines:
        raise ValueError("update chunk must contain an old or context line")

    chunks.append(
        UpdateChunk(
            old_lines=old_lines,
            new_lines=new_lines,
        )
    )

    return chunks

def apply_update_chunks(
    source_lines: list[str],
    chunks: list[UpdateChunk],
) -> list[str]:
    result = source_lines.copy()
    search_start = 0

    for chunk in chunks:
        old_lines = chunk.old_lines
        old_count = len(old_lines)

        matches = [
            index
            for index in range(
                search_start,
                len(result) - old_count + 1,
            )
            if result[index : index + old_count] == old_lines
        ]

        if not matches:
            raise ValueError(f"update was not found: {old_lines}")

        if len(matches) > 1:
            raise ValueError(f"update is ambiguous: {old_lines}")

        index = matches[0]
        result[index : index + old_count] = chunk.new_lines

        # The next chunk must match after this replacement.
        search_start = index + len(chunk.new_lines)

    return result
