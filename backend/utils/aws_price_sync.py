"""AWS Pricing sync utilities

Provides a small CLI to refresh hourly on-demand prices for SKUs in
`backend/data/aws_catalog.json` using either:
  1. The AWS Pricing API (boto3) — requires AWS credentials
  2. Public EC2 offerings JSON — no credentials required (recommended)

Usage (local, public mode — no credentials needed):
  python -m utils.aws_price_sync --public --write-catalog

Usage (with boto3, requires AWS credentials):
  python -m utils.aws_price_sync --write-catalog

The script writes a cache file at `backend/cache/aws_prices.json` and optionally
overwrites the catalog with updated `price_per_hour` values when `--write-catalog`
is passed.
"""
import argparse
import json
import logging
from pathlib import Path
from typing import Optional, Dict

try:
    import boto3
except Exception:  # pragma: no cover - boto3 may not be available in test env
    boto3 = None

try:
    import requests
except Exception:
    requests = None

LOG = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
CATALOG_PATH = BASE_DIR / 'data' / 'aws_catalog.json'
CACHE_DIR = BASE_DIR / 'cache'
CACHE_DIR.mkdir(exist_ok=True)
CACHE_PATH = CACHE_DIR / 'aws_prices.json'

# Public EC2 offerings URL
PUBLIC_EC2_OFFERINGS_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"


def _get_pricing_for_sku_public(offerings_data: dict, sku: str, location: str = 'US East (N. Virginia)') -> Optional[float]:
    """Extract hourly USD price from parsed public EC2 offerings JSON.

    Returns hourly USD price for the on-demand Linux usage, or None.
    """
    try:
        products = offerings_data.get('products', {})
        terms = offerings_data.get('terms', {})

        # Find product matching the SKU and location
        for product_key, product in products.items():
            attrs = product.get('attributes', {})
            if (attrs.get('instanceType') == sku and
                attrs.get('location') == location and
                attrs.get('operatingSystem') == 'Linux' and
                attrs.get('tenancy') == 'Shared'):  # Filter to shared tenancy only

                # Look up OnDemand terms for this product
                on_demand = terms.get('OnDemand', {}).get(product_key, {})
                for term_key, term in on_demand.items():
                    dims = term.get('priceDimensions', {})
                    for dim in dims.values():
                        price_str = dim.get('pricePerUnit', {}).get('USD')
                        if price_str:
                            try:
                                return float(price_str)
                            except (ValueError, TypeError):
                                continue

        return None
    except Exception as e:
        LOG.exception('Error extracting pricing from offerings for %s: %s', sku, e)
        return None


def _get_pricing_for_sku(client, sku: str, location: str = 'US East (N. Virginia)') -> Optional[float]:
    """Query the AWS Pricing 'get_products' API for a given instance type SKU.

    Returns hourly USD price for the on-demand Linux usage in the provided location, or None.
    """
    try:
        filters = [
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': sku},
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
        ]
        resp = client.get_products(ServiceCode='AmazonEC2', Filters=filters, FormatVersion='aws_v1')
        price_list = resp.get('PriceList', [])
        if not price_list:
            return None

        # PriceList is a list of JSON strings; pick first and parse OnDemand terms
        for item in price_list:
            data = json.loads(item)
            terms = data.get('terms', {})
            on_demand = terms.get('OnDemand', {})
            for term in on_demand.values():
                dims = term.get('priceDimensions', {})
                for dim in dims.values():
                    price = dim.get('pricePerUnit', {}).get('USD')
                    if price:
                        try:
                            return float(price)
                        except Exception:
                            continue
        return None
    except Exception as e:
        LOG.exception('Error fetching pricing for %s: %s', sku, e)
        return None


def _download_public_offerings(location: str = 'US East (N. Virginia)') -> Optional[dict]:
    """Download and parse the public EC2 offerings JSON.

    Returns the parsed offerings data or None on failure.
    """
    if requests is None:
        raise RuntimeError('requests is required for --public mode; install it or use boto3 mode instead')

    LOG.info('Downloading public EC2 offerings from %s', PUBLIC_EC2_OFFERINGS_URL)
    try:
        resp = requests.get(PUBLIC_EC2_OFFERINGS_URL, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        LOG.info('Downloaded offerings; products: %d, terms: %d', len(data.get('products', {})), len(data.get('terms', {})))
        return data
    except Exception as e:
        LOG.exception('Error downloading public offerings: %s', e)
        return None


def sync_prices_public(write_back: bool = False, location: str = 'US East (N. Virginia)') -> dict:
    """Load catalog, fetch public EC2 offerings, extract prices, write cache and optionally update catalog.

    Returns a mapping { sku: price_per_hour_or_None }.
    """
    offerings = _download_public_offerings(location=location)
    if offerings is None:
        raise RuntimeError('Failed to download or parse public offerings')

    catalog = json.loads(CATALOG_PATH.read_text())
    updated = {}
    for sku_entry in catalog:
        sku = sku_entry.get('sku')
        LOG.info('Extracting price for %s', sku)
        price = _get_pricing_for_sku_public(offerings, sku, location=location)
        if price is None:
            LOG.info('Price not found for %s; leaving as-is', sku)
        else:
            LOG.info('Found price for %s: %s USD/hour', sku, price)
            sku_entry['price_per_hour'] = round(price, 6)
        updated[sku] = price

    # write cache
    CACHE_PATH.write_text(json.dumps({k: (v if v is None else round(v, 6)) for k, v in updated.items()}, indent=2))
    LOG.info('Wrote cache to %s', CACHE_PATH)

    if write_back:
        CATALOG_PATH.write_text(json.dumps(catalog, indent=2))
        LOG.info('Wrote updated catalog to %s', CATALOG_PATH)

    return updated


def sync_prices(write_back: bool = False, location: str = 'US East (N. Virginia)') -> dict:
    """Load catalog, query AWS Pricing for each SKU, write cache and optionally update catalog.

    Returns a mapping { sku: price_per_hour_or_None }.
    """
    if boto3 is None:
        raise RuntimeError('boto3 is required to sync prices; install it or monkeypatch sync_mod.boto3 in tests')
    client = boto3.client('pricing', region_name='us-east-1')
    catalog = json.loads(CATALOG_PATH.read_text())
    updated = {}
    for sku_entry in catalog:
        sku = sku_entry.get('sku')
        LOG.info('Fetching price for %s', sku)
        price = _get_pricing_for_sku(client, sku, location=location)
        if price is None:
            LOG.info('Price not found for %s; leaving as-is', sku)
        else:
            LOG.info('Found price for %s: %s USD/hour', sku, price)
            sku_entry['price_per_hour'] = round(price, 6)
        updated[sku] = price

    # write cache
    CACHE_PATH.write_text(json.dumps({k: (v if v is None else round(v, 6)) for k, v in updated.items()}, indent=2))
    LOG.info('Wrote cache to %s', CACHE_PATH)

    if write_back:
        CATALOG_PATH.write_text(json.dumps(catalog, indent=2))
        LOG.info('Wrote updated catalog to %s', CATALOG_PATH)

    return updated


def main():
    parser = argparse.ArgumentParser(description='Sync AWS prices into local catalog cache')
    parser.add_argument('--public', action='store_true', help='Use public EC2 offerings (no AWS credentials required)')
    parser.add_argument('--write-catalog', action='store_true', help='Overwrite catalog with fetched prices')
    parser.add_argument('--location', default='US East (N. Virginia)', help='AWS region name (location filter)')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    
    if args.public:
        LOG.info('Starting AWS price sync via public offerings (location=%s)', args.location)
        updated = sync_prices_public(write_back=args.write_catalog, location=args.location)
    else:
        LOG.info('Starting AWS price sync via boto3 Pricing API (location=%s)', args.location)
        updated = sync_prices(write_back=args.write_catalog, location=args.location)
    
    LOG.info('Sync complete; %d SKUs processed', len(updated))


if __name__ == '__main__':
    main()
