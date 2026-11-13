"""Asynchronous Python client for TRMNL."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_PATCH, METH_POST
from aiointercept import aiointercept
import pytest

from trmnl import TRMNLClient
from trmnl.exceptions import (
    TRMNLAuthenticationError,
    TRMNLError,
    TRMNLForbiddenError,
    TRMNLNotFoundError,
    TRMNLRateLimitError,
)

from . import load_fixture
from .const import HEADERS, URL

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


@pytest.mark.parametrize(
    ("method", "kwargs", "endpoint", "fixture"),
    [
        ("get_devices", {}, "devices", "devices"),
        ("get_device", {"device_id": 42793}, "devices/42793", "device"),
        ("get_me", {}, "me", "me"),
        ("get_me", {}, "me", "me_without_api_key"),
        ("get_playlist_items", {}, "playlists/items", "playlist_items"),
        ("get_plugin_settings", {}, "plugin_settings", "plugin_settings"),
    ],
    ids=[
        "get_devices",
        "get_device",
        "get_me",
        "get_me_without_api_key",
        "get_playlist_items",
        "get_plugin_settings",
    ],
)
async def test_get(  # noqa: PLR0917
    responses: aiointercept,
    client: TRMNLClient,
    snapshot: SnapshotAssertion,
    method: str,
    kwargs: dict[str, Any],
    endpoint: str,
    fixture: str,
) -> None:
    """Test GET endpoints."""
    responses.get(
        f"{URL}{endpoint}",
        status=200,
        body=load_fixture(f"{fixture}.json"),
    )
    assert await getattr(client, method)(**kwargs) == snapshot
    responses.assert_called_once_with(
        f"{URL}{endpoint}",
        METH_GET,
        headers=HEADERS,
        json=None,
    )


async def test_create_plugin_setting(
    responses: aiointercept,
    client: TRMNLClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test creating a plugin setting."""
    responses.post(
        f"{URL}plugin_settings",
        status=200,
        body=load_fixture("plugin_setting.json"),
    )
    assert await client.create_plugin_setting("Hacker News", 13) == snapshot
    responses.assert_called_once_with(
        f"{URL}plugin_settings",
        METH_POST,
        headers=HEADERS,
        json={"name": "Hacker News", "plugin_id": 13},
    )


async def test_update_device(
    responses: aiointercept,
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
    responses: aiointercept,
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
    responses: aiointercept,
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


async def test_authentication_error(
    responses: aiointercept,
    client: TRMNLClient,
) -> None:
    """Test that a 401 response raises TRMNLAuthenticationError."""
    responses.get(f"{URL}devices", status=401)
    with pytest.raises(TRMNLAuthenticationError):
        await client.get_devices()


@pytest.mark.parametrize(
    ("status", "body", "error", "message"),
    [
        (
            403,
            '{"error": "This is a legacy API key."}',
            TRMNLForbiddenError,
            "Request failed with status 403: This is a legacy API key.",
        ),
        (
            404,
            '{"error": "Device not found"}',
            TRMNLNotFoundError,
            "Request failed with status 404: Device not found",
        ),
        (500, "", TRMNLError, "Request failed with status 500."),
        (
            502,
            "<html>Bad Gateway</html>",
            TRMNLError,
            "Request failed with status 502.",
        ),
    ],
    ids=["forbidden", "not_found", "empty_body", "html_body"],
)
async def test_error(  # noqa: PLR0917
    responses: aiointercept,
    client: TRMNLClient,
    status: int,
    body: str,
    error: type[TRMNLError],
    message: str,
) -> None:
    """Test that an error response raises with the server's reason."""
    responses.get(f"{URL}devices", status=status, body=body)
    with pytest.raises(error) as exc_info:
        await client.get_devices()
    assert str(exc_info.value) == message


@pytest.mark.parametrize(
    ("headers", "retry_after"),
    [({"Retry-After": "3600"}, 3600), (None, None)],
    ids=["retry_after", "no_retry_after"],
)
async def test_rate_limit_error(
    responses: aiointercept,
    client: TRMNLClient,
    headers: dict[str, str] | None,
    retry_after: int | None,
) -> None:
    """Test that a 429 raises with the reason and the Retry-After seconds."""
    responses.get(
        f"{URL}devices",
        status=429,
        body='{"error": "Rate limit exceeded."}',
        headers=headers,
    )
    with pytest.raises(TRMNLRateLimitError) as exc_info:
        await client.get_devices()
    assert str(exc_info.value) == "Request failed with status 429: Rate limit exceeded."
    assert exc_info.value.retry_after == retry_after


async def test_custom_base_url(responses: aiointercept) -> None:
    """Test that requests go to a custom base URL."""
    responses.get(
        "http://byos.local:2300/api/devices",
        status=200,
        body=load_fixture("devices.json"),
    )
    async with (
        aiohttp.ClientSession() as session,
        TRMNLClient(
            "token", session=session, base_url="http://byos.local:2300"
        ) as client,
    ):
        await client.get_devices()
    responses.assert_called_once_with(
        "http://byos.local:2300/api/devices",
        METH_GET,
        headers=HEADERS,
        json=None,
    )
