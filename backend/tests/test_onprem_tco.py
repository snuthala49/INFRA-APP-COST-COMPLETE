import os
import sys

# Ensure backend package modules are importable when running tests from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.onprem_tco import calculate_onprem_tco


def test_onprem_cost_structure_and_total_consistency():
    result = calculate_onprem_tco(cpu=4, ram=16, storage=200, network=20, backup=80)

    assert result["provider"] == "onprem"
    assert result["currency"] == "USD"
    assert result["total"] > 0
    assert set(result["breakdown"].keys()) == {
        "capex",
        "power",
        "facilities",
        "operations",
        "maintenance",
        "software_licensing",
        "network",
        "backup",
    }
    assert "capex_monthly" in result
    assert "opex_monthly" in result
    assert round(result["capex_monthly"] + result["opex_monthly"], 2) == result["total"]
    assert round(sum(result["breakdown"].values()), 2) == result["total"]
    assert "Per Garnter" in result["assumptions"]
    assert "1.4x redundancy" in result["assumptions"]
    assert "$0.12/kWh" in result["assumptions"]
    assert "ops 35% annually" in result["assumptions"]
    assert "maintenance 12% annually" in result["assumptions"]
    assert "software licensing $100/vCPU/year" in result["assumptions"]
    assert "network $0.02/GB" in result["assumptions"]
