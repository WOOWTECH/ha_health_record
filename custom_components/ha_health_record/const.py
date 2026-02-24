"""Constants for Ha Health Record integration."""
from typing import Final

DOMAIN: Final = "ha_health_record"

# Storage
STORAGE_KEY: Final = DOMAIN
STORAGE_VERSION: Final = 1

# Config keys
CONF_MEMBER_NAME = "member_name"
CONF_MEMBER_ID = "member_id"
CONF_ACTIVITY_SETS = "activity_sets"
CONF_GROWTH_SETS = "growth_sets"

# Activity set keys
CONF_ACTIVITY_TYPE = "activity_type"
CONF_ACTIVITY_NAME = "activity_name"
CONF_ACTIVITY_UNIT = "activity_unit"

# Growth set keys
CONF_GROWTH_TYPE = "growth_type"
CONF_GROWTH_NAME = "growth_name"
CONF_GROWTH_UNIT = "growth_unit"

# Event names
EVENT_ACTIVITY_LOGGED = f"{DOMAIN}_activity_logged"

# Default activity types
DEFAULT_ACTIVITY_TYPES = [
    {"id": "feeding", "name": "餵奶", "unit": "ml"},
    {"id": "sleep", "name": "睡眠", "unit": "分鐘"},
]

# Default growth types
DEFAULT_GROWTH_TYPES = [
    {"id": "weight", "name": "體重", "unit": "kg"},
    {"id": "height", "name": "身高", "unit": "cm"},
]

# Custom type identifier
CUSTOM_TYPE = "custom"
