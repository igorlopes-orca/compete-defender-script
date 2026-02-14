# get azure defender for cloud list:
curl -X POST 'https://api.orcasecurity.io/api/serving-layer/query'         -H 'authority: api.orcasecurity.io'         -H 'accept: application/json, text/plain, */*'         -H 'accept-language: en-US,en;q=0.9'         -H 'authorization: TOKEN {{ORCA_API_TOKEN}}'         -H 'content-type: application/json'         --data-raw '{
  "query": {
    "models": [
      "AzureDefenderForCloud"
    ],
    "type": "object_set"
  },
  "limit": 100,
  "start_at_index": 0,
  "select": [
    "Name",
    "CloudAccount.Name",
    "CloudAccount.CloudProvider",
    "BusinessUnits.Name",
    "AutoProvisioning",
    "PolicyAssignments",
    "SecurityCenterSubscription",
    "SecurityContacts",
    "ServicesPricing",
    "Settings"
  ],
  "get_results_and_count": false,
  "full_graph_fetch": {
    "enabled": true
  },
  "debug_enable_bu_tags": true,
  "max_tier": 2
}'         --compressed

# get azure compute instances:
curl -X POST 'https://api.orcasecurity.io/api/serving-layer/query'         -H 'authority: api.orcasecurity.io'         -H 'accept: application/json, text/plain, */*'         -H 'accept-language: en-US,en;q=0.9'         -H 'authorization: TOKEN {{ORCA_API_TOKEN}}'         -H 'content-type: application/json'         --data-raw '{
  "query": {
    "models": [
      "AzureComputeVm"
    ],
    "type": "object_set"
  },
  "limit": 100,
  "start_at_index": 0,
  "order_by[]": [
    "-OrcaScore"
  ],
  "select": [
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
    "Tags",
    "NewSubCategory",
    "AssetUniqueId",
    "ConsoleUrlLink",
    "DistributionName",
    "IngressPorts",
    "PrivateIps",
    "PublicIps"
  ],
  "get_results_and_count": false,
  "full_graph_fetch": {
    "enabled": true
  },
  "debug_enable_bu_tags": true,
  "max_tier": 2
}'         --compressed

# get storage account:
curl -X POST 'https://api.orcasecurity.io/api/serving-layer/query'         -H 'authority: api.orcasecurity.io'         -H 'accept: application/json, text/plain, */*'         -H 'accept-language: en-US,en;q=0.9'         -H 'authorization: TOKEN {{ORCA_API_TOKEN}}'         -H 'content-type: application/json'         --data-raw '{
  "query": {
    "models": [
      "AzureStorageAccount"
    ],
    "type": "object_set"
  },
  "limit": 100,
  "start_at_index": 0,
  "order_by[]": [
    "-OrcaScore"
  ],
  "select": [
    "Name",
    "CloudAccount.Name",
    "CloudAccount.CloudProvider",
    "BusinessUnits.Name",
    "OrcaScore",
    "RiskLevel",
    "group_unique_id",
    "UiUniqueField",
    "IsInternetFacing",
    "SensitiveData.Name",
    "SensitiveData.SensitiveData",
    "Tags",
    "NewCategory",
    "NewSubCategory",
    "AssetUniqueId",
    "ConsoleUrlLink"
  ],
  "get_results_and_count": false,
  "full_graph_fetch": {
    "enabled": true
  },
  "debug_enable_bu_tags": true,
  "max_tier": 2
}'         --compressed

# get app service:
curl -X POST 'https://api.orcasecurity.io/api/serving-layer/query'         -H 'authority: api.orcasecurity.io'         -H 'accept: application/json, text/plain, */*'         -H 'accept-language: en-US,en;q=0.9'         -H 'authorization: TOKEN {{ORCA_API_TOKEN}}'         -H 'content-type: application/json'         --data-raw '{
  "query": {
    "models": [
      "AzureWebAppService"
    ],
    "type": "object_set"
  },
  "limit": 100,
  "start_at_index": 0,
  "order_by[]": [
    "-OrcaScore"
  ],
  "select": [
    "Name",
    "CloudAccount.Name",
    "CloudAccount.CloudProvider",
    "BusinessUnits.Name",
    "OrcaScore",
    "RiskLevel",
    "group_unique_id",
    "UiUniqueField",
    "IsInternetFacing",
    "SensitiveData.Name",
    "SensitiveData.SensitiveData",
    "Tags",
    "NewCategory",
    "NewSubCategory",
    "AssetUniqueId",
    "ConsoleUrlLink"
  ],
  "get_results_and_count": false,
  "full_graph_fetch": {
    "enabled": true
  },
  "debug_enable_bu_tags": true,
  "max_tier": 2
}'         --compressed

# get container nodes: we can assume 4vcore as base
curl -X POST 'https://api.orcasecurity.io/api/serving-layer/query'         -H 'authority: api.orcasecurity.io'         -H 'accept: application/json, text/plain, */*'         -H 'accept-language: en-US,en;q=0.9'         -H 'authorization: TOKEN {{ORCA_API_TOKEN}}'         -H 'content-type: application/json'         --data-raw '{
  "query": {
    "models": [
      "AwsEksNodegroup",
      "AzureAksNodePool",
      "K8sNode",
      "OciOkeNodePool",
      "K8sTaint",
      "TencentCloudTkeNode"
    ],
    "type": "object_set",
    "with": {
      "keys": [
        "CloudAccount"
      ],
      "models": [
        "CloudAccount"
      ],
      "type": "object",
      "operator": "has",
      "with": {
        "key": "CloudProvider",
        "values": [
          "azure"
        ],
        "type": "str",
        "operator": "in"
      }
    }
  },
  "limit": 100,
  "start_at_index": 0,
  "order_by[]": [
    "-OrcaScore"
  ],
  "select": [
    "Name",
    "CiSource",
    "CloudAccount.Name",
    "CloudAccount.CloudProvider",
    "BusinessUnits.Name",
    "OrcaScore",
    "RiskLevel",
    "group_unique_id",
    "UiUniqueField",
    "IsInternetFacing",
    "SensitiveData.Name",
    "SensitiveData.SensitiveData",
    "Tags",
    "NewCategory",
    "NewSubCategory",
    "AssetUniqueId",
    "ConsoleUrlLink"
  ],
  "get_results_and_count": false,
  "full_graph_fetch": {
    "enabled": true
  },
  "debug_enable_bu_tags": true,
  "max_tier": 2
}'         --compressed
