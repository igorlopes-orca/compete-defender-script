from __future__ import annotations

import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DefenderConfig(BaseModel):
    """Defender for Cloud configuration for a subscription, from Orca API."""

    name: str
    cloud_account_name: str
    subscription_id: str
    services_pricing: dict[str, str]  # plan_name -> tier

    @classmethod
    def from_orca_response(cls, item: dict) -> DefenderConfig:
        """Parse an AzureDefenderForCloud item from Orca's serving-layer response.

        Response structure:
            {
                "id": "...", "name": "...", "type": "...",
                "data": {
                    "Name": {"value": "DefenderForCloud"},
                    "ServicesPricing": {"value": {"VirtualMachines": "Standard", ...}},
                    "SecurityCenterSubscription": {"value": "sub-id-here"},
                    "CloudAccount": {"name": "EA-Shape-Prod", ...},
                    ...
                }
            }
        """
        data = item.get("data", {})

        # CloudAccount is a nested object directly under data (not value-wrapped)
        cloud_account = data.get("CloudAccount", {})
        account_name = cloud_account.get("name", "") if isinstance(cloud_account, dict) else ""

        # Fields under data are value-wrapped: {"value": actual_value}
        sub_id = data.get("SecurityCenterSubscription", {}).get("value", "")
        name = data.get("Name", {}).get("value", item.get("name", ""))

        # ServicesPricing.value is a dict: {plan_name: tier_string}
        services = data.get("ServicesPricing", {}).get("value", {})
        if not isinstance(services, dict):
            logger.warning("Unexpected ServicesPricing format: %s", type(services).__name__)
            services = {}

        logger.debug(
            "Parsed DefenderConfig: account=%s sub=%s plans=%d",
            account_name, sub_id, len(services),
        )

        return cls(
            name=name,
            cloud_account_name=account_name,
            subscription_id=sub_id,
            services_pricing=services,
        )
