"""Text platform for Ha Health Record integration."""
from __future__ import annotations

import logging

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HealthRecordCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up text entities from a config entry."""
    coordinator: HealthRecordCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[TextEntity] = []

    # Create note input for each activity set
    for activity_type, activity_set in coordinator.activity_sets.items():
        entities.append(
            ActivityNoteText(
                coordinator=coordinator,
                activity_type=activity_type,
            )
        )

    async_add_entities(entities)


class ActivityNoteText(TextEntity):
    """Text entity for activity note input."""

    _attr_has_entity_name = True
    _attr_mode = TextMode.TEXT
    _attr_native_max = 255
    _attr_translation_key = "activity_note"

    def __init__(
        self,
        coordinator: HealthRecordCoordinator,
        activity_type: str,
    ) -> None:
        """Initialize the text entity."""
        self._coordinator = coordinator
        self._activity_type = activity_type
        activity_set = coordinator.get_activity_set(activity_type)

        self._attr_unique_id = f"{coordinator.member_id}_{activity_type}_note"
        self._attr_translation_placeholders = {"activity_name": activity_set.name}
        self._attr_device_info = coordinator.get_device_info()
        self._attr_icon = "mdi:note-text"

    @property
    def native_value(self) -> str | None:
        """Return the current value."""
        activity_set = self._coordinator.get_activity_set(self._activity_type)
        return activity_set.current_note if activity_set else None

    async def async_set_value(self, value: str) -> None:
        """Set the value."""
        self._coordinator.set_activity_note(self._activity_type, value)
        self.async_write_ha_state()
