from __future__ import annotations

import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AzureAsset(BaseModel):
    """Base model for any Azure asset from Orca API.

    Response structure:
        {
            "id": "...", "name": "...", "type": "...",
            "data": {
                "Name": {"value": "my-vm"},
                "CloudAccount": {"name": "EA-Shape-Prod", ...},
                "AssetUniqueId": {"value": "..."},
                ...
            }
        }
    """

    name: str
    cloud_account_name: str
    asset_unique_id: str

    @classmethod
    def _extract_common(cls, item: dict) -> dict:
        data = item.get("data", {})

        # CloudAccount is a nested object (not value-wrapped)
        cloud_account = data.get("CloudAccount", {})
        account_name = cloud_account.get("name", "") if isinstance(cloud_account, dict) else ""

        # Name and AssetUniqueId are value-wrapped
        name = data.get("Name", {}).get("value", item.get("name", ""))
        asset_id = data.get("AssetUniqueId", {}).get("value", item.get("id", ""))

        return {
            "name": name,
            "cloud_account_name": account_name,
            "asset_unique_id": asset_id,
        }


class VirtualMachine(AzureAsset):
    @classmethod
    def from_orca_response(cls, item: dict) -> VirtualMachine:
        return cls(**cls._extract_common(item))


class AppService(AzureAsset):
    @classmethod
    def from_orca_response(cls, item: dict) -> AppService:
        return cls(**cls._extract_common(item))


class StorageAccount(AzureAsset):
    @classmethod
    def from_orca_response(cls, item: dict) -> StorageAccount:
        return cls(**cls._extract_common(item))


class KeyVault(AzureAsset):
    @classmethod
    def from_orca_response(cls, item: dict) -> KeyVault:
        return cls(**cls._extract_common(item))


_DEFAULT_VCPUS = 4


class ContainerHost(AzureAsset):
    """A VM that has containers running on it.

    vcpu_count comes from VCpuCount in the API response.
    Falls back to 4 vCPUs when the field is missing.
    """

    vcpu_count: int = _DEFAULT_VCPUS

    @classmethod
    def from_orca_response(cls, item: dict) -> ContainerHost:
        common = cls._extract_common(item)
        data = item.get("data", {})
        vcpu = data.get("VCpuCount", {}).get("value", _DEFAULT_VCPUS)
        if not isinstance(vcpu, int) or vcpu <= 0:
            vcpu = _DEFAULT_VCPUS
        common["vcpu_count"] = vcpu
        return cls(**common)
