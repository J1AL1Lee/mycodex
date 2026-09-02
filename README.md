# MyCodex

MyCodex is a minimal Codex-style coding agent built to learn the core agent loop:

```text
User input
  -> model call
  -> shell or apply_patch tool call
  -> tool validation and execution
  -> tool result added to history
  -> model call
  -> final text response
```

It is intentionally small and educational, not a production coding agent.

## Features

- Interactive command-line chat with persistent conversation history
- DeepSeek client through the OpenAI Python SDK and Responses API
- `shell` function tool with JSON argument validation, timeout, and output limits
- `apply_patch` custom tool with safe workspace-relative paths
- `apply_patch` support for add, delete, and simple update operations
- Offline automated tests using `unittest` and `FakeModelClient`

## Requirements

- Python 3.10 or newer
- A DeepSeek API key

## Install

```powershell
git clone https://github.com/J1AL1Lee/mycodex.git
cd mycodex
python -m pip install -e .
```

The editable install provides a `mycodex` command and installs the required `openai` SDK.

Set the API key for the current PowerShell session:

```powershell
$env:DEEPSEEK_API_KEY = "your-api-key"
```

Never commit an API key.

## Run

Change into the workspace you want the agent to operate on, then run:

```powershell
mycodex
```

You can also run:

```powershell
python -m mycodex
```

Type `exit` or `quit` to leave the session. The same `Agent` object is reused throughout a session, so each new prompt keeps the previous history.

Example prompt:

```text
Use apply_patch to create hello.txt containing Hello from MyCodex.
```

## Run tests

The automated test suite is offline: it does not call DeepSeek and does not require an API key.

```powershell
python -m unittest discover -s tests -v
```

The tests cover the add, delete, update, path-validation, and all-or-nothing preflight behavior of `apply_patch`, plus the full Agent -> custom tool -> final text loop with `FakeModelClient`.

## Project layout

```text
mycodex/
├── main.py                 # Interactive CLI implementation
├── __main__.py             # Enables: python -m mycodex
├── models.py               # Messages, tool calls, and execution context
├── agents/agent.py         # Agent loop
├── llm/
│   ├── base.py             # ModelClient interface
│   ├── deepseek.py         # DeepSeek client
│   └── tests/fake.py       # Deterministic model for tests
├── tools/
│   ├── registry.py         # Tool registration and dispatch
│   ├── shell.py            # Shell tool
│   └── apply_patch.py      # Custom patch tool
└── tests/                  # Offline automated tests
```

## Current limits

`apply_patch` intentionally supports only a small subset of the official format. It does not support `*** Move to`, `*** End of File`, or named `@@` context headers.

The shell tool executes model-generated commands through `subprocess` without sandboxing or interactive approval. Use MyCodex only in a controlled learning workspace, never in production or around important data.
