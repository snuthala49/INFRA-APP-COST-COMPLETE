import os
import sys

# Ensure backend package modules are importable when running tests from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cloud_providers.azure import azure_cost


def test_azure_cost_positive_and_structure():
    r = azure_cost(cpu=2, ram=8, storage=100, network=10, backup=50)
    assert isinstance(r, dict)
    assert r["provider"] == "azure"
    assert "total" in r and isinstance(r["total"], (int, float))
    assert r["total"] > 0
    assert round(sum(r["breakdown"].values()), 2) == r["total"]
