import logging
import os
import sys

from defender_savings.api.client import OrcaClient
from defender_savings.api.defender import list_defender_configs
from defender_savings.api.resources import (
    list_app_services,
    list_container_hosts,
    list_key_vaults,
    list_storage_accounts,
    list_virtual_machines,
)
from defender_savings.output.table import print_cost_table, print_module_breakdown_table, print_savings_table, print_subscription_breakdown_table
from defender_savings.services.calculator import AccountSummary, aggregate_by_module, calculate_account_costs
from defender_savings.services.mapper import ResourceDefenderMap

logger = logging.getLogger(__name__)


def _load_token() -> str:
    """Load API token from environment, sourcing .env if needed."""
    token = os.environ.get("TOKEN")
    if not token:
        env_path = os.path.join(os.getcwd(), ".env")
        if os.path.exists(env_path):
            logger.info("Loading token from .env")
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TOKEN=") and not line.startswith("#"):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        logger.error("TOKEN environment variable is required (or set it in .env)")
        sys.exit(1)
    return token


def main() -> None:
    token = _load_token()
    client = OrcaClient(token)

    # 1. Fetch Defender configs
    logger.info("Fetching Defender configurations")
    defender_configs = list_defender_configs(client)

    # 2. Fetch resources
    logger.info("Fetching resources")
    vms = list_virtual_machines(client)
    apps = list_app_services(client)
    storage = list_storage_accounts(client)
    key_vaults = list_key_vaults(client)
    container_hosts = list_container_hosts(client)

    logger.info(
        "Total resources: %d VMs, %d App Services, %d Storage Accounts, %d Key Vaults, %d Container Hosts",
        len(vms), len(apps), len(storage), len(key_vaults), len(container_hosts),
    )

    # 3. Map resources to defender configs by cloud account
    mapper = ResourceDefenderMap(defender_configs)
    counts_by_account = mapper.count_resources_per_account(vms, apps, storage, key_vaults, container_hosts)

    # 4. Calculate costs per account
    # Azure Defender for Cloud is configured per subscription — one config per
    # subscription. Orca should never return duplicates, but if it does we warn
    # and keep the first record to avoid double-counting costs.
    seen: dict[str, DefenderConfig] = {}
    for config in defender_configs:
        if config.cloud_account_name in seen:
            logger.warning(
                "Duplicate DefenderConfig for account %r (subscription %s) — "
                "keeping first record, ignoring subsequent. "
                "This is unexpected; verify data quality in Orca.",
                config.cloud_account_name,
                config.subscription_id or "unknown",
            )
            continue
        seen[config.cloud_account_name] = config

    summaries: list[AccountSummary] = []
    for config in seen.values():
        resource_counts = counts_by_account.get(config.cloud_account_name, {})
        summary = calculate_account_costs(config, resource_counts)
        summaries.append(summary)

    # 5. Output tables
    print_cost_table(summaries)
    print_savings_table(summaries)
    print_subscription_breakdown_table(summaries)
    print_module_breakdown_table(aggregate_by_module(summaries))


if __name__ == "__main__":
    main()
