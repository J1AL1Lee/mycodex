# mycodex

A minimal Codex-style coding agent built for learning how agent loops and tool calls work.

The current implementation supports this flow:

```text
User input
  ↓
Call the DeepSeek model
  ↓
The model returns a shell tool call
  ↓
Validate and execute the tool
  ↓
Append the tool result to the message history
  ↓
Call the model again
  ↓
Return the model's final text response
```

## Implemented

- Abstract `ModelClient` interface
- `FakeModelClient` for deterministic tests
- DeepSeek Responses API client
- Agent loop
- Tool registry and dispatch
- Shell tool with argument validation
- Tool call/output pairing through `call_id`
- Working directory, timeout, and output-size limits

## Not Implemented Yet

- `apply_patch`
- Shell sandboxing and execution approval
- Interactive or background shell sessions
- Comprehensive error handling and automated tests

## Requirements

- Python 3.11 or newer
- A DeepSeek API key

Install the OpenAI Python SDK, which is compatible with the DeepSeek API:

```powershell
python -m pip install openai
```

## Configuration

Set your DeepSeek API key in PowerShell:

```powershell
$env:DEEPSEEK_API_KEY = "your-api-key"
```

Never hard-code an API key or commit one to Git.

## Running the Example

The repository directory must be named `mycodex`. Run the module from its parent directory:

```powershell
cd path\to\parent
python -m mycodex.test
```

The example asks the model to call the shell tool and execute:

```text
echo Hello World
```

## Project Structure

```text
mycodex/
├── agents/
│   └── agent.py          # Agent loop
├── llm/
│   ├── base.py           # ModelClient interface
│   ├── deepseek.py       # DeepSeek client
│   └── tests/fake.py     # Fake model client
├── tools/
│   ├── registry.py       # Tool registration and dispatch
│   └── shell.py          # Shell tool
├── types.py              # Messages, tool calls, and execution context
└── test.py               # End-to-end example
```

## Security Warning

The current shell tool executes model-generated commands directly through `subprocess`. It does not provide sandboxing or human approval. Run it only in a controlled learning environment, never in production or in a directory containing important data.
