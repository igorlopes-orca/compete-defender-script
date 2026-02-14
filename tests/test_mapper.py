"""Tests for defender_savings.services.mapper."""

from __future__ import annotations

from defender_savings.services.mapper import ResourceDefenderMap
from conftest import (
    make_app,
    make_container_host,
    make_defender_config,
    make_kv,
    make_storage,
    make_vm,
)


def _make_map(*account_names: str) -> ResourceDefenderMap:
    configs = [make_defender_config(cloud_account_name=a) for a in account_names]
    return ResourceDefenderMap(configs)


def _empty(**overrides: list) -> dict:
    defaults: dict = {
        "vms": [],
        "app_services": [],
        "storage_accounts": [],
        "key_vaults": [],
        "container_hosts": [],
    }
    defaults.update(overrides)
    return defaults


# ── Count VMs per account ─────────────────────────────────────────────


def test_count_vms_per_account() -> None:
    rdm = _make_map("acct-1")
    counts = rdm.count_resources_per_account(
        **_empty(vms=[make_vm("acct-1"), make_vm("acct-1")])
    )
    assert counts["acct-1"]["virtual_machines"] == 2


# ── Unknown account resources ignored ─────────────────────────────────


def test_unknown_account_resources_ignored() -> None:
    rdm = _make_map("acct-1")
    counts = rdm.count_resources_per_account(
        **_empty(vms=[make_vm("unknown-acct")])
    )
    assert counts["acct-1"]["virtual_machines"] == 0


# ── Multi-account multi-resource-type ─────────────────────────────────


def test_multi_account_multi_resource() -> None:
    rdm = _make_map("a", "b")
    counts = rdm.count_resources_per_account(
        **_empty(
            vms=[make_vm("a"), make_vm("b"), make_vm("b")],
            app_services=[make_app("a")],
            storage_accounts=[make_storage("b")],
            key_vaults=[make_kv("a"), make_kv("a")],
        )
    )
    assert counts["a"]["virtual_machines"] == 1
    assert counts["a"]["app_services"] == 1
    assert counts["a"]["key_vaults"] == 2
    assert counts["b"]["virtual_machines"] == 2
    assert counts["b"]["storage_accounts"] == 1


# ── Container hosts contribute vcpu_count ─────────────────────────────


def test_container_hosts_contribute_vcpu_count() -> None:
    rdm = _make_map("acct-1")
    counts = rdm.count_resources_per_account(
        **_empty(
            container_hosts=[
                make_container_host("acct-1", vcpu_count=8),
                make_container_host("acct-1", vcpu_count=16),
            ]
        )
    )
    assert counts["acct-1"]["container_vcores"] == 24  # 8 + 16, not +1 each


# ── Subscriptions always = 1 ─────────────────────────────────────────


def test_subscriptions_always_one() -> None:
    rdm = _make_map("acct-1")
    counts = rdm.count_resources_per_account(**_empty())
    assert counts["acct-1"]["subscriptions"] == 1


# ── Empty resources → zeroes ──────────────────────────────────────────


def test_empty_resources_gives_zeroes() -> None:
    rdm = _make_map("acct-1")
    counts = rdm.count_resources_per_account(**_empty())
    assert counts["acct-1"]["virtual_machines"] == 0
    assert counts["acct-1"]["app_services"] == 0
    assert counts["acct-1"]["storage_accounts"] == 0
    assert counts["acct-1"]["key_vaults"] == 0
    assert counts["acct-1"]["container_vcores"] == 0


# ── get_config found ──────────────────────────────────────────────────


def test_get_config_found() -> None:
    cfg = make_defender_config(cloud_account_name="acct-1")
    rdm = ResourceDefenderMap([cfg])
    assert rdm.get_config("acct-1") is cfg


# ── get_config not found ─────────────────────────────────────────────


def test_get_config_not_found() -> None:
    rdm = ResourceDefenderMap([])
    assert rdm.get_config("nonexistent") is None
