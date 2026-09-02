import os
from pathlib import Path
from .agents.agent import Agent
from .llm.deepseek import DeepSeekModelClient
from .tools.apply_patch import apply_patch_spec, execute_apply_patch
from .tools.registry import ToolRegistry
from .tools.shell import execute_shell, shell_spec
from .models import ExecutionContext


def main() -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if not api_key:
        print("Error: DEEPSEEK_API_KEY is not set.")
        return

    workspace = Path.cwd().resolve()

    registry = ToolRegistry()
    registry.register("shell", shell_spec, execute_shell)
    registry.register(
        "apply_patch",
        apply_patch_spec,
        execute_apply_patch,
    )

    model = DeepSeekModelClient(api_key=api_key)

    context = ExecutionContext(
        workspace_root=workspace,
        cwd=workspace,
    )

    agent = Agent(
        model_client=model,
        tool_registry=registry,
        context=context,
    )

    print(f"MyCodex workspace: {workspace}")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            prompt = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if prompt.lower() in {"exit", "quit"}:
            break

        if not prompt:
            continue

        try:
            result = agent.run(
                {
                    "type": "input_text",
                    "text": prompt,
                }
            )
            print(result["text"])
        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
