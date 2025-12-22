import json
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils.aws_price_sync as sync_mod


class DummyPricingClient:
    def get_products(self, ServiceCode=None, Filters=None, FormatVersion=None):
        # Simulate an OnDemand product response with pricePerUnit USD
        price_list = []
        sku = next((f['Value'] for f in Filters if f['Field'] == 'instanceType'), None)
        if sku:
            product = {
                'product': {'attributes': {'instanceType': sku}},
                'terms': {
                    'OnDemand': {
                        'term1': {
                            'priceDimensions': {
                                'pd1': {
                                    'pricePerUnit': {'USD': '0.1234'}
                                }
                            }
                        }
                    }
                }
            }
            price_list.append(json.dumps(product))
        return {'PriceList': price_list}


def test_get_pricing_for_sku_monkeypatch(monkeypatch):
    client = DummyPricingClient()
    price = sync_mod._get_pricing_for_sku(client, 'm5.large')
    assert price == 0.1234


def test_sync_prices_writes_cache(monkeypatch, tmp_path):
    # patch constants to use tmp paths and dummy client
    monkeypatch.setattr(sync_mod, 'CATALOG_PATH', tmp_path / 'catalog.json')
    monkeypatch.setattr(sync_mod, 'CACHE_PATH', tmp_path / 'cache.json')
    sample_catalog = [{'sku': 'm5.large', 'family': 'm5', 'vcpu': 2, 'ram_gb': 8, 'price_per_hour': 0.0}]
    (tmp_path / 'catalog.json').write_text(json.dumps(sample_catalog))

    def dummy_client_factory(name, region_name=None):
        return DummyPricingClient()

    monkeypatch.setattr(sync_mod, 'boto3', SimpleNamespace(client=dummy_client_factory))

    updated = sync_mod.sync_prices(write_back=False)
    assert 'm5.large' in updated
    cache = json.loads((tmp_path / 'cache.json').read_text())
    assert cache['m5.large'] == 0.1234


def test_get_pricing_for_sku_public():
    offerings = {
        'products': {
            'prod1': {
                'attributes': {
                    'instanceType': 'm5.large',
                    'location': 'US East (N. Virginia)',
                    'operatingSystem': 'Linux',
                    'tenancy': 'Shared'
                }
            }
        },
        'terms': {
            'OnDemand': {
                'prod1': {
                    'term1': {
                        'priceDimensions': {
                            'pd1': {
                                'pricePerUnit': {'USD': '0.5678'}
                            }
                        }
                    }
                }
            }
        }
    }
    price = sync_mod._get_pricing_for_sku_public(offerings, 'm5.large', 'US East (N. Virginia)')
    assert price == 0.5678


def test_sync_prices_public_writes_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(sync_mod, 'CATALOG_PATH', tmp_path / 'catalog.json')
    monkeypatch.setattr(sync_mod, 'CACHE_PATH', tmp_path / 'cache.json')
    sample_catalog = [{'sku': 'm5.large', 'family': 'm5', 'vcpu': 2, 'ram_gb': 8, 'price_per_hour': 0.0}]
    (tmp_path / 'catalog.json').write_text(json.dumps(sample_catalog))

    # Mock public offerings
    sample_offerings = {
        'products': {
            'prod1': {
                'attributes': {
                    'instanceType': 'm5.large',
                    'location': 'US East (N. Virginia)',
                    'operatingSystem': 'Linux',
                    'tenancy': 'Shared'
                }
            }
        },
        'terms': {
            'OnDemand': {
                'prod1': {
                    'term1': {
                        'priceDimensions': {
                            'pd1': {'pricePerUnit': {'USD': '0.5678'}}
                        }
                    }
                }
            }
        }
    }

    def mock_download(*args, **kwargs):
        return sample_offerings

    monkeypatch.setattr(sync_mod, '_download_public_offerings', mock_download)

    updated = sync_mod.sync_prices_public(write_back=False)
    assert 'm5.large' in updated
    cache = json.loads((tmp_path / 'cache.json').read_text())
    assert cache['m5.large'] == 0.5678
