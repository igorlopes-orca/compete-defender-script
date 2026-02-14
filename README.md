# Defender Savings

Microsoft Defender for Cloud cost estimator and savings calculator.

Uses the Orca Security API to fetch Defender configurations and Azure resources, maps each resource to its cloud account's Defender plan, and calculates current costs with potential savings opportunities.

## Setup

```bash
uv sync
```

## Usage

```bash
# Set your Orca API token in .env
echo 'TOKEN=your-orca-api-token' > .env

# Run
uv run defender-savings

# With debug logging
LOG_LEVEL=DEBUG uv run defender-savings
```

## Project Structure

```
src/defender_savings/
├── cli.py              # Entry point — orchestrates the pipeline
├── config.py           # Settings, constants, pricing tables
├── models/
│   ├── defender.py     # Defender config models (Pydantic)
│   └── resources.py    # Azure resource models (VM, App Service, Storage, Container)
├── api/
│   ├── client.py       # Orca API client with pagination
│   ├── defender.py     # Query AzureDefenderForCloud configs
│   └── resources.py    # Query VMs, App Services, Storage Accounts, Containers
├── services/
│   ├── mapper.py       # Map resources to Defender configs by cloud account
│   └── calculator.py   # Cost calculation and savings analysis
└── output/
    └── table.py        # Table-formatted terminal output
```

## How It Works

1. Fetches all AzureDefenderForCloud configs from the Orca API
2. Fetches resources (VMs, App Services, Storage Accounts, Container Nodes)
3. Maps each resource to its cloud account's Defender config
4. Calculates per-account costs based on retail pricing
5. Identifies savings opportunities (plan downgrades)
6. Outputs a consolidated cost table and savings table

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `TOKEN` | Yes | Orca Security API token (can be set in `.env`) |
| `LOG_LEVEL` | No | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` (default: `INFO`) |
