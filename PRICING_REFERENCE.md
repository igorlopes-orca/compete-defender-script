# Defender for Cloud - Pricing Reference

Source: https://azure.microsoft.com/en-us/pricing/details/defender-for-cloud/

Last updated: 2026-02-14

## How to update prices

1. Visit the [pricing page](https://azure.microsoft.com/en-us/pricing/details/defender-for-cloud/)
2. Compare each row below with the page
3. Update `src/defender_savings/config.py` → `PRICING` dict
4. Update the "Current Price" column below

## SKU field mapping

The Orca API returns `ServicesPricing` as a dict of `{key: tier}` where tier is `"Free"` or `"Standard"`.
Below is how each API key maps to a Defender SKU and how we decide what to calculate.

| API `ServicesPricing` Key | Defender SKU | How we decide | Pricing logic |
|---|---|---|---|
| `VirtualMachines` | Defender for Servers | `Standard` = enabled. **We assume Plan 2** (API doesn't distinguish P1 vs P2) | count of `AzureComputeVm` × $14.60 |
| `Containers` | Defender for Containers | `Standard` = enabled | sum of `VCpuCount` across Azure VMs with containers × $6.8693 (default 4 vCPU if missing) |
| `AppServices` | Defender for App Service | `Standard` = enabled | count of `AzureWebAppService` × $14.60 |
| `Arm` | Defender for Resource Manager | `Standard` = enabled | count of subscriptions (1 per Defender config) × $5.04 |
| `KeyVaults` | Defender for Key Vault | `Standard` = enabled | count of `AzureKeyVault` × $0.25 |
| `CloudPosture` | Defender CSPM (paid) | `Standard` = advanced CSPM (paid). `Free` = foundational CSPM (free) | billable resources (VMs + Storage Accounts) × $5.00 |
| `FoundationalCspm` | Foundational CSPM | Always free tier, no cost. Not used for pricing decisions | not calculated |
| `CosmosDbs` | Defender for Azure Cosmos DB | `Standard` = enabled | **not counted** (no RU data from API) |
| `SqlServers` | Defender for SQL (Azure-connected) | `Standard` = enabled | **not counted** (no SQL instance query yet) |
| `SqlServerVirtualMachines` | Defender for SQL on machines | `Standard` = enabled | **not counted** (no SQL VM query yet) |
| `OpenSourceRelationalDatabases` | Defender for OSS Databases | `Standard` = enabled | **not counted** (no OSS DB query yet) |
| `StorageAccounts` | Defender for Storage | `Standard` = enabled | count of `AzureStorageAccount` × $10.00 |
| `AI` | Defender for AI Services | `Standard` = enabled | not calculated (token-based) |
| `Api` | Defender for APIs | `Standard` = enabled | not calculated (plan-based) |
| `Discovery` | Asset discovery | `Standard` = enabled | not calculated (no direct cost) |
| `Dns` | Defender for DNS | retired | not calculated |
| `ContainerRegistry` | Legacy Container Registry | superseded by Containers plan | not calculated |
| `KubernetesService` | Legacy Kubernetes | superseded by Containers plan | not calculated |

## Price mapping (calculated services)

| API Key | Service | Current Price | Unit | Config count_key |
|---|---|---|---|---|
| `VirtualMachines` | Defender for Servers Plan 2 | $14.60 | server/mo | `virtual_machines` |
| `Containers` | Defender for Containers | $6.8693 | vCore/mo | `container_vcores` |
| `AppServices` | Defender for App Service | $14.60 | instance/mo | `app_services` |
| `Arm` | Defender for Resource Manager | $5.04 | subscription/mo | `subscriptions` |
| `KeyVaults` | Defender for Key Vault | $0.25 | vault/mo | `key_vaults` |
| `StorageAccounts` | Defender for Storage | $10.00 | storage account/mo | `storage_accounts` |
| `CloudPosture` | Defender CSPM | $5.00 | billable resource/mo | `_cspm_billable` |

## CSPM billable resources

`_cspm_billable` is computed as: **VMs + Storage Accounts**

Full billable list per Microsoft: VMs, Storage Accounts, OSS DBs, SQL PaaS & Servers on Machines, Serverless functions, and Web apps. We currently only count VMs and Storage Accounts (the resources we already fetch).

## Notes

- Prices are USD pay-as-you-go (no commit discounts applied)
- Pre-purchase plans offer 10-22% discounts (not reflected here)
- Defender for Servers: API reports `"Standard"` without distinguishing Plan 1 vs Plan 2. We assume Plan 2
- Container vCPU count: read from `VCpuCount` field; defaults to 4 vCPUs when missing
- CSPM price ($5.00/billable resource/mo) needs confirmation — not shown on pricing page
