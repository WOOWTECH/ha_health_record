"""Config flow for Ha Health Record integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlowWithConfigEntry,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

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
    CUSTOM_TYPE,
    DEFAULT_ACTIVITY_TYPES,
    DEFAULT_GROWTH_TYPES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def _sanitize_id(name: str) -> str:
    """Sanitize a name to create a valid ID."""
    return re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_"))


class HaHealthRecordConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ha Health Record."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - add a family member."""
        errors: dict[str, str] = {}

        if user_input is not None:
            member_id = user_input[CONF_MEMBER_ID]

            # Check if member already exists
            await self.async_set_unique_id(member_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_MEMBER_NAME],
                data={
                    CONF_MEMBER_ID: member_id,
                    CONF_MEMBER_NAME: user_input[CONF_MEMBER_NAME],
                },
                options={
                    CONF_ACTIVITY_SETS: [],
                    CONF_GROWTH_SETS: [],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MEMBER_NAME): str,
                    vol.Required(CONF_MEMBER_ID): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithConfigEntry:
        """Get the options flow for this handler."""
        return HaHealthRecordOptionsFlow(config_entry)


class HaHealthRecordOptionsFlow(OptionsFlowWithConfigEntry):
    """Handle options flow for Ha Health Record."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        super().__init__(config_entry)
        self._activity_sets: list[dict[str, Any]] = list(
            config_entry.options.get(CONF_ACTIVITY_SETS, [])
        )
        self._growth_sets: list[dict[str, Any]] = list(
            config_entry.options.get(CONF_GROWTH_SETS, [])
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - main menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["add_activity", "add_growth", "manage_sets"],
        )

    async def async_step_add_activity(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a new activity set."""
        errors: dict[str, str] = {}

        if user_input is not None:
            activity_type = user_input.get(CONF_ACTIVITY_TYPE)

            if activity_type == CUSTOM_TYPE:
                # Custom type - use provided name and unit
                activity_name = user_input.get(CONF_ACTIVITY_NAME, "").strip()
                activity_unit = user_input.get(CONF_ACTIVITY_UNIT, "").strip()

                if not activity_name:
                    errors[CONF_ACTIVITY_NAME] = "required_name"
                else:
                    activity_id = _sanitize_id(activity_name)
                    if not activity_id:
                        errors[CONF_ACTIVITY_NAME] = "invalid_name"
            else:
                # Predefined type
                preset = next(
                    (t for t in DEFAULT_ACTIVITY_TYPES if t["id"] == activity_type),
                    None,
                )
                if preset:
                    activity_id = preset["id"]
                    activity_name = preset["name"]
                    activity_unit = preset["unit"]
                else:
                    errors["base"] = "invalid_type"

            if not errors:
                # Check for duplicates
                if any(s[CONF_ACTIVITY_TYPE] == activity_id for s in self._activity_sets):
                    errors["base"] = "duplicate_set"
                else:
                    self._activity_sets.append(
                        {
                            CONF_ACTIVITY_TYPE: activity_id,
                            CONF_ACTIVITY_NAME: activity_name,
                            CONF_ACTIVITY_UNIT: activity_unit,
                        }
                    )
                    return await self._save_options()

        # Build activity type options
        activity_options = [
            selector.SelectOptionDict(value=t["id"], label=f"{t['name']} ({t['unit']})")
            for t in DEFAULT_ACTIVITY_TYPES
        ]
        activity_options.append(
            selector.SelectOptionDict(value=CUSTOM_TYPE, label="Custom...")
        )

        return self.async_show_form(
            step_id="add_activity",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ACTIVITY_TYPE): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=activity_options,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(CONF_ACTIVITY_NAME): str,
                    vol.Optional(CONF_ACTIVITY_UNIT): str,
                }
            ),
            errors=errors,
        )

    async def async_step_add_growth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a new growth set."""
        errors: dict[str, str] = {}

        if user_input is not None:
            growth_type = user_input.get(CONF_GROWTH_TYPE)

            if growth_type == CUSTOM_TYPE:
                # Custom type
                growth_name = user_input.get(CONF_GROWTH_NAME, "").strip()
                growth_unit = user_input.get(CONF_GROWTH_UNIT, "").strip()

                if not growth_name:
                    errors[CONF_GROWTH_NAME] = "required_name"
                else:
                    growth_id = _sanitize_id(growth_name)
                    if not growth_id:
                        errors[CONF_GROWTH_NAME] = "invalid_name"
            else:
                # Predefined type
                preset = next(
                    (t for t in DEFAULT_GROWTH_TYPES if t["id"] == growth_type),
                    None,
                )
                if preset:
                    growth_id = preset["id"]
                    growth_name = preset["name"]
                    growth_unit = preset["unit"]
                else:
                    errors["base"] = "invalid_type"

            if not errors:
                # Check for duplicates
                if any(s[CONF_GROWTH_TYPE] == growth_id for s in self._growth_sets):
                    errors["base"] = "duplicate_set"
                else:
                    self._growth_sets.append(
                        {
                            CONF_GROWTH_TYPE: growth_id,
                            CONF_GROWTH_NAME: growth_name,
                            CONF_GROWTH_UNIT: growth_unit,
                        }
                    )
                    return await self._save_options()

        # Build growth type options
        growth_options = [
            selector.SelectOptionDict(value=t["id"], label=f"{t['name']} ({t['unit']})")
            for t in DEFAULT_GROWTH_TYPES
        ]
        growth_options.append(
            selector.SelectOptionDict(value=CUSTOM_TYPE, label="Custom...")
        )

        return self.async_show_form(
            step_id="add_growth",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_GROWTH_TYPE): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=growth_options,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(CONF_GROWTH_NAME): str,
                    vol.Optional(CONF_GROWTH_UNIT): str,
                }
            ),
            errors=errors,
        )

    async def async_step_manage_sets(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage existing sets - show list and allow deletion."""
        if user_input is not None:
            # Process deletions
            sets_to_delete = user_input.get("delete_sets", [])
            for set_id in sets_to_delete:
                set_type, set_name = set_id.split(":", 1)
                if set_type == "activity":
                    self._activity_sets = [
                        s for s in self._activity_sets
                        if s[CONF_ACTIVITY_TYPE] != set_name
                    ]
                elif set_type == "growth":
                    self._growth_sets = [
                        s for s in self._growth_sets
                        if s[CONF_GROWTH_TYPE] != set_name
                    ]

            return await self._save_options()

        # Build list of all sets
        all_sets = []
        for activity in self._activity_sets:
            all_sets.append(
                selector.SelectOptionDict(
                    value=f"activity:{activity[CONF_ACTIVITY_TYPE]}",
                    label=f"[Activity] {activity[CONF_ACTIVITY_NAME]} ({activity[CONF_ACTIVITY_UNIT]})",
                )
            )
        for growth in self._growth_sets:
            all_sets.append(
                selector.SelectOptionDict(
                    value=f"growth:{growth[CONF_GROWTH_TYPE]}",
                    label=f"[Growth] {growth[CONF_GROWTH_NAME]} ({growth[CONF_GROWTH_UNIT]})",
                )
            )

        if not all_sets:
            return self.async_abort(reason="no_sets")

        return self.async_show_form(
            step_id="manage_sets",
            data_schema=vol.Schema(
                {
                    vol.Optional("delete_sets"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=all_sets,
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
            description_placeholders={
                "count_activity": str(len(self._activity_sets)),
                "count_growth": str(len(self._growth_sets)),
            },
        )

    async def _save_options(self) -> FlowResult:
        """Save the options and create entry."""
        return self.async_create_entry(
            title="",
            data={
                CONF_ACTIVITY_SETS: self._activity_sets,
                CONF_GROWTH_SETS: self._growth_sets,
            },
        )
