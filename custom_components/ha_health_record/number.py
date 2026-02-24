"""Number platform for Ha Health Record integration."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
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
    """Set up number entities from a config entry."""
    coordinator: HealthRecordCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NumberEntity] = []

    # Create amount input for each activity set
    for activity_type, activity_set in coordinator.activity_sets.items():
        entities.append(
            ActivityAmountNumber(
                coordinator=coordinator,
                activity_type=activity_type,
            )
        )

    # Create value input for each growth set
    for growth_type, growth_set in coordinator.growth_sets.items():
        entities.append(
            GrowthValueNumber(
                coordinator=coordinator,
                growth_type=growth_type,
            )
        )

    async_add_entities(entities)


class ActivityAmountNumber(NumberEntity):
    """Number entity for activity amount input."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0
    _attr_native_max_value = 10000
    _attr_native_step = 1
    _attr_translation_key = "activity_amount"

    def __init__(
        self,
        coordinator: HealthRecordCoordinator,
        activity_type: str,
    ) -> None:
        """Initialize the number entity."""
        self._coordinator = coordinator
        self._activity_type = activity_type
        activity_set = coordinator.get_activity_set(activity_type)

        self._attr_unique_id = f"{coordinator.member_id}_{activity_type}_amount"
        self._attr_translation_placeholders = {"activity_name": activity_set.name}
        self._attr_native_unit_of_measurement = activity_set.unit
        self._attr_device_info = coordinator.get_device_info()
        self._attr_icon = "mdi:numeric"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        activity_set = self._coordinator.get_activity_set(self._activity_type)
        return activity_set.current_amount if activity_set else None

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        self._coordinator.set_activity_amount(self._activity_type, value)
        self.async_write_ha_state()


class GrowthValueNumber(NumberEntity):
    """Number entity for growth value input."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0
    _attr_native_max_value = 1000
    _attr_native_step = 0.1
    _attr_translation_key = "growth_input"

    def __init__(
        self,
        coordinator: HealthRecordCoordinator,
        growth_type: str,
    ) -> None:
        """Initialize the number entity."""
        self._coordinator = coordinator
        self._growth_type = growth_type
        growth_set = coordinator.get_growth_set(growth_type)

        self._attr_unique_id = f"{coordinator.member_id}_{growth_type}_input"
        self._attr_translation_placeholders = {"growth_name": growth_set.name}
        self._attr_native_unit_of_measurement = growth_set.unit
        self._attr_device_info = coordinator.get_device_info()
        self._attr_icon = "mdi:human-male-height"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        growth_set = self._coordinator.get_growth_set(self._growth_type)
        return growth_set.current_value if growth_set else None

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        self._coordinator.set_growth_value(self._growth_type, value)
        self.async_write_ha_state()
