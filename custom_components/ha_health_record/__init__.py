"""Ha Health Record integration for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import CONF_MEMBER_ID, DOMAIN, STORAGE_KEY, STORAGE_VERSION
from .coordinator import HealthRecordCoordinator
from .panel import async_setup_panel, async_unload_panel, register_websocket_commands

_LOGGER = logging.getLogger(__name__)

type HaHealthRecordConfigEntry = ConfigEntry[HealthRecordCoordinator]

PLATFORMS_LIST: list[Platform] = [
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.TEXT,
    Platform.SENSOR,
]

# Keys for tracking one-time setup state in hass.data
_KEY_WS_REGISTERED = f"{DOMAIN}_ws_registered"
_KEY_PANEL_REGISTERED = f"{DOMAIN}_panel_registered"


async def async_setup_entry(
    hass: HomeAssistant, entry: HaHealthRecordConfigEntry
) -> bool:
    """Set up Ha Health Record from a config entry."""
    coordinator = HealthRecordCoordinator(hass, entry)
    try:
        await coordinator.async_load()
    except Exception:
        _LOGGER.exception("Failed to load health record data for %s", entry.title)
        return False

    entry.runtime_data = coordinator

    # Register WS commands once (they persist across entry reloads)
    if not hass.data.get(_KEY_WS_REGISTERED):
        register_websocket_commands(hass)
        hass.data[_KEY_WS_REGISTERED] = True

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_LIST)

    # Set up panel only once (for the first entry).
    # Set flag before awaiting to prevent concurrent entries from double-registering.
    if not hass.data.get(_KEY_PANEL_REGISTERED):
        hass.data[_KEY_PANEL_REGISTERED] = True
        try:
            await async_setup_panel(hass)
        except Exception:
            hass.data[_KEY_PANEL_REGISTERED] = False
            raise

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(
    hass: HomeAssistant, entry: HaHealthRecordConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant, entry: HaHealthRecordConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS_LIST)

    if unload_ok:
        # Check if any other loaded entries remain
        remaining = [
            e
            for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id
            and e.state is ConfigEntryState.LOADED
        ]

        # Unload panel if no more entries
        if not remaining and hass.data.get(_KEY_PANEL_REGISTERED):
            await async_unload_panel(hass)
            hass.data[_KEY_PANEL_REGISTERED] = False

    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove a config entry and clean up its storage file."""
    member_id = entry.data.get(CONF_MEMBER_ID)
    if member_id:
        store: Store[dict] = Store(
            hass, STORAGE_VERSION, f"{STORAGE_KEY}_{member_id}"
        )
        await store.async_remove()
