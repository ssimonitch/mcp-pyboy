"""Run tests using pytest."""

import subprocess
import sys

from .utils import find_project_root


def main() -> None:
    """Run pytest on tests/ directory with verbose output."""
    project_root = find_project_root()
    tests_dir = project_root / "tests"

    # Use python -m to ensure we use the correct environment
    cmd = [sys.executable, "-m", "pytest", str(tests_dir), "-v"]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print("✓ Tests completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Tests failed: {e}", file=sys.stderr)
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(
            "✗ pytest not found. Make sure it's installed in the environment.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
