"""Data coordinator for Ha Health Record integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ACTIVITY_NAME,
    CONF_ACTIVITY_SETS,
    CONF_ACTIVITY_TYPE,
    CONF_ACTIVITY_UNIT,
    CONF_GROWTH_NAME,
    CONF_GROWTH_SETS,
    CONF_GROWTH_TYPE,
    CONF_GROWTH_UNIT,
    CONF_MEMBER_ID,
    CONF_MEMBER_NAME,
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)


def signal_activity_updated(member_id: str, activity_type: str) -> str:
    """Return signal name for activity update."""
    return f"{DOMAIN}_{member_id}_{activity_type}_updated"


def signal_growth_updated(member_id: str, growth_type: str) -> str:
    """Return signal name for growth update."""
    return f"{DOMAIN}_{member_id}_{growth_type}_updated"


@dataclass
class ActivityRecord:
    """Represents an activity record."""

    amount: float | None = None
    note: str = ""
    timestamp: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "amount": self.amount,
            "note": self.note,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActivityRecord:
        """Create from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = dt_util.parse_datetime(data["timestamp"])
        return cls(
            amount=data.get("amount"),
            note=data.get("note", ""),
            timestamp=timestamp,
        )


@dataclass
class GrowthRecord:
    """Represents a growth record."""

    value: float | None = None
    note: str = ""
    timestamp: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "value": self.value,
            "note": self.note,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GrowthRecord:
        """Create from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = dt_util.parse_datetime(data["timestamp"])
        return cls(
            value=data.get("value"),
            note=data.get("note", ""),
            timestamp=timestamp,
        )


@dataclass
class ActivitySet:
    """Represents an activity set configuration."""

    type_id: str
    name: str
    unit: str
    current_amount: float | None = None
    current_note: str = ""
    last_record: ActivityRecord = field(default_factory=ActivityRecord)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "current_amount": self.current_amount,
            "current_note": self.current_note,
            "last_record": self.last_record.to_dict(),
        }

    def load_from_dict(self, data: dict[str, Any]) -> None:
        """Load state from dictionary."""
        self.current_amount = data.get("current_amount")
        self.current_note = data.get("current_note", "")
        if data.get("last_record"):
            self.last_record = ActivityRecord.from_dict(data["last_record"])


@dataclass
class GrowthSet:
    """Represents a growth set configuration."""

    type_id: str
    name: str
    unit: str
    current_value: float | None = None
    current_note: str = ""
    last_record: GrowthRecord = field(default_factory=GrowthRecord)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "current_value": self.current_value,
            "current_note": self.current_note,
            "last_record": self.last_record.to_dict(),
        }

    def load_from_dict(self, data: dict[str, Any]) -> None:
        """Load state from dictionary."""
        self.current_value = data.get("current_value")
        self.current_note = data.get("current_note", "")
        if data.get("last_record"):
            self.last_record = GrowthRecord.from_dict(data["last_record"])


class HealthRecordCoordinator:
    """Coordinator for managing health record data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry

        # Records history storage
        self.activity_records: list[dict[str, Any]] = []
        self.growth_records: list[dict[str, Any]] = []

        # Member info
        self.member_id: str = entry.data[CONF_MEMBER_ID]
        self.member_name: str = entry.data[CONF_MEMBER_NAME]

        # Storage - unique per member
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{STORAGE_KEY}_{self.member_id}"
        )

        # Activity sets
        self.activity_sets: dict[str, ActivitySet] = {}
        for activity_data in entry.options.get(CONF_ACTIVITY_SETS, []):
            type_id = activity_data[CONF_ACTIVITY_TYPE]
            self.activity_sets[type_id] = ActivitySet(
                type_id=type_id,
                name=activity_data[CONF_ACTIVITY_NAME],
                unit=activity_data[CONF_ACTIVITY_UNIT],
            )

        # Growth sets
        self.growth_sets: dict[str, GrowthSet] = {}
        for growth_data in entry.options.get(CONF_GROWTH_SETS, []):
            type_id = growth_data[CONF_GROWTH_TYPE]
            self.growth_sets[type_id] = GrowthSet(
                type_id=type_id,
                name=growth_data[CONF_GROWTH_NAME],
                unit=growth_data[CONF_GROWTH_UNIT],
            )

    async def async_load(self) -> None:
        """Load data from storage."""
        data = await self._store.async_load()
        if data is None:
            _LOGGER.debug("No stored data for member %s", self.member_id)
            return

        # Load activity set states
        activities_data = data.get("activity_sets", {})
        for type_id, activity_set in self.activity_sets.items():
            if type_id in activities_data:
                activity_set.load_from_dict(activities_data[type_id])

        # Load growth set states
        growth_data = data.get("growth_sets", {})
        for type_id, growth_set in self.growth_sets.items():
            if type_id in growth_data:
                growth_set.load_from_dict(growth_data[type_id])

        # Load records history
        self.activity_records = data.get("activity_records", [])
        self.growth_records = data.get("growth_records", [])

        _LOGGER.debug(
            "Loaded health record data for member %s: %d activities, %d growth sets, %d activity records, %d growth records",
            self.member_id,
            len(self.activity_sets),
            len(self.growth_sets),
            len(self.activity_records),
            len(self.growth_records),
        )

    async def _async_save(self) -> None:
        """Save data to storage."""
        data = {
            "activity_sets": {
                type_id: activity_set.to_dict()
                for type_id, activity_set in self.activity_sets.items()
            },
            "growth_sets": {
                type_id: growth_set.to_dict()
                for type_id, growth_set in self.growth_sets.items()
            },
            "activity_records": self.activity_records,
            "growth_records": self.growth_records,
        }
        await self._store.async_save(data)
        _LOGGER.debug("Saved health record data for member %s", self.member_id)

    def get_device_info(self) -> DeviceInfo:
        """Return device info for this member."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.member_id)},
            name=self.member_name,
            manufacturer="Ha Health Record",
            model="Family Member",
        )

    def set_activity_amount(self, activity_type: str, amount: float | None) -> None:
        """Set the current amount for an activity."""
        if activity_type in self.activity_sets:
            self.activity_sets[activity_type].current_amount = amount

    def set_activity_note(self, activity_type: str, note: str) -> None:
        """Set the current note for an activity."""
        if activity_type in self.activity_sets:
            self.activity_sets[activity_type].current_note = note

    async def async_log_activity(self, activity_type: str) -> ActivityRecord | None:
        """Log an activity and return the record."""
        if activity_type not in self.activity_sets:
            return None

        activity_set = self.activity_sets[activity_type]
        record = ActivityRecord(
            amount=activity_set.current_amount,
            note=activity_set.current_note,
            timestamp=dt_util.now(),
        )
        activity_set.last_record = record

        # Save to storage
        await self._async_save()

        # Notify sensor to update
        async_dispatcher_send(
            self.hass,
            signal_activity_updated(self.member_id, activity_type),
        )

        return record

    @callback
    def log_activity(self, activity_type: str, timestamp: datetime | None = None) -> ActivityRecord | None:
        """Log an activity and return the record (sync wrapper)."""
        if activity_type not in self.activity_sets:
            return None

        activity_set = self.activity_sets[activity_type]
        record_timestamp = timestamp or dt_util.now()
        record = ActivityRecord(
            amount=activity_set.current_amount,
            note=activity_set.current_note,
            timestamp=record_timestamp,
        )
        activity_set.last_record = record

        # Add to records history
        self.activity_records.append({
            "activity_type": activity_type,
            "activity_name": activity_set.name,
            "amount": activity_set.current_amount,
            "unit": activity_set.unit,
            "note": activity_set.current_note,
            "timestamp": record_timestamp.isoformat(),
        })

        # Schedule save
        self.hass.async_create_task(self._async_save())

        # Notify sensor to update
        async_dispatcher_send(
            self.hass,
            signal_activity_updated(self.member_id, activity_type),
        )

        return record

    async def async_set_growth_value(
        self, growth_type: str, value: float | None
    ) -> GrowthRecord | None:
        """Set the value for a growth measurement and return the record."""
        if growth_type not in self.growth_sets:
            return None

        growth_set = self.growth_sets[growth_type]
        growth_set.current_value = value
        record = GrowthRecord(
            value=value,
            timestamp=dt_util.now(),
        )
        growth_set.last_record = record

        # Save to storage
        await self._async_save()

        # Notify sensor to update
        async_dispatcher_send(
            self.hass,
            signal_growth_updated(self.member_id, growth_type),
        )

        return record

    @callback
    def set_growth_value(self, growth_type: str, value: float | None, note: str = "", timestamp: datetime | None = None) -> GrowthRecord | None:
        """Set the value for a growth measurement and return the record (sync wrapper)."""
        if growth_type not in self.growth_sets:
            return None

        growth_set = self.growth_sets[growth_type]
        growth_set.current_value = value
        growth_set.current_note = note
        record_timestamp = timestamp or dt_util.now()
        record = GrowthRecord(
            value=value,
            note=note,
            timestamp=record_timestamp,
        )
        growth_set.last_record = record

        # Add to records history
        self.growth_records.append({
            "growth_type": growth_type,
            "growth_name": growth_set.name,
            "value": value,
            "unit": growth_set.unit,
            "note": note,
            "timestamp": record_timestamp.isoformat(),
        })

        # Schedule save
        self.hass.async_create_task(self._async_save())

        # Notify sensor to update
        async_dispatcher_send(
            self.hass,
            signal_growth_updated(self.member_id, growth_type),
        )

        return record

    def get_activity_set(self, activity_type: str) -> ActivitySet | None:
        """Get an activity set by type."""
        return self.activity_sets.get(activity_type)

    def get_growth_set(self, growth_type: str) -> GrowthSet | None:
        """Get a growth set by type."""
        return self.growth_sets.get(growth_type)

    def get_records_in_range(self, start_time: datetime, end_time: datetime) -> list[dict[str, Any]]:
        """Get all records in a time range."""
        records = []

        # Get activity records
        for record in self.activity_records:
            try:
                record_time = dt_util.parse_datetime(record["timestamp"])
                if record_time and start_time <= record_time <= end_time:
                    records.append({
                        "member_id": self.member_id,
                        "member_name": self.member_name,
                        "type": "activity",
                        "activity_type": record["activity_type"],
                        "activity_name": record["activity_name"],
                        "amount": record["amount"],
                        "unit": record["unit"],
                        "note": record.get("note", ""),
                        "timestamp": record["timestamp"],
                    })
            except (ValueError, TypeError):
                continue

        # Get growth records
        for record in self.growth_records:
            try:
                record_time = dt_util.parse_datetime(record["timestamp"])
                if record_time and start_time <= record_time <= end_time:
                    records.append({
                        "member_id": self.member_id,
                        "member_name": self.member_name,
                        "type": "growth",
                        "growth_type": record["growth_type"],
                        "growth_name": record["growth_name"],
                        "value": record["value"],
                        "unit": record["unit"],
                        "note": record.get("note", ""),
                        "timestamp": record["timestamp"],
                    })
            except (ValueError, TypeError):
                continue

        return records

    def delete_record(self, record_type: str, type_id: str, timestamp: str) -> bool:
        """Delete a record by type and timestamp."""
        if record_type == "activity":
            for i, record in enumerate(self.activity_records):
                if record["activity_type"] == type_id and record["timestamp"] == timestamp:
                    del self.activity_records[i]
                    self.hass.async_create_task(self._async_save())
                    return True
        elif record_type == "growth":
            for i, record in enumerate(self.growth_records):
                if record["growth_type"] == type_id and record["timestamp"] == timestamp:
                    del self.growth_records[i]
                    self.hass.async_create_task(self._async_save())
                    return True
        return False

    def update_record(self, record_type: str, type_id: str, timestamp: str, amount: float | None = None, note: str | None = None, new_timestamp: str | None = None) -> bool:
        """Update a record by type and timestamp."""
        if record_type == "activity":
            for record in self.activity_records:
                if record["activity_type"] == type_id and record["timestamp"] == timestamp:
                    if amount is not None:
                        record["amount"] = amount
                    if note is not None:
                        record["note"] = note
                    if new_timestamp is not None:
                        record["timestamp"] = new_timestamp
                    self.hass.async_create_task(self._async_save())
                    return True
        elif record_type == "growth":
            for record in self.growth_records:
                if record["growth_type"] == type_id and record["timestamp"] == timestamp:
                    if amount is not None:
                        record["value"] = amount
                    if note is not None:
                        record["note"] = note
                    if new_timestamp is not None:
                        record["timestamp"] = new_timestamp
                    self.hass.async_create_task(self._async_save())
                    return True
        return False
