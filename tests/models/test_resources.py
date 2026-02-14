"""Tests for defender_savings.models.resources — asset parsing and vCPU fallback."""

from __future__ import annotations

import pytest

from defender_savings.models.resources import (
    AppService,
    ContainerHost,
    KeyVault,
    StorageAccount,
    VirtualMachine,
)
from conftest import make_orca_asset_item


# ── Parametrized parsing for simple types ─────────────────────────────


@pytest.mark.parametrize(
    "cls",
    [
        pytest.param(VirtualMachine, id="VirtualMachine"),
        pytest.param(AppService, id="AppService"),
        pytest.param(StorageAccount, id="StorageAccount"),
        pytest.param(KeyVault, id="KeyVault"),
    ],
)
def test_simple_asset_parsing(cls: type) -> None:
    item = make_orca_asset_item(
        name="my-resource",
        cloud_account_name="acct-prod",
        asset_unique_id="uid-42",
    )
    obj = cls.from_orca_response(item)

    assert obj.name == "my-resource"
    assert obj.cloud_account_name == "acct-prod"
    assert obj.asset_unique_id == "uid-42"


# ── ContainerHost with explicit VCpuCount ─────────────────────────────


def test_container_host_explicit_vcpu() -> None:
    item = make_orca_asset_item(
        name="host-1",
        extra_data={"VCpuCount": {"value": 16}},
    )
    host = ContainerHost.from_orca_response(item)
    assert host.vcpu_count == 16


# ── ContainerHost default vCPU = 4 ───────────────────────────────────


def test_container_host_default_vcpu() -> None:
    item = make_orca_asset_item(name="host-no-vcpu")
    host = ContainerHost.from_orca_response(item)
    assert host.vcpu_count == 4


# ── Invalid VCpuCount values → default 4 ─────────────────────────────


@pytest.mark.parametrize(
    "vcpu_value",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param("eight", id="string"),
        pytest.param(None, id="none"),
        pytest.param(3.5, id="float"),
    ],
)
def test_invalid_vcpu_defaults_to_4(vcpu_value: object) -> None:
    item = make_orca_asset_item(
        name="host-bad-vcpu",
        extra_data={"VCpuCount": {"value": vcpu_value}},
    )
    host = ContainerHost.from_orca_response(item)
    assert host.vcpu_count == 4


# ── Missing data → empty strings ─────────────────────────────────────


def test_missing_data_gives_empty_strings() -> None:
    item: dict = {}
    vm = VirtualMachine.from_orca_response(item)
    assert vm.name == ""
    assert vm.cloud_account_name == ""
    assert vm.asset_unique_id == ""


# ── Fallback to item-level name/id ───────────────────────────────────


def test_fallback_to_item_level_fields() -> None:
    item = {"name": "item-name", "id": "item-id", "data": {}}
    vm = VirtualMachine.from_orca_response(item)
    assert vm.name == "item-name"
    assert vm.asset_unique_id == "item-id"
