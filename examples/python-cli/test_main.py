import subprocess
import sys
from pathlib import Path

MAIN = Path(__file__).parent / "main.py"


def test_greets_by_name():
    result = subprocess.run(
        [sys.executable, str(MAIN), "Crossmith"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Hello, Crossmith!" in result.stdout


def test_defaults_to_world():
    result = subprocess.run([sys.executable, str(MAIN)], capture_output=True, text=True)
    assert "Hello, world!" in result.stdout
