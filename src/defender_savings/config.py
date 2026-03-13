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
#
# ---------------------------------------------------------------------------
# BILLING ASSUMPTIONS & KNOWN LIMITATIONS
# ---------------------------------------------------------------------------
#
# WHAT WE ASSUME / INTENTIONAL BEHAVIOUR
#
#   Servers plan:
#     - The API returns "Standard" for both P1 ($5.02) and P2 ($14.60) without
#       distinguishing them. We always assume Plan 2 ($14.60). If the customer
#       is on Plan 1 the estimate will be ~3× too high for this service.
#
#   Containers:
#     - Priced at $6.8693/vCore/mo (Azure list price).
#     - vCPU count comes from VCpuCount in the Orca response.
#     - A VM that hosts containers is counted for BOTH Defender for Servers
#       AND Defender for Containers. This matches Azure's actual billing.
#
#   Savings:
#     - Calculated as the full monthly cost of disabling each Standard service
#       entirely. Only services with at least 1 resource appear.
#
# KNOWN UNDERCOUNTING (intentional — we prefer to underestimate)
#
#   CSPM billable:
#     - We count VMs + Storage Accounts only.
#     - Azure also bills App Services, SQL, OSS DBs, and serverless functions
#       as CSPM billable resources. Those are excluded here.
#
#   Container hosts without VCpuCount:
#     - The API query filters to VMs where VCpuCount *exists*. Container hosts
#       missing that field are not counted. The default-4 fallback in the model
#       only fires for invalid values, not for records filtered at query time.
#
#   Services with no API query (always show $0):
#     - CosmosDbs, SqlServers, SqlServerVirtualMachines,
#       OpenSourceRelationalDatabases are in the pricing table for reference
#       but have no Orca query backing them. They are silently skipped (count=0).
#
# POTENTIAL OVERCOUNT RISKS (mitigated in code)
#
#   Duplicate subscription records:
#     - Orca should never return multiple AzureDefenderForCloud records for the
#       same subscription (Defender is a per-subscription setting in Azure).
#       If it does, cli.py logs a WARNING and keeps the first record to prevent
#       double-counting.
#
#   Resource account mismatch:
#     - Resources whose cloud_account_name doesn't match any DefenderConfig are
#       silently dropped. No inflation risk; may cause undercounting instead.
#
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
