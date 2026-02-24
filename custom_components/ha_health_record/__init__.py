"""Ha Health Record integration for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HealthRecordCoordinator
from .panel import async_setup_panel, async_unload_panel

_LOGGER = logging.getLogger(__name__)

PLATFORMS_LIST: list[Platform] = [
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.TEXT,
    Platform.SENSOR,
]

# Key for tracking panel setup state in hass.data
PANEL_SETUP_KEY = "_panel_setup"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ha Health Record from a config entry."""
    hass.data.setdefault(DOMAIN, {PANEL_SETUP_KEY: False})

    coordinator = HealthRecordCoordinator(hass, entry)
    await coordinator.async_load()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_LIST)

    # Set up panel only once (for the first entry)
    if not hass.data[DOMAIN].get(PANEL_SETUP_KEY):
        await async_setup_panel(hass)
        hass.data[DOMAIN][PANEL_SETUP_KEY] = True

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS_LIST)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

        # Count remaining entries (excluding the panel setup key)
        remaining_entries = [
            k for k in hass.data[DOMAIN] if k != PANEL_SETUP_KEY
        ]

        # Unload panel if no more entries
        if not remaining_entries and hass.data[DOMAIN].get(PANEL_SETUP_KEY):
            await async_unload_panel(hass)
            hass.data[DOMAIN][PANEL_SETUP_KEY] = False

    return unload_ok
