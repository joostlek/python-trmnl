"""Asynchronous Python client for TRMNL."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiohttp.hdrs import METH_DELETE, METH_GET, METH_PATCH, METH_POST
from aioresponses import aioresponses
import pytest

from . import load_fixture
from .const import HEADERS, URL

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion
    from trmnl.trmnl import TRMNLClient


@pytest.mark.parametrize(
    ("method", "kwargs", "endpoint", "fixture"),
    [
        ("get_devices", {}, "devices", "devices"),
        ("get_device", {"device_id": 42793}, "devices/42793", "device"),
        ("get_me", {}, "me", "me"),
        ("get_playlist_items", {}, "playlists/items", "playlist_items"),
        ("get_plugin_settings", {}, "plugin_settings", "plugin_settings"),
        (
            "create_plugin_setting",
            {"name": "Hacker News", "plugin_id": 13},
            "plugin_settings",
            "plugin_setting",
        ),
    ],
    ids=[
        "get_devices",
        "get_device",
        "get_me",
        "get_playlist_items",
        "get_plugin_settings",
        "create_plugin_setting",
    ],
)
async def test_retrieve_data(
    responses: aioresponses,
    client: TRMNLClient,
    snapshot: SnapshotAssertion,
    method: str,
    kwargs: dict[str, Any],
    endpoint: str,
    fixture: str,
) -> None:
    """Test retrieving data."""
    if method == "create_plugin_setting":
        responses.post(
            f"{URL}{endpoint}",
            status=200,
            body=load_fixture(f"{fixture}.json"),
        )
    else:
        responses.get(
            f"{URL}{endpoint}",
            status=200,
            body=load_fixture(f"{fixture}.json"),
        )
    assert await getattr(client, method)(**kwargs) == snapshot
    if method == "create_plugin_setting":
        responses.assert_called_once_with(
            f"{URL}{endpoint}",
            METH_POST,
            headers=HEADERS,
            json={"name": "Hacker News", "plugin_id": 13},
        )
    else:
        responses.assert_called_once_with(
            f"{URL}{endpoint}",
            METH_GET,
            headers=HEADERS,
            json=None,
        )


async def test_update_device(
    responses: aioresponses,
    client: TRMNLClient,
) -> None:
    """Test updating a device."""
    responses.patch(
        f"{URL}devices/42793",
        status=200,
    )
    await client.update_device(42793, sleep_mode_enabled=True, sleep_start_time=1320)
    responses.assert_called_once_with(
        f"{URL}devices/42793",
        METH_PATCH,
        headers=HEADERS,
        json={"sleep_mode_enabled": True, "sleep_start_time": 1320},
    )


async def test_update_playlist_item(
    responses: aioresponses,
    client: TRMNLClient,
) -> None:
    """Test updating a playlist item."""
    responses.patch(
        f"{URL}playlists/items/523205",
        status=200,
    )
    await client.update_playlist_item(523205, visible=False)
    responses.assert_called_once_with(
        f"{URL}playlists/items/523205",
        METH_PATCH,
        headers=HEADERS,
        json={"visible": False},
    )


async def test_delete_plugin_setting(
    responses: aioresponses,
    client: TRMNLClient,
) -> None:
    """Test deleting a plugin setting."""
    responses.delete(
        f"{URL}plugin_settings/258760",
        status=204,
    )
    await client.delete_plugin_setting(258760)
    responses.assert_called_once_with(
        f"{URL}plugin_settings/258760",
        METH_DELETE,
        headers=HEADERS,
        json=None,
    )
