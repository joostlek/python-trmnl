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
    mac_address: str
    battery_voltage: float | None
    rssi: int | None
    sleep_mode_enabled: bool
    sleep_start_time: int
    sleep_end_time: int
    percent_charged: float
    wifi_strength: int


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
    first_name: str
    last_name: str
    locale: str
    time_zone: str
    time_zone_iana: str
    utc_offset: int
    api_key: str


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
    plugin_setting_id: int
    rendered_at: str
    row_order: int
    updated_at: str
    visible: bool
    plugin_setting: PluginSetting


@dataclass
class PlaylistItemsResponse(DataClassORJSONMixin):
    """Playlist items list response."""

    data: list[PlaylistItem]
