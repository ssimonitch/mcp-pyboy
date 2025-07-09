"""Format code using Black."""

import subprocess
import sys

from .utils import find_project_root


def main() -> None:
    """Run Black code formatter on src/ and tests/ directories."""
    project_root = find_project_root()
    src_dir = project_root / "src"
    tests_dir = project_root / "tests"

    # Use python -m to ensure we use the correct environment
    cmd = [sys.executable, "-m", "black", str(src_dir), str(tests_dir)]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print("✓ Code formatting completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Formatting failed: {e}", file=sys.stderr)
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(
            "✗ Black not found. Make sure it's installed in the environment.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
