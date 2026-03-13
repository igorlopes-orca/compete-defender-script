import logging

from pydantic import BaseModel

from defender_savings.config import PRICING
from defender_savings.models.defender import DefenderConfig

logger = logging.getLogger(__name__)


class CostLineItem(BaseModel):
    cloud_account: str
    module: str
    description: str
    tier: str
    count: int
    unit_price: float
    unit: str
    monthly_cost: float
    annual_cost: float


class SavingsLineItem(BaseModel):
    cloud_account: str
    module: str
    description: str
    monthly_saving: float
    annual_saving: float


class AccountSummary(BaseModel):
    cloud_account: str
    costs: list[CostLineItem]
    savings: list[SavingsLineItem]
    total_monthly: float
    total_annual: float
    potential_monthly_saving: float
    potential_annual_saving: float


class ModuleBreakdown(BaseModel):
    module: str
    description: str
    subscription_count: int
    total_qty: int
    unit_price: float
    unit: str
    monthly_cost: float
    annual_cost: float


def calculate_account_costs(
    config: DefenderConfig,
    resource_counts: dict[str, int],
) -> AccountSummary:
    """Calculate costs and savings for a single cloud account.

    Only includes services that are enabled (Standard) in the API response
    AND have actual resources. Savings = disabling that service entirely.
    """
    resource_counts = {**resource_counts}  # avoid mutating caller's dict
    costs: list[CostLineItem] = []
    savings: list[SavingsLineItem] = []
    total_monthly = 0.0

    # Compute CSPM billable count
    cspm_billable = (
        resource_counts.get("virtual_machines", 0)
        + resource_counts.get("storage_accounts", 0)
    )
    resource_counts["_cspm_billable"] = cspm_billable

    for module, tier in config.services_pricing.items():
        if tier != "Standard":
            continue

        if module not in PRICING:
            logger.debug("Skipping module %s (no pricing info)", module)
            continue

        pricing = PRICING[module]
        count = resource_counts.get(pricing["count_key"], 0)
        if count == 0:
            logger.debug("Skipping module %s (0 resources)", module)
            continue

        monthly = pricing["unit_price"] * count

        costs.append(CostLineItem(
            cloud_account=config.subscription_id or config.cloud_account_name,
            module=module,
            description=pricing["description"],
            tier=tier,
            count=count,
            unit_price=pricing["unit_price"],
            unit=pricing["unit"],
            monthly_cost=monthly,
            annual_cost=monthly * 12,
        ))
        total_monthly += monthly

        savings.append(SavingsLineItem(
            cloud_account=config.subscription_id or config.cloud_account_name,
            module=module,
            description=pricing["description"],
            monthly_saving=monthly,
            annual_saving=monthly * 12,
        ))

    costs.sort(key=lambda x: x.monthly_cost, reverse=True)
    savings.sort(key=lambda x: x.monthly_saving, reverse=True)
    total_saving = sum(s.monthly_saving for s in savings)

    logger.info(
        "Account %s: $%.2f/mo, potential savings $%.2f/mo",
        config.cloud_account_name, total_monthly, total_saving,
    )

    return AccountSummary(
        cloud_account=config.subscription_id or config.cloud_account_name,
        costs=costs,
        savings=savings,
        total_monthly=total_monthly,
        total_annual=total_monthly * 12,
        potential_monthly_saving=total_saving,
        potential_annual_saving=total_saving * 12,
    )


def aggregate_by_module(summaries: list[AccountSummary]) -> list[ModuleBreakdown]:
    """Aggregate costs across all accounts, grouped by module."""
    acc: dict[str, dict] = {}

    for summary in summaries:
        for cost in summary.costs:
            if cost.module not in acc:
                acc[cost.module] = {
                    "description": cost.description,
                    "unit_price": cost.unit_price,
                    "unit": cost.unit,
                    "subscription_count": 0,
                    "total_qty": 0,
                    "monthly_cost": 0.0,
                    "annual_cost": 0.0,
                    "seen_accounts": set(),
                }
            entry = acc[cost.module]
            entry["seen_accounts"].add(cost.cloud_account)
            entry["total_qty"] += cost.count
            entry["monthly_cost"] += cost.monthly_cost
            entry["annual_cost"] += cost.annual_cost

    breakdowns = [
        ModuleBreakdown(
            module=module,
            description=entry["description"],
            subscription_count=len(entry["seen_accounts"]),
            total_qty=entry["total_qty"],
            unit_price=entry["unit_price"],
            unit=entry["unit"],
            monthly_cost=entry["monthly_cost"],
            annual_cost=entry["annual_cost"],
        )
        for module, entry in acc.items()
    ]
    breakdowns.sort(key=lambda x: x.monthly_cost, reverse=True)
    return breakdowns
