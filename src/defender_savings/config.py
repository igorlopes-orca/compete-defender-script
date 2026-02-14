import logging
import os


ORCA_API_URL = "https://api.orcasecurity.io"
ORCA_QUERY_ENDPOINT = "/api/serving-layer/query"

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# ---------------------------------------------------------------------------
# Defender for Cloud pricing (USD, pay-as-you-go)
#
# Source: https://azure.microsoft.com/en-us/pricing/details/defender-for-cloud/
# Last updated: 2026-02-14
#
# To update prices, visit the URL above, compare each entry below with the
# page, and update unit_price / unit as needed. The "api_key" field maps
# each entry to the ServicesPricing key returned by the Orca API. The
# "count_key" maps to the resource count produced by the mapper.
# ---------------------------------------------------------------------------

PRICING: dict[str, dict] = {
    "VirtualMachines": {
        "description": "Defender for Servers Plan 2",
        "unit_price": 14.60,
        "unit": "server/mo",
        "count_key": "virtual_machines",
    },
    "Containers": {
        "description": "Defender for Containers",
        "unit_price": 6.8693,
        "unit": "vCore/mo",
        "count_key": "container_vcores",
    },
    "AppServices": {
        "description": "Defender for App Service",
        "unit_price": 14.60,
        "unit": "instance/mo",
        "count_key": "app_services",
    },
    "Arm": {
        "description": "Defender for Resource Manager",
        "unit_price": 5.04,
        "unit": "subscription/mo",
        "count_key": "subscriptions",
    },
    "KeyVaults": {
        "description": "Defender for Key Vault",
        "unit_price": 0.25,
        "unit": "vault/mo",
        "count_key": "key_vaults",
    },
    "CosmosDbs": {
        "description": "Defender for Azure Cosmos DB",
        "unit_price": 0.876,
        "unit": "100 RUs/mo",
        "count_key": "cosmos_db_ru_hundreds",
    },
    "SqlServers": {
        "description": "Defender for SQL (Azure-connected)",
        "unit_price": 15.00,
        "unit": "instance/mo",
        "count_key": "sql_servers",
    },
    "SqlServerVirtualMachines": {
        "description": "Defender for SQL on machines",
        "unit_price": 15.00,
        "unit": "instance/mo",
        "count_key": "sql_server_vms",
    },
    "OpenSourceRelationalDatabases": {
        "description": "Defender for OSS Databases",
        "unit_price": 15.00,
        "unit": "instance/mo",
        "count_key": "oss_databases",
    },
    "StorageAccounts": {
        "description": "Defender for Storage",
        "unit_price": 10.00,
        "unit": "storage account/mo",
        "count_key": "storage_accounts",
    },
    "CloudPosture": {
        "description": "Defender CSPM",
        "unit_price": 5.00,
        "unit": "billable resource/mo",
        "count_key": "_cspm_billable",
    },
}
