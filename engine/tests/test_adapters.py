from crossmith.adapters.registry import discover_adapters
from crossmith.detection.engine import needs_manual_review, scan_project


def test_discover_adapters_empty_is_safe():
    # No adapters are registered yet (Phase 3 adds the Python adapter) — this
    # must return an empty iterator, not crash.
    assert list(discover_adapters()) == []


def test_scan_with_no_adapters_needs_manual_review(tmp_path):
    results = scan_project(tmp_path)
    assert results == []
    assert needs_manual_review(results) is True


def test_scan_endpoint_missing_path_returns_404(client):
    response = client.post("/projects/scan", json={"project_path": "/no/such/path"})
    assert response.status_code == 404


def test_scan_endpoint_existing_empty_dir(client, tmp_path):
    response = client.post("/projects/scan", json={"project_path": str(tmp_path)})
    assert response.status_code == 200
    body = response.json()
    assert body["matches"] == []
    assert body["needs_manual_review"] is True
