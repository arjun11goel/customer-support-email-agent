from pathlib import Path


PROMPTS_DIR = Path("prompts")


def load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""

    path = PROMPTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}"
        )

    return path.read_text(encoding="utf-8")