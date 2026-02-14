"""Tests for defender_savings.services.calculator."""

from __future__ import annotations

import pytest

from defender_savings.config import PRICING
from defender_savings.services.calculator import calculate_account_costs
from conftest import make_defender_config


# ── Parametrized: single service cost ──────────────────────────────────

_SINGLE_SERVICE_CASES = [
    (module, info["unit_price"], info["count_key"])
    for module, info in PRICING.items()
]


@pytest.mark.parametrize("module,unit_price,count_key", _SINGLE_SERVICE_CASES, ids=[m for m in PRICING])
def test_single_service_cost(module: str, unit_price: float, count_key: str) -> None:
    config = make_defender_config(services_pricing={module: "Standard"})
    # _cspm_billable is derived from VMs + storage; seed those instead
    if count_key == "_cspm_billable":
        counts = {"virtual_machines": 2, "storage_accounts": 1}
    else:
        counts = {count_key: 3}
    result = calculate_account_costs(config, counts)

    assert len(result.costs) == 1
    item = result.costs[0]
    expected = unit_price * 3
    assert item.monthly_cost == pytest.approx(expected)
    assert item.annual_cost == pytest.approx(expected * 12)
    assert item.count == 3
    assert item.unit_price == unit_price


# ── CSPM billable = VMs + storage accounts ────────────────────────────


def test_cspm_billable_derived_from_vms_and_storage() -> None:
    config = make_defender_config(services_pricing={"CloudPosture": "Standard"})
    counts = {"virtual_machines": 5, "storage_accounts": 3}
    result = calculate_account_costs(config, counts)

    assert len(result.costs) == 1
    assert result.costs[0].count == 8  # 5 + 3
    assert result.costs[0].monthly_cost == pytest.approx(5.00 * 8)


def test_cspm_zero_when_no_vms_or_storage() -> None:
    config = make_defender_config(services_pricing={"CloudPosture": "Standard"})
    counts: dict[str, int] = {}
    result = calculate_account_costs(config, counts)

    assert len(result.costs) == 0  # skipped because count=0


# ── Free / non-Standard tiers skipped ─────────────────────────────────


@pytest.mark.parametrize("tier", ["Free", "free", "Basic", ""])
def test_free_tier_skipped(tier: str) -> None:
    config = make_defender_config(services_pricing={"VirtualMachines": tier})
    counts = {"virtual_machines": 10}
    result = calculate_account_costs(config, counts)

    assert result.costs == []
    assert result.total_monthly == 0.0


# ── Unknown module skipped ────────────────────────────────────────────


def test_unknown_module_skipped() -> None:
    config = make_defender_config(services_pricing={"FakeModule": "Standard"})
    counts = {"fake_stuff": 10}
    result = calculate_account_costs(config, counts)

    assert result.costs == []


# ── Zero resources skipped ────────────────────────────────────────────


def test_zero_resources_skipped() -> None:
    config = make_defender_config(services_pricing={"VirtualMachines": "Standard"})
    counts = {"virtual_machines": 0}
    result = calculate_account_costs(config, counts)

    assert result.costs == []


# ── Multi-service combined cost ───────────────────────────────────────


def test_multi_service_combined() -> None:
    services = {
        "VirtualMachines": "Standard",
        "AppServices": "Standard",
        "KeyVaults": "Standard",
        "Arm": "Standard",
        "StorageAccounts": "Standard",
    }
    config = make_defender_config(services_pricing=services)
    counts = {
        "virtual_machines": 10,
        "app_services": 5,
        "key_vaults": 20,
        "subscriptions": 1,
        "storage_accounts": 3,
    }
    result = calculate_account_costs(config, counts)

    expected = (
        14.60 * 10  # VMs
        + 14.60 * 5  # AppServices
        + 0.25 * 20  # KeyVaults
        + 5.04 * 1   # Arm
        + 10.00 * 3  # Storage
    )
    assert result.total_monthly == pytest.approx(expected)
    assert result.total_annual == pytest.approx(expected * 12)
    assert len(result.costs) == 5


# ── Savings = costs (full removal) ────────────────────────────────────


def test_savings_equals_costs() -> None:
    config = make_defender_config(services_pricing={"VirtualMachines": "Standard"})
    counts = {"virtual_machines": 7}
    result = calculate_account_costs(config, counts)

    assert result.potential_monthly_saving == result.total_monthly
    assert result.potential_annual_saving == result.total_annual


# ── Costs sorted descending ──────────────────────────────────────────


def test_costs_sorted_descending() -> None:
    services = {
        "VirtualMachines": "Standard",
        "KeyVaults": "Standard",
        "Arm": "Standard",
    }
    config = make_defender_config(services_pricing=services)
    counts = {"virtual_machines": 2, "key_vaults": 1, "subscriptions": 1}
    result = calculate_account_costs(config, counts)

    monthly_costs = [c.monthly_cost for c in result.costs]
    assert monthly_costs == sorted(monthly_costs, reverse=True)


# ── Empty services_pricing ────────────────────────────────────────────


def test_empty_services_pricing() -> None:
    config = make_defender_config(services_pricing={})
    counts = {"virtual_machines": 10}
    result = calculate_account_costs(config, counts)

    assert result.costs == []
    assert result.savings == []
    assert result.total_monthly == 0.0


# ── resource_counts not mutated ──────────────────────────────────────


def test_resource_counts_not_mutated() -> None:
    config = make_defender_config(services_pricing={"CloudPosture": "Standard"})
    counts = {"virtual_machines": 2, "storage_accounts": 3}
    original = dict(counts)
    calculate_account_costs(config, counts)

    assert counts == original
    assert "_cspm_billable" not in counts
