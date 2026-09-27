from crossmith.adapters.registry import discover_adapters
from crossmith.detection.engine import needs_manual_review, scan_project


def test_discover_adapters_finds_the_python_adapter():
    # As of Phase 3, the first-party Python adapter is always registered.
    # The registry itself must still never crash even if a future adapter
    # is broken (see registry.py's try/except) — that part isn't
    # re-testable without a deliberately broken plugin, so it's covered by
    # code review rather than a unit test here.
    names = [adapter.name for adapter in discover_adapters()]
    assert "python" in names


def test_scan_with_no_matching_adapter_needs_manual_review(tmp_path):
    # An empty directory matches no adapter, registered or not.
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
