import logging

from defender_savings.api.client import OrcaClient
from defender_savings.models.resources import AppService, ContainerHost, KeyVault, StorageAccount, VirtualMachine

logger = logging.getLogger(__name__)

_ASSET_SELECT = [
    "Name",
    "CloudAccount.Name",
    "CloudAccount.CloudProvider",
    "BusinessUnits.Name",
    "OrcaScore",
    "RiskLevel",
    "group_unique_id",
    "UiUniqueField",
    "IsInternetFacing",
    "Tags",
    "NewSubCategory",
    "AssetUniqueId",
    "ConsoleUrlLink",
]

_CONTAINER_HOST_SELECT = [
    "Name",
    "CloudAccount.Name",
    "CloudAccount.CloudProvider",
    "BusinessUnits.Name",
    "OrcaScore",
    "RiskLevel",
    "State",
    "StopDate",
    "group_unique_id",
    "UiUniqueField",
    "IsInternetFacing",
    "VCpuCount",
    "CpuCount",
    "Containers.Name",
    "Tags",
    "NewSubCategory",
    "AssetUniqueId",
    "ConsoleUrlLink",
    "DistributionName",
    "IngressPorts",
    "PrivateIps",
    "PublicIps",
]

_CONTAINER_HOST_FILTER = {
    "operator": "and",
    "type": "operation",
    "values": [
        {
            "keys": ["Containers"],
            "models": ["Container"],
            "type": "object_set",
            "operator": "has",
        },
        {
            "key": "VCpuCount",
            "values": [],
            "type": "int",
            "operator": "exists",
        },
    ],
}


def list_virtual_machines(client: OrcaClient) -> list[VirtualMachine]:
    """Fetch Azure VMs from Orca."""
    logger.info("Fetching Azure VMs")
    items = client.query(models=["AzureComputeVm"], select=_ASSET_SELECT)
    return [VirtualMachine.from_orca_response(item) for item in items]


def list_app_services(client: OrcaClient) -> list[AppService]:
    """Fetch Azure App Services from Orca."""
    logger.info("Fetching Azure App Services")
    items = client.query(models=["AzureWebAppService"], select=_ASSET_SELECT)
    return [AppService.from_orca_response(item) for item in items]


def list_storage_accounts(client: OrcaClient) -> list[StorageAccount]:
    """Fetch Azure Storage Accounts from Orca."""
    logger.info("Fetching Azure Storage Accounts")
    items = client.query(models=["AzureStorageAccount"], select=_ASSET_SELECT)
    return [StorageAccount.from_orca_response(item) for item in items]


def list_key_vaults(client: OrcaClient) -> list[KeyVault]:
    """Fetch Azure Key Vaults from Orca."""
    logger.info("Fetching Azure Key Vaults")
    items = client.query(models=["AzureKeyVault"], select=_ASSET_SELECT)
    return [KeyVault.from_orca_response(item) for item in items]


def list_container_hosts(client: OrcaClient) -> list[ContainerHost]:
    """Fetch Azure VMs with containers and VCpuCount available."""
    logger.info("Fetching container hosts (Azure VMs with containers)")
    items = client.query(
        models=["AzureComputeVm"],
        select=_CONTAINER_HOST_SELECT,
        with_filter=_CONTAINER_HOST_FILTER,
    )
    return [ContainerHost.from_orca_response(item) for item in items]
