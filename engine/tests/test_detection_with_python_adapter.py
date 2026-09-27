from pathlib import Path

from crossmith.adapters.registry import discover_adapters
from crossmith.detection.engine import needs_manual_review, scan_project


def test_python_adapter_is_discoverable():
    names = [adapter.name for adapter in discover_adapters()]
    assert "python" in names


def test_scan_project_finds_python_project(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hi')")

    results = scan_project(tmp_path)

    assert len(results) == 1
    assert results[0].language == "python"
    assert needs_manual_review(results) is False


def test_scan_endpoint_finds_python_project(client, tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hi')")

    response = client.post("/projects/scan", json={"project_path": str(tmp_path)})

    assert response.status_code == 200
    body = response.json()
    assert body["needs_manual_review"] is False
    assert body["matches"][0]["language"] == "python"
