"""Models for TRMNL."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class PluginSetting(DataClassORJSONMixin):
    """Plugin setting model."""

    identifier: int = field(metadata=field_options(alias="id"))
    name: str
    plugin_id: int


@dataclass
class PluginSettingResponse(DataClassORJSONMixin):
    """Plugin setting response."""

    data: PluginSetting


@dataclass
class PluginSettingsResponse(DataClassORJSONMixin):
    """Plugin settings list response."""

    data: list[PluginSetting]


@dataclass
class Device(DataClassORJSONMixin):
    """Device model."""

    identifier: int = field(metadata=field_options(alias="id"))
    name: str
    friendly_id: str
    model: str
    mac_address: str
    firmware_version: str | None
    battery_voltage: float | None
    rssi: int | None
    sleep_mode_enabled: bool
    sleep_start_time: int
    sleep_end_time: int
    percent_charged: float
    wifi_strength: int
    last_ping_at: str | None


@dataclass
class DeviceResponse(DataClassORJSONMixin):
    """Device response."""

    data: Device


@dataclass
class DevicesResponse(DataClassORJSONMixin):
    """Devices list response."""

    data: list[Device]


@dataclass
class User(DataClassORJSONMixin):
    """User model."""

    identifier: int = field(metadata=field_options(alias="id"))
    name: str
    email: str
    first_name: str | None
    last_name: str | None
    locale: str
    time_zone: str
    time_zone_iana: str
    utc_offset: int
    # Only returned when authenticated with the legacy account API key
    api_key: str | None = None


@dataclass
class UserResponse(DataClassORJSONMixin):
    """User response."""

    data: User


@dataclass
class PlaylistItem(DataClassORJSONMixin):
    """Playlist item model."""

    created_at: str
    device_id: int
    identifier: int = field(metadata=field_options(alias="id"))
    mashup_id: int | None
    mirror: bool
    plugin_setting_id: int | None
    rendered_at: str | None
    row_order: int
    updated_at: str
    visible: bool
    # Absent for mashup items
    plugin_setting: PluginSetting | None = None


@dataclass
class PlaylistItemsResponse(DataClassORJSONMixin):
    """Playlist items list response."""

    data: list[PlaylistItem]
