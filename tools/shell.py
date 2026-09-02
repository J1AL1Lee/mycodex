import subprocess
import json
from ..models import ExecutionContext, ToolCall, ToolSpec

shell_spec: ToolSpec = {
    "type": "function",
    "name": "shell",
    "description": "Execute shell and return the output. The input is a shell command string.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute.",
            }
        },
        "required": ["command"],
        "additionalProperties": False,
    },
}


def execute_shell(
    call: ToolCall,
    context: ExecutionContext,
) -> str:
    if call["type"] != "function_call":
        return "Invalid tool call: shell requires a function_call."

    try:
        arguments = json.loads(call["arguments"])
    except json.JSONDecodeError as error:
        return f"Invalid JSON arguments: {error}"

    if not isinstance(arguments, dict):
        return "Invalid arguments: expected a JSON object."

    if set(arguments) != {"command"}:
        return "Invalid arguments: expected only 'command'."

    command = arguments.get("command")

    if not isinstance(command, str) or not command.strip():
        return "Invalid arguments: 'command' must be a non-empty string."

    try:
        completed = subprocess.run(
            command,
            cwd=context.cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=context.timeout_ms / 1000.0,  # Convert milliseconds to seconds
        )
    except subprocess.TimeoutExpired:
        return f"Command timed out after {context.timeout_ms} milliseconds."
    except OSError as error:
        return f"Failed to execute command: {error}"

    result = (
        f"exit_code: {completed.returncode}\n"
        f"stdout: {completed.stdout}\n"
        f"stderr: {completed.stderr}"
    )
    return result.encode("utf-8")[: context.max_output_bytes].decode(
        "utf-8",
        errors="ignore",
    )
