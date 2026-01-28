"""Button platform for Ha Health Record integration."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, EVENT_ACTIVITY_LOGGED
from .coordinator import HealthRecordCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities from a config entry."""
    coordinator: HealthRecordCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[ButtonEntity] = []

    # Create a log button for each activity set
    for activity_type, activity_set in coordinator.activity_sets.items():
        entities.append(
            ActivityLogButton(
                coordinator=coordinator,
                activity_type=activity_type,
            )
        )

    async_add_entities(entities)


class ActivityLogButton(ButtonEntity):
    """Button to log an activity record."""

    _attr_has_entity_name = True
    _attr_translation_key = "activity_log"

    def __init__(
        self,
        coordinator: HealthRecordCoordinator,
        activity_type: str,
    ) -> None:
        """Initialize the button."""
        self._coordinator = coordinator
        self._activity_type = activity_type
        activity_set = coordinator.get_activity_set(activity_type)

        self._attr_unique_id = f"{coordinator.member_id}_{activity_type}_log"
        self._attr_translation_placeholders = {"activity_name": activity_set.name}
        self._attr_device_info = coordinator.get_device_info()
        self._attr_icon = "mdi:content-save"

    async def async_press(self) -> None:
        """Handle the button press."""
        record = self._coordinator.log_activity(self._activity_type)

        if record is None:
            _LOGGER.warning("Failed to log activity: %s", self._activity_type)
            return

        activity_set = self._coordinator.get_activity_set(self._activity_type)

        # Fire event
        self.hass.bus.async_fire(
            EVENT_ACTIVITY_LOGGED,
            {
                "member_id": self._coordinator.member_id,
                "member_name": self._coordinator.member_name,
                "activity_type": self._activity_type,
                "activity_name": activity_set.name,
                "amount": record.amount,
                "unit": activity_set.unit,
                "note": record.note,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
            },
        )

        _LOGGER.info(
            "Activity logged: %s - %s %s (note: %s)",
            activity_set.name,
            record.amount,
            activity_set.unit,
            record.note,
        )

        # Trigger sensor update
        self.async_write_ha_state()
