from pathlib import Path
import subprocess


def normalize_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        return path.resolve()

    return path


def run_cmd(cmd, cwd=None, stdout=None, stderr=None, capture_output=False, text=True, check=False):
    """Run subprocess command with configurable stdout and stderr, raise on error."""
    return subprocess.run(cmd, cwd=cwd, stdout=stdout, stderr=stderr, check=check, capture_output=capture_output, text=text)
