import os
import sys
import math

# Ensure backend package modules are importable when running tests from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cloud_providers.aws import aws_cost


def test_aws_cost_positive_and_structure():
    r = aws_cost(cpu=2, ram=8, storage=100, network=10, backup=50)
    assert isinstance(r, dict)
    assert r["provider"] == "aws"
    assert "total" in r and isinstance(r["total"], (int, float))
    assert r["total"] >= 0
    assert math.isclose(r["breakdown"]["instance"] + r["breakdown"]["storage"] + r["breakdown"]["network"] + r["breakdown"]["backup"], r["total"], rel_tol=1e-6)

