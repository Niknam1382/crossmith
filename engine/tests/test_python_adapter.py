from pathlib import Path

import pytest

from crossmith.adapters.python_adapter import PythonAdapter


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_detects_main_py_with_no_dependencies(tmp_path: Path):
    _write(tmp_path / "main.py", "print('hi')")

    result = PythonAdapter().detect(tmp_path)

    assert result.matched is True
    assert result.language == "python"
    assert result.entry_point == "main.py"
    assert result.dependencies == []
    assert result.confidence >= 0.6


def test_confidence_increases_with_pyproject_and_requirements(tmp_path: Path):
    _write(tmp_path / "main.py", "print('hi')")
    _write(tmp_path / "requirements.txt", "requests==2.32.0\nclick>=8.0\n")
    _write(tmp_path / "pyproject.toml", "[project]\nname = 'x'\nversion = '0'\n")

    result = PythonAdapter().detect(tmp_path)

    assert result.matched is True
    assert result.dependencies == ["requests==2.32.0", "click>=8.0"]
    # main.py (+0.2) + pyproject.toml (+0.1) + has deps (+0.05) over the 0.6 base
    assert result.confidence == pytest.approx(0.95)


def test_falls_back_to_single_py_file(tmp_path: Path):
    _write(tmp_path / "weird_name.py", "print('hi')")

    result = PythonAdapter().detect(tmp_path)

    assert result.matched is True
    assert result.entry_point == "weird_name.py"
    # No recognized filename bonus, no pyproject.toml, no deps -> base confidence only
    assert result.confidence == 0.6


def test_no_match_on_ambiguous_multi_file_project(tmp_path: Path):
    _write(tmp_path / "a.py", "")
    _write(tmp_path / "b.py", "")

    result = PythonAdapter().detect(tmp_path)

    assert result.matched is False
    assert result.confidence == 0.0


def test_no_match_on_empty_directory(tmp_path: Path):
    result = PythonAdapter().detect(tmp_path)
    assert result.matched is False


def test_pyproject_dependencies_used_when_no_requirements_txt(tmp_path: Path):
    _write(tmp_path / "main.py", "")
    _write(
        tmp_path / "pyproject.toml",
        "[project]\nname = 'x'\nversion = '0'\ndependencies = ['httpx']\n",
    )

    result = PythonAdapter().detect(tmp_path)

    assert result.dependencies == ["httpx"]


def test_requirements_txt_takes_priority_over_pyproject(tmp_path: Path):
    _write(tmp_path / "main.py", "")
    _write(tmp_path / "requirements.txt", "requests\n")
    _write(
        tmp_path / "pyproject.toml",
        "[project]\nname = 'x'\nversion = '0'\ndependencies = ['httpx']\n",
    )

    result = PythonAdapter().detect(tmp_path)

    assert result.dependencies == ["requests"]
