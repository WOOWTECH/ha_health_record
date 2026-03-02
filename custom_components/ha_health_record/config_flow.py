"""Config flow for Ha Health Record integration."""
from __future__ import annotations

import copy
import logging
import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_MEMBER_ID,
    CONF_MEMBER_NAME,
    CONF_RECORD_NAME,
    CONF_RECORD_SETS,
    CONF_RECORD_TYPE,
    CONF_RECORD_UNIT,
    CUSTOM_TYPE,
    DEFAULT_RECORD_TYPES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Label for the custom type option in dropdowns
CUSTOM_TYPE_LABEL = "Custom..."


def _sanitize_id(name: str) -> str:
    """Sanitize a name to create a valid ID."""
    return re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_"))


class HaHealthRecordConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ha Health Record."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step - add a family member."""
        errors: dict[str, str] = {}

        if user_input is not None:
            member_id = user_input.get(CONF_MEMBER_ID, "").strip()
            if not member_id:
                member_id = user_input[CONF_MEMBER_NAME]

            # Validate member_id produces a usable sanitized ID
            sanitized_id = _sanitize_id(member_id)
            if not sanitized_id:
                errors[CONF_MEMBER_ID] = "invalid_id"
            else:
                # Use the sanitized ID as the unique ID
                await self.async_set_unique_id(sanitized_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_MEMBER_NAME],
                    data={
                        CONF_MEMBER_ID: sanitized_id,
                        CONF_MEMBER_NAME: user_input[CONF_MEMBER_NAME],
                    },
                    options={
                        CONF_RECORD_SETS: [],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MEMBER_NAME): str,
                    vol.Optional(CONF_MEMBER_ID, default=""): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> HaHealthRecordOptionsFlow:
        """Get the options flow for this handler."""
        return HaHealthRecordOptionsFlow()


class HaHealthRecordOptionsFlow(OptionsFlow):
    """Handle options flow for Ha Health Record."""

    _record_sets: list[dict[str, Any]]

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options - main menu."""
        # Deep copy options to avoid mutating the live config entry data
        self._record_sets = copy.deepcopy(
            list(self.config_entry.options.get(CONF_RECORD_SETS, []))
        )
        return self.async_show_menu(
            step_id="init",
            menu_options=["add_record_type", "manage_sets"],
        )

    async def async_step_add_record_type(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add a new record type."""
        errors: dict[str, str] = {}

        if user_input is not None:
            record_type = user_input.get(CONF_RECORD_TYPE)

            if record_type == CUSTOM_TYPE:
                # Custom type - use provided name and unit
                record_name = user_input.get(CONF_RECORD_NAME, "").strip()
                record_unit = user_input.get(CONF_RECORD_UNIT, "").strip()

                if not record_name:
                    errors[CONF_RECORD_NAME] = "required_name"
                else:
                    record_id = _sanitize_id(record_name)
                    if not record_id:
                        errors[CONF_RECORD_NAME] = "invalid_name"
            else:
                # Predefined type
                preset = next(
                    (t for t in DEFAULT_RECORD_TYPES if t["id"] == record_type),
                    None,
                )
                if preset:
                    record_id = preset["id"]
                    record_name = preset["name"]
                    record_unit = preset["unit"]
                else:
                    errors["base"] = "invalid_type"

            if not errors:
                # Check for duplicates
                if any(
                    s[CONF_RECORD_TYPE] == record_id for s in self._record_sets
                ):
                    errors["base"] = "duplicate_set"
                else:
                    self._record_sets.append(
                        {
                            CONF_RECORD_TYPE: record_id,
                            CONF_RECORD_NAME: record_name,
                            CONF_RECORD_UNIT: record_unit,
                        }
                    )
                    return await self._save_options()

        # Build record type options
        type_options = [
            selector.SelectOptionDict(
                value=t["id"], label=f"{t['name']} ({t['unit']})"
            )
            for t in DEFAULT_RECORD_TYPES
        ]
        type_options.append(
            selector.SelectOptionDict(value=CUSTOM_TYPE, label=CUSTOM_TYPE_LABEL)
        )

        return self.async_show_form(
            step_id="add_record_type",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_RECORD_TYPE): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=type_options,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(CONF_RECORD_NAME): str,
                    vol.Optional(CONF_RECORD_UNIT): str,
                }
            ),
            errors=errors,
        )

    async def async_step_manage_sets(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage existing sets - show list and allow deletion."""
        if user_input is not None:
            # Process deletions
            sets_to_delete = user_input.get("delete_sets", [])
            self._record_sets = [
                s
                for s in self._record_sets
                if s[CONF_RECORD_TYPE] not in sets_to_delete
            ]
            return await self._save_options()

        # Build list of all sets
        all_sets = [
            selector.SelectOptionDict(
                value=rs[CONF_RECORD_TYPE],
                label=f"{rs[CONF_RECORD_NAME]} ({rs[CONF_RECORD_UNIT]})",
            )
            for rs in self._record_sets
        ]

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
                "count": str(len(self._record_sets)),
            },
        )

    async def _save_options(self) -> ConfigFlowResult:
        """Save the options and create entry."""
        return self.async_create_entry(
            data={
                CONF_RECORD_SETS: self._record_sets,
            },
        )
