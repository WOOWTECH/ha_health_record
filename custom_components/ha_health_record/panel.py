"""Panel registration and WebSocket API for Ha Health Record."""
from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api, frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PANEL_TITLE = "Health Record"
PANEL_ICON = "mdi:heart-pulse"
PANEL_URL_PATH = "ha-health-record"  # URL path for the panel in sidebar
PANEL_COMPONENT_NAME = "ha-health-record-panel"  # Web component name
FRONTEND_SCRIPT_PATH = f"/{DOMAIN}/frontend"  # Static path for JS files


async def async_setup_panel(hass: HomeAssistant) -> None:
    """Set up the Ha Health Record panel."""
    # Register WebSocket commands
    websocket_api.async_register_command(hass, ws_get_members)
    websocket_api.async_register_command(hass, ws_get_records)
    websocket_api.async_register_command(hass, ws_log_activity)
    websocket_api.async_register_command(hass, ws_update_growth)
    # Record management APIs
    websocket_api.async_register_command(hass, ws_update_record)
    websocket_api.async_register_command(hass, ws_delete_record)
    # Activity type management APIs
    websocket_api.async_register_command(hass, ws_add_activity_type)
    websocket_api.async_register_command(hass, ws_update_activity_type)
    websocket_api.async_register_command(hass, ws_delete_activity_type)
    # Growth type management APIs
    websocket_api.async_register_command(hass, ws_add_growth_type)
    websocket_api.async_register_command(hass, ws_update_growth_type)
    websocket_api.async_register_command(hass, ws_delete_growth_type)
    # Member management APIs
    websocket_api.async_register_command(hass, ws_add_member)
    websocket_api.async_register_command(hass, ws_update_member)
    websocket_api.async_register_command(hass, ws_delete_member)

    # Register static path for frontend files
    frontend_path = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths([
        StaticPathConfig(FRONTEND_SCRIPT_PATH, str(frontend_path), cache_headers=False)
    ])

    # Register the panel using panel_custom
    # Add cache-busting timestamp to force browser to reload the JS file
    cache_buster = int(time.time())
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_COMPONENT_NAME,
        frontend_url_path=PANEL_URL_PATH,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        module_url=f"{FRONTEND_SCRIPT_PATH}/ha-health-record-panel.js?v={cache_buster}",
        require_admin=False,
        config={},
    )

    _LOGGER.info("Registered Ha Health Record panel")


async def async_unload_panel(hass: HomeAssistant) -> None:
    """Unload the Ha Health Record panel."""
    if PANEL_URL_PATH in hass.data.get(frontend.DATA_PANELS, {}):
        frontend.async_remove_panel(hass, PANEL_URL_PATH)
        _LOGGER.info("Unregistered Ha Health Record panel")


def _get_coordinators(hass: HomeAssistant) -> list:
    """Get all coordinators, filtering out non-coordinator entries."""
    coordinators = []
    for key, value in hass.data.get(DOMAIN, {}).items():
        # Skip internal keys like _panel_setup
        if isinstance(key, str) and key.startswith("_"):
            continue
        # Check if it's a coordinator (has member_id attribute)
        if hasattr(value, "member_id"):
            coordinators.append(value)
    return coordinators


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/get_members",
    }
)
@callback
def ws_get_members(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle get_members WebSocket command."""
    members = []

    for coordinator in _get_coordinators(hass):
        member = {
            "id": coordinator.member_id,
            "name": coordinator.member_name,
            "activity_sets": [
                {
                    "type": s.type_id,
                    "name": s.name,
                    "unit": s.unit,
                    "current_amount": s.current_amount,
                    "last_record": {
                        "amount": s.last_record.amount,
                        "note": s.last_record.note,
                        "timestamp": s.last_record.timestamp.isoformat() if s.last_record.timestamp else None,
                    } if s.last_record else None,
                }
                for s in coordinator.activity_sets.values()
            ],
            "growth_sets": [
                {
                    "type": s.type_id,
                    "name": s.name,
                    "unit": s.unit,
                    "current_value": s.current_value,
                    "last_record": {
                        "value": s.last_record.value,
                        "timestamp": s.last_record.timestamp.isoformat() if s.last_record.timestamp else None,
                    } if s.last_record else None,
                }
                for s in coordinator.growth_sets.values()
            ],
        }
        members.append(member)

    connection.send_result(msg["id"], {"members": members})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/get_records",
        vol.Required("start_time"): str,
        vol.Required("end_time"): str,
    }
)
@callback
def ws_get_records(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle get_records WebSocket command."""
    try:
        start_time = datetime.fromisoformat(msg["start_time"].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(msg["end_time"].replace('Z', '+00:00'))
    except ValueError:
        connection.send_error(msg["id"], "invalid_date", "Invalid date format")
        return

    records = []

    # Get records from all coordinators
    for coordinator in _get_coordinators(hass):
        coordinator_records = coordinator.get_records_in_range(start_time, end_time)
        records.extend(coordinator_records)

    # Sort by timestamp descending
    records.sort(key=lambda x: x["timestamp"], reverse=True)

    connection.send_result(msg["id"], {"records": records})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/log_activity",
        vol.Required("member_id"): str,
        vol.Required("activity_type"): str,
        vol.Required("amount"): vol.Coerce(float),
        vol.Optional("note", default=""): str,
        vol.Optional("timestamp"): str,
    }
)
@callback
def ws_log_activity(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle log_activity WebSocket command."""
    member_id = msg["member_id"]
    activity_type = msg["activity_type"]
    amount = msg["amount"]
    note = msg.get("note", "")
    timestamp_str = msg.get("timestamp")

    # Find the coordinator
    coordinator = None
    for coord in _get_coordinators(hass):
        if coord.member_id == member_id:
            coordinator = coord
            break

    if coordinator is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    if activity_type not in coordinator.activity_sets:
        connection.send_error(msg["id"], "activity_not_found", f"Activity {activity_type} not found")
        return

    # Parse optional timestamp
    custom_timestamp = None
    if timestamp_str:
        try:
            custom_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            connection.send_error(msg["id"], "invalid_timestamp", "Invalid timestamp format")
            return

    # Set the values and log
    coordinator.set_activity_amount(activity_type, amount)
    coordinator.set_activity_note(activity_type, note)
    record = coordinator.log_activity(activity_type, timestamp=custom_timestamp)

    if record is None:
        connection.send_error(msg["id"], "log_failed", "Failed to log activity")
        return

    # Fire event
    activity_set = coordinator.get_activity_set(activity_type)
    hass.bus.async_fire(
        f"{DOMAIN}_activity_logged",
        {
            "member_id": coordinator.member_id,
            "member_name": coordinator.member_name,
            "activity_type": activity_type,
            "activity_name": activity_set.name,
            "amount": record.amount,
            "unit": activity_set.unit,
            "note": record.note,
            "timestamp": record.timestamp.isoformat() if record.timestamp else None,
        },
    )

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/update_growth",
        vol.Required("member_id"): str,
        vol.Required("growth_type"): str,
        vol.Required("value"): vol.Coerce(float),
        vol.Optional("note", default=""): str,
        vol.Optional("timestamp"): str,
    }
)
@callback
def ws_update_growth(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update_growth WebSocket command."""
    member_id = msg["member_id"]
    growth_type = msg["growth_type"]
    value = msg["value"]
    note = msg.get("note", "")
    timestamp_str = msg.get("timestamp")

    # Find the coordinator
    coordinator = None
    for coord in _get_coordinators(hass):
        if coord.member_id == member_id:
            coordinator = coord
            break

    if coordinator is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    if growth_type not in coordinator.growth_sets:
        connection.send_error(msg["id"], "growth_not_found", f"Growth {growth_type} not found")
        return

    # Parse optional timestamp
    custom_timestamp = None
    if timestamp_str:
        try:
            custom_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            connection.send_error(msg["id"], "invalid_timestamp", "Invalid timestamp format")
            return

    # Set the value
    record = coordinator.set_growth_value(growth_type, value, note=note, timestamp=custom_timestamp)

    if record is None:
        connection.send_error(msg["id"], "update_failed", "Failed to update growth")
        return

    # Fire event for growth update
    growth_set = coordinator.get_growth_set(growth_type)
    hass.bus.async_fire(
        f"{DOMAIN}_growth_updated",
        {
            "member_id": coordinator.member_id,
            "member_name": coordinator.member_name,
            "growth_type": growth_type,
            "growth_name": growth_set.name,
            "value": record.value,
            "unit": growth_set.unit,
            "note": record.note,
            "timestamp": record.timestamp.isoformat() if record.timestamp else None,
        },
    )

    connection.send_result(msg["id"], {"success": True})


# ============================================================================
# Record Management APIs
# ============================================================================

@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/update_record",
        vol.Required("member_id"): str,
        vol.Required("record_type"): str,  # "activity" or "growth"
        vol.Required("type_id"): str,  # activity_type or growth_type
        vol.Required("timestamp"): str,  # ISO format to identify the record
        vol.Optional("amount"): vol.Coerce(float),
        vol.Optional("value"): vol.Coerce(float),
        vol.Optional("note"): str,
        vol.Optional("new_timestamp"): str,  # New timestamp if editing time
    }
)
@callback
def ws_update_record(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update_record WebSocket command."""
    member_id = msg["member_id"]
    record_type = msg["record_type"]
    type_id = msg["type_id"]
    timestamp = msg["timestamp"]

    # Find the coordinator
    coordinator = None
    for coord in _get_coordinators(hass):
        if coord.member_id == member_id:
            coordinator = coord
            break

    if coordinator is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    # Get the update values
    amount = msg.get("amount") if record_type == "activity" else msg.get("value")
    note = msg.get("note")
    new_timestamp = msg.get("new_timestamp")

    if coordinator.update_record(record_type, type_id, timestamp, amount=amount, note=note, new_timestamp=new_timestamp):
        connection.send_result(msg["id"], {"success": True})
    else:
        connection.send_error(msg["id"], "record_not_found", "Record not found")


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/delete_record",
        vol.Required("member_id"): str,
        vol.Required("record_type"): str,
        vol.Required("type_id"): str,
        vol.Required("timestamp"): str,
    }
)
@callback
def ws_delete_record(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle delete_record WebSocket command."""
    member_id = msg["member_id"]
    record_type = msg["record_type"]
    type_id = msg["type_id"]
    timestamp = msg["timestamp"]

    # Find the coordinator
    coordinator = None
    for coord in _get_coordinators(hass):
        if coord.member_id == member_id:
            coordinator = coord
            break

    if coordinator is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    if coordinator.delete_record(record_type, type_id, timestamp):
        connection.send_result(msg["id"], {"success": True})
    else:
        connection.send_error(msg["id"], "record_not_found", "Record not found")


# ============================================================================
# Activity Type Management APIs
# ============================================================================

@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/add_activity_type",
        vol.Required("member_id"): str,
        vol.Required("name"): str,
        vol.Required("unit"): str,
        vol.Optional("default_amount", default=0): vol.Coerce(float),
    }
)
@websocket_api.async_response
async def ws_add_activity_type(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle add_activity_type WebSocket command."""
    member_id = msg["member_id"]
    name = msg["name"]
    unit = msg["unit"]
    default_amount = msg.get("default_amount", 0)

    # Generate type_id from name (sanitize)
    type_id = name.lower().replace(" ", "_").replace("-", "_")
    type_id = "".join(c for c in type_id if c.isalnum() or c == "_")

    # Find the config entry for this member
    entry = None
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.data.get("member_id") == member_id:
            entry = e
            break

    if entry is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    # Get current activity sets
    current_options = dict(entry.options)
    activity_sets = list(current_options.get("activity_sets", []))

    # Check if type already exists
    for s in activity_sets:
        if s.get("activity_type") == type_id:
            connection.send_error(msg["id"], "type_exists", f"Activity type {type_id} already exists")
            return

    # Add new type
    activity_sets.append({
        "activity_type": type_id,
        "activity_name": name,
        "activity_unit": unit,
        "default_amount": default_amount,
    })

    current_options["activity_sets"] = activity_sets

    # Update config entry
    hass.config_entries.async_update_entry(entry, options=current_options)

    # Reload entry to create new entities
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True, "type_id": type_id})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/update_activity_type",
        vol.Required("member_id"): str,
        vol.Required("type_id"): str,
        vol.Required("name"): str,
        vol.Required("unit"): str,
        vol.Optional("default_amount"): vol.Coerce(float),
    }
)
@websocket_api.async_response
async def ws_update_activity_type(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update_activity_type WebSocket command."""
    member_id = msg["member_id"]
    type_id = msg["type_id"]
    name = msg["name"]
    unit = msg["unit"]
    default_amount = msg.get("default_amount")

    # Find the config entry for this member
    entry = None
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.data.get("member_id") == member_id:
            entry = e
            break

    if entry is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    # Get current activity sets
    current_options = dict(entry.options)
    activity_sets = list(current_options.get("activity_sets", []))

    # Find and update the type
    found = False
    for s in activity_sets:
        if s.get("activity_type") == type_id:
            s["activity_name"] = name
            s["activity_unit"] = unit
            if default_amount is not None:
                s["default_amount"] = default_amount
            found = True
            break

    if not found:
        connection.send_error(msg["id"], "type_not_found", f"Activity type {type_id} not found")
        return

    current_options["activity_sets"] = activity_sets

    # Update config entry
    hass.config_entries.async_update_entry(entry, options=current_options)

    # Reload entry to update entities
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/delete_activity_type",
        vol.Required("member_id"): str,
        vol.Required("type_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_activity_type(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle delete_activity_type WebSocket command."""
    member_id = msg["member_id"]
    type_id = msg["type_id"]

    # Find the config entry for this member
    entry = None
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.data.get("member_id") == member_id:
            entry = e
            break

    if entry is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    # Get current activity sets
    current_options = dict(entry.options)
    activity_sets = list(current_options.get("activity_sets", []))

    # Find and remove the type
    new_sets = [s for s in activity_sets if s.get("activity_type") != type_id]

    if len(new_sets) == len(activity_sets):
        connection.send_error(msg["id"], "type_not_found", f"Activity type {type_id} not found")
        return

    current_options["activity_sets"] = new_sets

    # Update config entry
    hass.config_entries.async_update_entry(entry, options=current_options)

    # Reload entry to remove entities
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True})


# ============================================================================
# Growth Type Management APIs
# ============================================================================

@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/add_growth_type",
        vol.Required("member_id"): str,
        vol.Required("name"): str,
        vol.Required("unit"): str,
        vol.Optional("default_value", default=0): vol.Coerce(float),
    }
)
@websocket_api.async_response
async def ws_add_growth_type(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle add_growth_type WebSocket command."""
    member_id = msg["member_id"]
    name = msg["name"]
    unit = msg["unit"]
    default_value = msg.get("default_value", 0)

    # Generate type_id from name (sanitize)
    type_id = name.lower().replace(" ", "_").replace("-", "_")
    type_id = "".join(c for c in type_id if c.isalnum() or c == "_")

    # Find the config entry for this member
    entry = None
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.data.get("member_id") == member_id:
            entry = e
            break

    if entry is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    # Get current growth sets
    current_options = dict(entry.options)
    growth_sets = list(current_options.get("growth_sets", []))

    # Check if type already exists
    for s in growth_sets:
        if s.get("growth_type") == type_id:
            connection.send_error(msg["id"], "type_exists", f"Growth type {type_id} already exists")
            return

    # Add new type
    growth_sets.append({
        "growth_type": type_id,
        "growth_name": name,
        "growth_unit": unit,
        "default_value": default_value,
    })

    current_options["growth_sets"] = growth_sets

    # Update config entry
    hass.config_entries.async_update_entry(entry, options=current_options)

    # Reload entry to create new entities
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True, "type_id": type_id})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/update_growth_type",
        vol.Required("member_id"): str,
        vol.Required("type_id"): str,
        vol.Required("name"): str,
        vol.Required("unit"): str,
        vol.Optional("default_value"): vol.Coerce(float),
    }
)
@websocket_api.async_response
async def ws_update_growth_type(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update_growth_type WebSocket command."""
    member_id = msg["member_id"]
    type_id = msg["type_id"]
    name = msg["name"]
    unit = msg["unit"]
    default_value = msg.get("default_value")

    # Find the config entry for this member
    entry = None
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.data.get("member_id") == member_id:
            entry = e
            break

    if entry is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    # Get current growth sets
    current_options = dict(entry.options)
    growth_sets = list(current_options.get("growth_sets", []))

    # Find and update the type
    found = False
    for s in growth_sets:
        if s.get("growth_type") == type_id:
            s["growth_name"] = name
            s["growth_unit"] = unit
            if default_value is not None:
                s["default_value"] = default_value
            found = True
            break

    if not found:
        connection.send_error(msg["id"], "type_not_found", f"Growth type {type_id} not found")
        return

    current_options["growth_sets"] = growth_sets

    # Update config entry
    hass.config_entries.async_update_entry(entry, options=current_options)

    # Reload entry to update entities
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/delete_growth_type",
        vol.Required("member_id"): str,
        vol.Required("type_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_growth_type(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle delete_growth_type WebSocket command."""
    member_id = msg["member_id"]
    type_id = msg["type_id"]

    # Find the config entry for this member
    entry = None
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.data.get("member_id") == member_id:
            entry = e
            break

    if entry is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    # Get current growth sets
    current_options = dict(entry.options)
    growth_sets = list(current_options.get("growth_sets", []))

    # Find and remove the type
    new_sets = [s for s in growth_sets if s.get("growth_type") != type_id]

    if len(new_sets) == len(growth_sets):
        connection.send_error(msg["id"], "type_not_found", f"Growth type {type_id} not found")
        return

    current_options["growth_sets"] = new_sets

    # Update config entry
    hass.config_entries.async_update_entry(entry, options=current_options)

    # Reload entry to remove entities
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True})


# ============================================================================
# Member (Person) Management APIs
# ============================================================================

@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/add_member",
        vol.Required("name"): str,
        vol.Optional("member_id"): str,
    }
)
@websocket_api.async_response
async def ws_add_member(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle add_member WebSocket command."""
    name = msg["name"]
    member_id = msg.get("member_id")

    # Generate member_id from name if not provided
    if not member_id:
        member_id = name.lower().replace(" ", "_").replace("-", "_")
        member_id = "".join(c for c in member_id if c.isalnum() or c == "_")

    # Check if member already exists
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.data.get("member_id") == member_id:
            connection.send_error(msg["id"], "member_exists", f"Member {member_id} already exists")
            return

    # Create new config entry via config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
        data={"member_name": name, "member_id": member_id},
    )

    if result.get("type") == "create_entry":
        connection.send_result(msg["id"], {
            "success": True,
            "member_id": member_id,
            "entry_id": result.get("result").entry_id if result.get("result") else None,
        })
    else:
        connection.send_error(msg["id"], "create_failed", "Failed to create member")


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/update_member",
        vol.Required("member_id"): str,
        vol.Required("name"): str,
    }
)
@websocket_api.async_response
async def ws_update_member(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update_member WebSocket command."""
    member_id = msg["member_id"]
    name = msg["name"]

    # Find the config entry for this member
    entry = None
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.data.get("member_id") == member_id:
            entry = e
            break

    if entry is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    # Update entry data (need to update both data and title)
    new_data = dict(entry.data)
    new_data["member_name"] = name

    hass.config_entries.async_update_entry(entry, data=new_data, title=name)

    # Reload to apply changes
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_health_record/delete_member",
        vol.Required("member_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_member(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle delete_member WebSocket command."""
    member_id = msg["member_id"]

    # Find the config entry for this member
    entry = None
    for e in hass.config_entries.async_entries(DOMAIN):
        if e.data.get("member_id") == member_id:
            entry = e
            break

    if entry is None:
        connection.send_error(msg["id"], "member_not_found", f"Member {member_id} not found")
        return

    # Remove the config entry
    await hass.config_entries.async_remove(entry.entry_id)

    connection.send_result(msg["id"], {"success": True})
