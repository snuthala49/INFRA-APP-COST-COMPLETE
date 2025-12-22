import pytest
from utils.gcp_catalog import find_best_fit, price_month_from_hour


def test_gcp_find_best_fit_exact():
    """Test GCP catalog finds exact fit for 2 CPU, 8 GB RAM (n2-standard-2)."""
    result = find_best_fit(cpu=2, ram=8)
    assert result["sku"] == "n2-standard-2"
    assert result["vcpu"] == 2
    assert result["ram_gb"] == 8
    assert result["count"] == 1


def test_gcp_find_best_fit_scale():
    """Test GCP catalog scales up when exact fit not found."""
    result = find_best_fit(cpu=6, ram=32)
    # Should select largest SKU (n2-highmem-4: 4 vCPU) and scale by vCPU
    assert result["sku"] == "n2-highmem-4"
    assert result["count"] == 2  # ceil(6 / 4) = 2


def test_gcp_price_month_from_hour():
    """Test GCP monthly price calculation from hourly rate."""
    monthly = price_month_from_hour(hourly_price=0.1, instance_count=1)
    expected = 0.1 * 730 * 1  # 730 hours/month
    assert abs(monthly - expected) < 0.01
