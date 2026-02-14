"""Tests for defender_savings.models.defender.DefenderConfig.from_orca_response."""

from __future__ import annotations

import pytest

from defender_savings.models.defender import DefenderConfig
from conftest import make_orca_defender_item


# ── Happy path ────────────────────────────────────────────────────────


def test_parse_full_response() -> None:
    item = make_orca_defender_item(
        name="DefenderForCloud",
        cloud_account_name="EA-Prod",
        subscription_id="sub-abc",
        services_pricing={"VirtualMachines": "Standard", "KeyVaults": "Free"},
    )
    cfg = DefenderConfig.from_orca_response(item)

    assert cfg.name == "DefenderForCloud"
    assert cfg.cloud_account_name == "EA-Prod"
    assert cfg.subscription_id == "sub-abc"
    assert cfg.services_pricing == {"VirtualMachines": "Standard", "KeyVaults": "Free"}


# ── Missing fields → empty strings ───────────────────────────────────


@pytest.mark.parametrize(
    "item,expected_name,expected_account,expected_sub",
    [
        pytest.param({}, "", "", "", id="empty-dict"),
        pytest.param({"data": {}}, "", "", "", id="empty-data"),
        pytest.param(
            {"data": {"Name": {}, "CloudAccount": {}, "SecurityCenterSubscription": {}}},
            "",
            "",
            "",
            id="missing-value-keys",
        ),
        pytest.param(
            {"name": "fallback-name", "data": {}},
            "fallback-name",
            "",
            "",
            id="fallback-to-item-name",
        ),
    ],
)
def test_missing_fields(
    item: dict,
    expected_name: str,
    expected_account: str,
    expected_sub: str,
) -> None:
    cfg = DefenderConfig.from_orca_response(item)
    assert cfg.name == expected_name
    assert cfg.cloud_account_name == expected_account
    assert cfg.subscription_id == expected_sub


# ── Invalid ServicesPricing types → empty dict ───────────────────────


@pytest.mark.parametrize(
    "services_value",
    [
        pytest.param("not-a-dict", id="string"),
        pytest.param(["list"], id="list"),
        pytest.param(42, id="int"),
        pytest.param(None, id="none"),
    ],
)
def test_invalid_services_pricing_types(services_value: object) -> None:
    item = {
        "data": {
            "ServicesPricing": {"value": services_value},
            "CloudAccount": {"name": "acct"},
        }
    }
    cfg = DefenderConfig.from_orca_response(item)
    assert cfg.services_pricing == {}


# ── CloudAccount not a dict → empty string ───────────────────────────


def test_cloud_account_not_dict() -> None:
    item = {"data": {"CloudAccount": "just-a-string"}}
    cfg = DefenderConfig.from_orca_response(item)
    assert cfg.cloud_account_name == ""
