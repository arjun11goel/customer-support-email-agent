from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = PROJECT_ROOT / "prompts"


def load_prompt(filename: str) -> str:
    """Load a prompt file from the project's prompts folder."""
    prompt_path = (PROMPTS_DIR / filename).resolve()

    try:
        prompt_path.relative_to(PROMPTS_DIR.resolve())
    except ValueError as exc:
        raise ValueError("Prompt files must be inside the prompts folder.") from exc

    if not prompt_path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")