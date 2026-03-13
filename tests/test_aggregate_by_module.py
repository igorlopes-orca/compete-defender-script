"""Tests for defender_savings.services.calculator.aggregate_by_module."""

from __future__ import annotations

import pytest

from defender_savings.services.calculator import aggregate_by_module, calculate_account_costs
from conftest import make_defender_config


def _summary(services_pricing: dict[str, str], counts: dict[str, int], sub_id: str = "sub-1"):
    config = make_defender_config(services_pricing=services_pricing, subscription_id=sub_id)
    return calculate_account_costs(config, counts)


# ── Empty input ───────────────────────────────────────────────────────


def test_empty_returns_empty() -> None:
    assert aggregate_by_module([]) == []


# ── Single account, single module ─────────────────────────────────────


def test_single_account_single_module() -> None:
    summary = _summary({"VirtualMachines": "Standard"}, {"virtual_machines": 5})
    result = aggregate_by_module([summary])

    assert len(result) == 1
    b = result[0]
    assert b.module == "VirtualMachines"
    assert b.subscription_count == 1
    assert b.total_qty == 5
    assert b.monthly_cost == pytest.approx(14.60 * 5)
    assert b.annual_cost == pytest.approx(14.60 * 5 * 12)


# ── Two accounts, same module — qty and cost summed, subs=2 ───────────


def test_two_accounts_same_module_aggregated() -> None:
    s1 = _summary({"VirtualMachines": "Standard"}, {"virtual_machines": 3}, sub_id="sub-1")
    s2 = _summary({"VirtualMachines": "Standard"}, {"virtual_machines": 5}, sub_id="sub-2")
    result = aggregate_by_module([s1, s2])

    assert len(result) == 1
    b = result[0]
    assert b.subscription_count == 2
    assert b.total_qty == 8
    assert b.monthly_cost == pytest.approx(14.60 * 8)


# ── Two accounts, different modules — two entries ─────────────────────


def test_two_accounts_different_modules() -> None:
    s1 = _summary({"VirtualMachines": "Standard"}, {"virtual_machines": 2}, sub_id="sub-1")
    s2 = _summary({"AppServices": "Standard"}, {"app_services": 4}, sub_id="sub-2")
    result = aggregate_by_module([s1, s2])

    modules = {b.module for b in result}
    assert modules == {"VirtualMachines", "AppServices"}
    assert len(result) == 2


# ── Sorted by monthly_cost descending ────────────────────────────────


def test_sorted_by_monthly_cost_descending() -> None:
    # VMs: 1 × $14.60, KeyVaults: 100 × $0.25 = $25 — KeyVaults should be first
    s1 = _summary(
        {"VirtualMachines": "Standard", "KeyVaults": "Standard"},
        {"virtual_machines": 1, "key_vaults": 100},
    )
    result = aggregate_by_module([s1])

    monthly_costs = [b.monthly_cost for b in result]
    assert monthly_costs == sorted(monthly_costs, reverse=True)


# ── Module present in only one of two accounts ────────────────────────


def test_module_in_one_account_only() -> None:
    s1 = _summary({"VirtualMachines": "Standard"}, {"virtual_machines": 2}, sub_id="sub-1")
    s2 = _summary({"AppServices": "Standard"}, {"app_services": 3}, sub_id="sub-2")
    result = aggregate_by_module([s1, s2])

    vm_entry = next(b for b in result if b.module == "VirtualMachines")
    assert vm_entry.subscription_count == 1

    app_entry = next(b for b in result if b.module == "AppServices")
    assert app_entry.subscription_count == 1


# ── Account with no costs (all zero resources) not counted ────────────


def test_zero_resource_account_not_counted() -> None:
    s_with = _summary({"VirtualMachines": "Standard"}, {"virtual_machines": 4}, sub_id="sub-1")
    s_without = _summary({"VirtualMachines": "Standard"}, {"virtual_machines": 0}, sub_id="sub-2")
    result = aggregate_by_module([s_with, s_without])

    assert len(result) == 1
    assert result[0].subscription_count == 1
    assert result[0].total_qty == 4


# ── unit_price and unit carried through correctly ─────────────────────


def test_unit_price_and_unit_preserved() -> None:
    summary = _summary({"Arm": "Standard"}, {"subscriptions": 1})
    result = aggregate_by_module([summary])

    assert len(result) == 1
    assert result[0].unit_price == pytest.approx(5.04)
    assert result[0].unit == "subscription/mo"
