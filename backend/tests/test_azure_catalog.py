import pytest
from utils.azure_catalog import find_best_fit, price_month_from_hour


def test_azure_find_best_fit_exact():
    """Test Azure catalog finds exact fit for 2 CPU, 8 GB RAM (Standard_B2ms)."""
    result = find_best_fit(cpu=2, ram=8)
    assert result["sku"] == "Standard_B2ms"
    assert result["vcpu"] == 2
    assert result["ram_gb"] == 8
    assert result["count"] == 1


def test_azure_find_best_fit_scale():
    """Test Azure catalog scales up when exact fit not found."""
    result = find_best_fit(cpu=8, ram=64)
    # Should select largest SKU and scale by vCPU
    assert result["sku"] == "Standard_E4s_v3"
    assert result["count"] == 2  # ceil(8 / 4) = 2


def test_azure_price_month_from_hour():
    """Test Azure monthly price calculation from hourly rate."""
    monthly = price_month_from_hour(hourly_price=0.1, instance_count=1)
    expected = 0.1 * 730 * 1  # 730 hours/month
    assert abs(monthly - expected) < 0.01
