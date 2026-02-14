import logging

from defender_savings.api.client import OrcaClient
from defender_savings.models.defender import DefenderConfig

logger = logging.getLogger(__name__)

_DEFENDER_SELECT = [
    "Name",
    "CloudAccount.Name",
    "CloudAccount.CloudProvider",
    "BusinessUnits.Name",
    "AutoProvisioning",
    "PolicyAssignments",
    "SecurityCenterSubscription",
    "SecurityContacts",
    "ServicesPricing",
    "Settings",
]


def list_defender_configs(client: OrcaClient) -> list[DefenderConfig]:
    """Fetch all AzureDefenderForCloud objects from Orca."""
    logger.info("Fetching Defender for Cloud configurations")
    items = client.query(
        models=["AzureDefenderForCloud"],
        select=_DEFENDER_SELECT,
    )

    configs: list[DefenderConfig] = []
    for item in items:
        configs.append(DefenderConfig.from_orca_response(item))

    logger.info("Found %d Defender configurations", len(configs))
    return configs
