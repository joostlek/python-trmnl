"""Asynchronous Python client for TRMNL."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any, Self

from aiohttp import ClientSession
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_PATCH, METH_POST
from yarl import URL

from trmnl.exceptions import TRMNLAuthenticationError, TRMNLError
from trmnl.models import (
    Device,
    DeviceResponse,
    DevicesResponse,
    PlaylistItem,
    PlaylistItemsResponse,
    PluginSetting,
    PluginSettingResponse,
    PluginSettingsResponse,
    User,
    UserResponse,
)

VERSION = "1"

_LOGGER = logging.getLogger(__package__)

HOST = "trmnl.com"


@dataclass
class TRMNLClient:
    """Main class for handling connections with the TRMNL API."""

    token: str
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to the TRMNL API."""
        url = URL.build(host=HOST, scheme="https").joinpath(f"api/{uri}")
        headers = {
            "User-Agent": f"python-trmnl/{VERSION}",
            "Authorization": f"Bearer {self.token}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        async with asyncio.timeout(self.request_timeout):
            response = await self.session.request(
                method,
                url,
                headers=headers,
                json=data,
            )

        if response.status == 401:
            raise TRMNLAuthenticationError(
                "Authentication failed. Check your API token."
            )

        if response.status >= 400:
            raise TRMNLError(f"Request failed with status {response.status}.")

        return await response.text()

    async def _get(self, uri: str) -> str:
        """Handle a GET request to the TRMNL API."""
        return await self._request(uri, method=METH_GET)

    async def _patch(self, uri: str, data: dict[str, Any]) -> str:
        """Handle a PATCH request to the TRMNL API."""
        return await self._request(uri, method=METH_PATCH, data=data)

    async def _post(self, uri: str, data: dict[str, Any]) -> str:
        """Handle a POST request to the TRMNL API."""
        return await self._request(uri, method=METH_POST, data=data)

    async def _delete(self, uri: str) -> None:
        """Handle a DELETE request to the TRMNL API."""
        await self._request(uri, method=METH_DELETE)

    async def get_devices(self) -> list[Device]:
        """Retrieve the list of devices."""
        result = await self._get("devices")
        return DevicesResponse.from_json(result).data

    async def get_device(self, device_id: int) -> Device:
        """Retrieve a single device by ID."""
        result = await self._get(f"devices/{device_id}")
        return DeviceResponse.from_json(result).data

    async def update_device(
        self,
        device_id: int,
        *,
        sleep_mode_enabled: bool | None = None,
        sleep_start_time: int | None = None,
        sleep_end_time: int | None = None,
        percent_charged: float | None = None,
    ) -> None:
        """Update a device."""
        payload: dict[str, Any] = {}
        if sleep_mode_enabled is not None:
            payload["sleep_mode_enabled"] = sleep_mode_enabled
        if sleep_start_time is not None:
            payload["sleep_start_time"] = sleep_start_time
        if sleep_end_time is not None:
            payload["sleep_end_time"] = sleep_end_time
        if percent_charged is not None:
            payload["percent_charged"] = percent_charged
        await self._patch(f"devices/{device_id}", payload)

    async def get_me(self) -> User:
        """Retrieve the current user."""
        result = await self._get("me")
        return UserResponse.from_json(result).data

    async def get_playlist_items(self) -> list[PlaylistItem]:
        """Retrieve all playlist items."""
        result = await self._get("playlists/items")
        return PlaylistItemsResponse.from_json(result).data

    async def update_playlist_item(self, item_id: int, *, visible: bool) -> None:
        """Update a playlist item's visibility."""
        await self._patch(f"playlists/items/{item_id}", {"visible": visible})

    async def get_plugin_settings(
        self, plugin_id: int | None = None
    ) -> list[PluginSetting]:
        """Retrieve plugin settings, optionally filtered by plugin_id."""
        uri = "plugin_settings"
        if plugin_id is not None:
            uri = f"{uri}?plugin_id={plugin_id}"
        result = await self._get(uri)
        return PluginSettingsResponse.from_json(result).data

    async def create_plugin_setting(self, name: str, plugin_id: int) -> PluginSetting:
        """Create a new plugin setting."""
        result = await self._post(
            "plugin_settings", {"name": name, "plugin_id": plugin_id}
        )
        return PluginSettingResponse.from_json(result).data

    async def delete_plugin_setting(self, plugin_setting_id: int) -> None:
        """Delete a plugin setting."""
        await self._delete(f"plugin_settings/{plugin_setting_id}")

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The TRMNLClient object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
