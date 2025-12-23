# Infrastructure Cost Calculator - Technical Documentation

## 📚 Current Technology Stack

### Backend Stack
- **Language**: Python 3.x
- **Framework**: Flask (lightweight web framework)
- **Port**: 5000
- **Key Libraries**:
  - `flask-cors`: Cross-Origin Resource Sharing support
  - `pydantic`: Data validation and settings management
  - `pandas`: Data manipulation (for future analytics)
  - `requests`: HTTP library (for API calls)
  - `reportlab`: PDF generation (for reports)

### Frontend Stack
- **Framework**: Next.js 14.2.35 (React 18.2.0)
- **Language**: TypeScript 5.2.2
- **Styling**: TailwindCSS 3.3.2 + Custom CSS
- **Port**: 3000
- **Testing**: Playwright (E2E testing)

### Architecture
```
┌─────────────┐         HTTP/REST API        ┌──────────────┐
│             │    ← localhost:5000/calculate│              │
│  Frontend   │◄──────────────────────────────┤   Backend    │
│  (Next.js)  │                               │   (Flask)    │
│  Port 3000  │────────────────────────────►  │  Port 5000   │
└─────────────┘         JSON Response         └──────────────┘
      │                                               │
      │                                               │
      ▼                                               ▼
  React UI                                    Cloud Provider
  Components                                   Cost Calculators
```

---

## 🎯 AWS MVP Implementation (NEW!)

### What Changed?

#### ❌ OLD: Hardcoded Rates (Fake Numbers)
```python
# OLD aws.py
cpu_rate = 10.0      # $ per vCPU / month (FAKE!)
ram_rate = 4.0       # $ per GB / month (FAKE!)
total = cpu * cpu_rate + ram * ram_rate  # Simple multiplication
```

#### ✅ NEW: Instance Catalog + Nearest Match (Real Pricing!)
```python
# NEW aws.py
matcher = get_matcher()  # Load real instance catalog
result = matcher.calculate_costs(cpu, ram, storage, network, backup)
# Returns: selected instance + real pricing
```

### Architecture Overview

```
User Input (4 vCPU, 16GB RAM)
        │
        ▼
  AWS Matcher Algorithm
        │
        ├──► Load Instance Catalog (aws_instance_catalog.json)
        │
        ├──► Filter instances that meet requirements
        │      - Must have >= 4 vCPU
        │      - Must have >= 16 GB RAM
        │
        ├──► Analyze workload type
        │      - RAM/CPU ratio = 16/4 = 4
        │      - Balanced workload → General purpose instances
        │
        ├──► Select cheapest matching instance
        │      - t3.xlarge: $121.47/month ✓ (cheapest)
        │      - m5.xlarge: $140.16/month
        │
        └──► Calculate total costs
               ├─ Compute: $121.47 (instance)
               ├─ Storage: $8.00 (100 GB EBS gp3)
               ├─ Network: $291.60 (10 Mbps transfer)
               └─ Backup: $1.15 (50 GB S3)
                  TOTAL: $422.22/month
```

### Key Components

#### 1. Instance Catalog (`aws_instance_catalog.json`)
- **14 Real EC2 Instance Types**:
  - t3 series: Burstable performance (cost-effective)
  - m5 series: General purpose, balanced
  - c5 series: Compute-optimized (CPU-heavy workloads)
  - r5 series: Memory-optimized (RAM-heavy workloads)

- **Real AWS Pricing** (US East 1, as of Dec 2024):
  ```json
  {
    "instance_type": "t3.xlarge",
    "vcpu": 4,
    "memory_gb": 16,
    "price_per_hour": 0.1664,
    "price_per_month": 121.47
  }
  ```

- **Storage, Network, Backup Pricing**:
  - EBS gp3: $0.08/GB/month
  - Data transfer out: $0.09/GB
  - S3 Standard backup: $0.023/GB/month

#### 2. Instance Matcher (`aws_matcher.py`)
**Smart Selection Algorithm**:

```python
def find_best_instance(cpu, ram):
    # Step 1: Calculate workload characteristics
    ram_to_cpu_ratio = ram / cpu
    
    # Step 2: Determine workload type
    if ram_to_cpu_ratio > 6:
        # Memory-heavy → Prefer r5 instances
        select from memory-optimized instances
    elif ram_to_cpu_ratio < 3:
        # CPU-heavy → Prefer c5 instances
        select from compute-optimized instances
    else:
        # Balanced → Use t3/m5 instances
        select from general purpose instances
    
    # Step 3: Filter instances meeting requirements
    matching = instances where vcpu >= cpu AND memory >= ram
    
    # Step 4: Sort by price and return cheapest
    return cheapest matching instance
```

**Example Selections**:
| Input | Selected Instance | Reasoning |
|-------|------------------|-----------|
| 2 vCPU, 8 GB | `t3.large` | Balanced, burstable, cheapest |
| 4 vCPU, 16 GB | `t3.xlarge` | Balanced general purpose |
| 4 vCPU, 32 GB | `r5.xlarge` | High RAM ratio → memory-optimized |
| 8 vCPU, 16 GB | `c5.2xlarge` | Low RAM ratio → compute-optimized |

#### 3. Updated AWS Cost Function
```python
def aws_cost(cpu, ram, storage, network, backup):
    matcher = get_matcher()
    return matcher.calculate_costs(cpu, ram, storage, network, backup)
```

**Returns**:
```json
{
  "provider": "aws",
  "total": 422.22,
  "currency": "USD",
  "selected_instance": {
    "type": "t3.xlarge",
    "vcpu": 4,
    "memory_gb": 16,
    "category": "general",
    "description": "Burstable performance",
    "price_per_month": 121.47
  },
  "breakdown": {
    "compute": 121.47,
    "storage": 8.0,
    "network": 291.6,
    "backup": 1.15
  }
}
```

### UI Changes

#### Provider Card Now Shows Instance Details
**Before**:
```
AWS
per month • estimated
$422.22
```

**After**:
```
AWS
t3.xlarge • 4 vCPU • 16 GB RAM
$422.22
```

---

## 🔄 How to Update Pricing

### Option 1: Manual Update (Easiest)
1. Visit [AWS EC2 Pricing](https://aws.amazon.com/ec2/pricing/on-demand/)
2. Update `aws_instance_catalog.json` with new prices
3. Restart backend

### Option 2: Automated Scraping (Future)
```python
# Future implementation
import boto3
client = boto3.client('pricing', region_name='us-east-1')
response = client.get_products(
    ServiceCode='AmazonEC2',
    Filters=[...]
)
```

### Option 3: AWS Price List API
- Use AWS Price List API (official)
- Update catalog periodically (daily/weekly)
- Cache results locally

---

## 🚀 Next Steps for Azure & GCP

### Azure MVP
- Create `azure_instance_catalog.json`
- Implement `azure_matcher.py`
- Map to VM sizes: Standard_D2s_v3, Standard_D4s_v3, etc.

### GCP MVP
- Create `gcp_instance_catalog.json`
- Implement `gcp_matcher.py`
- Map to machine types: n1-standard-2, n2-standard-4, etc.

### Kubernetes & On-Prem
- Keep current simplified calculations
- Or calculate based on underlying cloud provider

---

## 📊 Testing the Implementation

### Test Backend
```bash
cd backend
python3 -c "
from cloud_providers.aws import aws_cost
result = aws_cost(cpu=4, ram=16, storage=100, network=10, backup=50)
import json
print(json.dumps(result, indent=2))
"
```

### Test Full Stack
1. Start backend: `./run_services.sh`
2. Open http://localhost:3000
3. Enter: 4 vCPU, 16 GB RAM
4. Click "Show prices"
5. See: "t3.xlarge • 4 vCPU • 16 GB RAM" on AWS card

---

## 🎯 Benefits of This Approach

### ✅ Realistic Pricing
- Uses actual AWS instance types and prices
- Shows users what they would actually buy

### ✅ Smart Selection
- Automatically picks most cost-effective instance
- Considers workload characteristics (CPU vs RAM heavy)

### ✅ Easy Maintenance
- Simple JSON file for updates
- No complex API integration needed
- Can be automated later

### ✅ User-Friendly
- Shows exact instance type in UI
- Users can verify on AWS pricing page
- Transparent pricing breakdown

### ✅ Scalable
- Easy to add more instance types
- Can extend to reserved instances, spot instances
- Foundation for Azure, GCP, etc.

---

## 🔧 Maintenance Guide

### Adding New Instance Types
Edit `aws_instance_catalog.json`:
```json
{
  "instance_type": "m5.8xlarge",
  "vcpu": 32,
  "memory_gb": 128,
  "price_per_hour": 1.536,
  "price_per_month": 1121.28,
  "category": "general",
  "description": "General purpose, balanced compute"
}
```

### Updating Prices
1. Check AWS pricing page
2. Update `price_per_hour` and `price_per_month`
3. No code changes needed!

### Adding New Categories
- Storage: Add to `storage_pricing`
- Network: Update `network_pricing`
- Other services: Extend catalog structure

---

## 📈 Future Enhancements

1. **Reserved Instance Pricing**: 1-year, 3-year commitments
2. **Spot Instance Pricing**: Up to 90% discount
3. **Regional Pricing**: Different prices per AWS region
4. **Commitment Discounts**: Volume discounts
5. **Real-time Price Fetching**: AWS Price List API integration
6. **Historical Pricing**: Track price changes over time
7. **Cost Optimization Tips**: Suggest reserved instances, right-sizing

---

## 💡 Summary

**Current State**: AWS now uses **real instance catalog** with **smart matching algorithm**

**What You Get**:
- ✅ Real AWS instance types (t3, m5, c5, r5 series)
- ✅ Actual AWS pricing (Dec 2024, US East 1)
- ✅ Smart instance selection based on workload
- ✅ Instance details shown in UI
- ✅ Easy to maintain and update

**Next**: Apply same approach to Azure and GCP! 🚀
