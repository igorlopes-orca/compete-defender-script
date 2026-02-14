"""Shared factories for test data."""

from __future__ import annotations

from defender_savings.models.defender import DefenderConfig
from defender_savings.models.resources import (
    AppService,
    ContainerHost,
    KeyVault,
    StorageAccount,
    VirtualMachine,
)


# ── Pydantic model factories ──────────────────────────────────────────


def make_defender_config(
    name: str = "DefenderForCloud",
    cloud_account_name: str = "acct-1",
    subscription_id: str = "sub-111",
    services_pricing: dict[str, str] | None = None,
) -> DefenderConfig:
    return DefenderConfig(
        name=name,
        cloud_account_name=cloud_account_name,
        subscription_id=subscription_id,
        services_pricing=services_pricing or {},
    )


def make_vm(
    cloud_account_name: str = "acct-1",
    name: str = "vm-1",
) -> VirtualMachine:
    return VirtualMachine(
        name=name,
        cloud_account_name=cloud_account_name,
        asset_unique_id=f"{cloud_account_name}/{name}",
    )


def make_app(
    cloud_account_name: str = "acct-1",
    name: str = "app-1",
) -> AppService:
    return AppService(
        name=name,
        cloud_account_name=cloud_account_name,
        asset_unique_id=f"{cloud_account_name}/{name}",
    )


def make_storage(
    cloud_account_name: str = "acct-1",
    name: str = "sa-1",
) -> StorageAccount:
    return StorageAccount(
        name=name,
        cloud_account_name=cloud_account_name,
        asset_unique_id=f"{cloud_account_name}/{name}",
    )


def make_kv(
    cloud_account_name: str = "acct-1",
    name: str = "kv-1",
) -> KeyVault:
    return KeyVault(
        name=name,
        cloud_account_name=cloud_account_name,
        asset_unique_id=f"{cloud_account_name}/{name}",
    )


def make_container_host(
    cloud_account_name: str = "acct-1",
    name: str = "host-1",
    vcpu_count: int = 4,
) -> ContainerHost:
    return ContainerHost(
        name=name,
        cloud_account_name=cloud_account_name,
        asset_unique_id=f"{cloud_account_name}/{name}",
        vcpu_count=vcpu_count,
    )


# ── Raw API dict factories ────────────────────────────────────────────


def make_orca_asset_item(
    name: str = "my-resource",
    cloud_account_name: str = "acct-1",
    asset_unique_id: str = "uid-123",
    extra_data: dict | None = None,
) -> dict:
    data: dict = {
        "Name": {"value": name},
        "CloudAccount": {"name": cloud_account_name},
        "AssetUniqueId": {"value": asset_unique_id},
    }
    if extra_data:
        data.update(extra_data)
    return {"name": name, "id": asset_unique_id, "data": data}


def make_orca_defender_item(
    name: str = "DefenderForCloud",
    cloud_account_name: str = "acct-1",
    subscription_id: str = "sub-111",
    services_pricing: dict[str, str] | None = None,
) -> dict:
    return {
        "name": name,
        "id": f"defender-{cloud_account_name}",
        "data": {
            "Name": {"value": name},
            "CloudAccount": {"name": cloud_account_name},
            "SecurityCenterSubscription": {"value": subscription_id},
            "ServicesPricing": {"value": services_pricing or {}},
        },
    }
