import logging

from defender_savings.models.defender import DefenderConfig
from defender_savings.models.resources import AppService, ContainerHost, KeyVault, StorageAccount, VirtualMachine

logger = logging.getLogger(__name__)


class ResourceDefenderMap:
    """Maps Azure resources to their cloud account's Defender configuration."""

    def __init__(self, defender_configs: list[DefenderConfig]) -> None:
        self._configs: dict[str, DefenderConfig] = {
            cfg.cloud_account_name: cfg for cfg in defender_configs
        }

    def get_config(self, cloud_account_name: str) -> DefenderConfig | None:
        return self._configs.get(cloud_account_name)

    def count_resources_per_account(
        self,
        vms: list[VirtualMachine],
        app_services: list[AppService],
        storage_accounts: list[StorageAccount],
        key_vaults: list[KeyVault],
        container_hosts: list[ContainerHost],
    ) -> dict[str, dict[str, int]]:
        """Count resources grouped by cloud account name."""
        counts: dict[str, dict[str, int]] = {}
        for account_name in self._configs:
            counts[account_name] = {
                "virtual_machines": 0,
                "app_services": 0,
                "storage_accounts": 0,
                "key_vaults": 0,
                "container_vcores": 0,
                "subscriptions": 1,
            }

        for vm in vms:
            if vm.cloud_account_name in counts:
                counts[vm.cloud_account_name]["virtual_machines"] += 1

        for app in app_services:
            if app.cloud_account_name in counts:
                counts[app.cloud_account_name]["app_services"] += 1

        for sa in storage_accounts:
            if sa.cloud_account_name in counts:
                counts[sa.cloud_account_name]["storage_accounts"] += 1

        for kv in key_vaults:
            if kv.cloud_account_name in counts:
                counts[kv.cloud_account_name]["key_vaults"] += 1

        for host in container_hosts:
            if host.cloud_account_name in counts:
                counts[host.cloud_account_name]["container_vcores"] += host.vcpu_count

        logger.info("Mapped resources across %d cloud accounts", len(counts))
        return counts
