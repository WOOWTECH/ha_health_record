"""Sensor platform for Ha Health Record integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import (
    HealthRecordCoordinator,
    signal_activity_updated,
    signal_growth_updated,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    coordinator: HealthRecordCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    # Create record sensor for each activity set
    for activity_type in coordinator.activity_sets:
        entities.append(
            ActivityRecordSensor(
                coordinator=coordinator,
                activity_type=activity_type,
            )
        )

    # Create record sensor for each growth set
    for growth_type in coordinator.growth_sets:
        entities.append(
            GrowthRecordSensor(
                coordinator=coordinator,
                growth_type=growth_type,
            )
        )

    async_add_entities(entities)


class ActivityRecordSensor(SensorEntity):
    """Sensor showing the last activity record."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "activity_record"

    def __init__(
        self,
        coordinator: HealthRecordCoordinator,
        activity_type: str,
    ) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._activity_type = activity_type
        activity_set = coordinator.get_activity_set(activity_type)

        self._attr_unique_id = f"{coordinator.member_id}_{activity_type}_record"
        self._attr_translation_placeholders = {"activity_name": activity_set.name}
        self._attr_native_unit_of_measurement = activity_set.unit
        self._attr_device_info = coordinator.get_device_info()
        self._attr_icon = "mdi:clipboard-text-clock"

    async def async_added_to_hass(self) -> None:
        """Subscribe to dispatcher signals when added to hass."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_activity_updated(
                    self._coordinator.member_id, self._activity_type
                ),
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle update signal."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> float | None:
        """Return the last recorded amount."""
        activity_set = self._coordinator.get_activity_set(self._activity_type)
        if activity_set and activity_set.last_record:
            return activity_set.last_record.amount
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        activity_set = self._coordinator.get_activity_set(self._activity_type)
        if not activity_set or not activity_set.last_record:
            return {}

        record = activity_set.last_record
        attrs = {
            "note": record.note,
            "activity_name": activity_set.name,
            "unit": activity_set.unit,
        }
        if record.timestamp:
            attrs["timestamp"] = record.timestamp.isoformat()

        return attrs


class GrowthRecordSensor(SensorEntity):
    """Sensor showing the current growth value."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "growth_record"

    def __init__(
        self,
        coordinator: HealthRecordCoordinator,
        growth_type: str,
    ) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._growth_type = growth_type
        growth_set = coordinator.get_growth_set(growth_type)

        self._attr_unique_id = f"{coordinator.member_id}_{growth_type}_record"
        self._attr_translation_placeholders = {"growth_name": growth_set.name}
        self._attr_native_unit_of_measurement = growth_set.unit
        self._attr_device_info = coordinator.get_device_info()
        self._attr_icon = "mdi:chart-line"

    async def async_added_to_hass(self) -> None:
        """Subscribe to dispatcher signals when added to hass."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_growth_updated(self._coordinator.member_id, self._growth_type),
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle update signal."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> float | None:
        """Return the current growth value."""
        growth_set = self._coordinator.get_growth_set(self._growth_type)
        if growth_set and growth_set.last_record:
            return growth_set.last_record.value
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        growth_set = self._coordinator.get_growth_set(self._growth_type)
        if not growth_set or not growth_set.last_record:
            return {}

        record = growth_set.last_record
        attrs = {
            "growth_name": growth_set.name,
            "unit": growth_set.unit,
        }
        if record.timestamp:
            attrs["timestamp"] = record.timestamp.isoformat()

        return attrs
