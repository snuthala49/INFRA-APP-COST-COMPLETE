# Price Sync Scheduler Documentation

## Overview

The infrastructure cost app includes a periodic price sync scheduler that automatically updates AWS instance pricing from public EC2 offerings. This ensures that cost calculations stay current without requiring manual intervention.

## How It Works

The scheduler runs automatically when the Flask app starts and executes AWS price syncs at a configurable time (default: daily at 2 AM UTC).

### Architecture

- **Scheduler Engine**: APScheduler (BackgroundScheduler)
- **Sync Job**: `sync_aws_prices()` calls `sync_prices_public()` from AWS price sync module
- **Frequency**: Daily cron job (configurable)
- **Error Handling**: Exceptions are logged but don't crash the app

### Files

- `backend/utils/price_sync_scheduler.py`: Scheduler logic and management functions
- `backend/utils/aws_price_sync.py`: AWS pricing fetch and catalog update logic
- `backend/data/aws_catalog.json`: Local instance catalog (updated by price sync)
- `backend/data/cache.json`: Price cache from AWS offerings (intermediate data)

## Setup & Usage

### 1. Install Dependencies

APScheduler is already in `requirements.txt`:

```bash
pip install -r backend/requirements.txt
```

### 2. Start the App

The scheduler starts automatically on app startup:

```bash
cd backend
python app.py
```

Logs will show:
```
Scheduler started. AWS price sync scheduled daily at 02:00 UTC.
```

### 3. Configure Sync Timing

Edit `backend/app.py` to change the sync schedule:

```python
# Default: daily at 2 AM UTC
start_scheduler(cron_hour=2, cron_minute=0)

# Example: daily at 3 PM UTC
start_scheduler(cron_hour=15, cron_minute=0)

# Example: every Sunday at 6 AM UTC
# (Note: requires extended CronTrigger configuration)
```

### 4. Manual Sync (Optional)

Run price sync manually anytime:

```bash
python backend/utils/aws_price_sync.py --public --write-back
```

Options:
- `--public`: Use public EC2 offerings (no credentials required)
- `--boto3`: Use AWS Pricing API (requires AWS credentials)
- `--write-back`: Update the local catalog JSON with fetched prices

## Key Features

✅ **No Credentials Required**: Default mode uses public EC2 offerings  
✅ **Automatic**: Runs on schedule without manual intervention  
✅ **Error Resilient**: Failures are logged; app continues running  
✅ **Graceful Shutdown**: Scheduler stops cleanly on app termination  
✅ **Flexible**: Easy to adjust timing or switch between public/boto3 modes

## Verification

Check the scheduler is running:

1. Monitor logs for scheduler startup and sync job execution
2. Verify `backend/data/cache.json` is created/updated after each sync
3. Optional: Check `backend/data/aws_catalog.json` for updated prices (with `--write-back`)

## Troubleshooting

### Scheduler doesn't start
- Check `requirements.txt` includes `apscheduler`
- Review Flask app logs for import errors

### Price sync fails
- Verify internet connectivity for public EC2 offerings
- Check logs for specific error messages
- Scheduler continues running even if a sync job fails

### Disable Scheduler
Comment out `start_scheduler()` call in `backend/app.py` if not needed.

## Future Enhancements

- Add Azure and GCP price sync modules (Azure/GCP catalogs exist, pricing updates TBD)
- Support systemd timer or cron wrapper for production deployments
- Add webhook notifications on price changes
- Implement caching strategy to avoid redundant syncs
