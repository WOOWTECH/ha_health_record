# Ha Health Record

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-41BDF5.svg)](https://www.home-assistant.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/oaoomg/ha_health_record)](https://github.com/oaoomg/ha_health_record/releases)

**English** | [繁體中文](README_zh-TW.md)

A Home Assistant custom integration for tracking family members' health records. Manage feeding, sleep, weight, height, and custom record types through a dedicated sidebar panel with full timeline, filtering, and inline editing.

![Health Record Panel](screenshots/record-tab.png)

## Features

- **Multi-member management** - Track health records for multiple family members independently
- **Flexible record types** - Built-in types (feeding, sleep, weight, height) plus unlimited custom types with configurable units and default values
- **Dedicated sidebar panel** - Full-featured UI with date filtering, search, type toggles, inline editing, and record timeline
- **Home Assistant entities** - Each record type creates sensor, number, button, and text entities for native HA integration
- **Event-driven automations** - Fires `ha_health_record_record_logged` events for use in automations
- **CSV export** - Export all records for a member as CSV
- **Multi-language** - Supports English, Traditional Chinese (繁體中文), and Simplified Chinese (简体中文)
- **Local-only** - All data stored locally in Home Assistant, no cloud dependencies

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click the three-dot menu in the top right corner
3. Select **Custom repositories**
4. Enter repository URL: `https://github.com/oaoomg/ha_health_record`
5. Select category: **Integration**
6. Click **Add**, then find "Ha Health Record" in the HACS integration list and click **Download**
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/oaoomg/ha_health_record/releases)
2. Copy the `custom_components/ha_health_record` folder to your Home Assistant `config/custom_components/` directory:
   ```
   config/
   └── custom_components/
       └── ha_health_record/
           ├── __init__.py
           ├── manifest.json
           ├── config_flow.py
           ├── coordinator.py
           ├── const.py
           ├── sensor.py
           ├── number.py
           ├── button.py
           ├── text.py
           ├── panel.py
           └── frontend/
               ├── ha-health-record-panel.js
               └── sidebar-title.js
   ```
3. Restart Home Assistant

## Configuration

### Adding Your First Member

1. Go to **Settings** > **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Ha Health Record**
4. Enter a member name (e.g., "Baby Emma") and optionally a custom ID
5. Click **Submit**

![Config Flow](screenshots/config-flow.png)

The integration will automatically create default record types (feeding, sleep, weight, height) and a sidebar panel entry.

### Adding More Members

Repeat the config flow above for each family member. Each member gets their own device, entities, and independent data storage.

### Managing Record Types

Record types can be added, edited, or removed from the **Settings** tab in the sidebar panel. Each record type has:
- **Name** - Display name (e.g., "Feeding")
- **Unit** - Measurement unit (e.g., "ml", "kg", "cm")
- **Default Value** - Fixed value or "Last Value" mode for quick entry

## Panel UI

### Member Switcher

Switch between family members or add a new member directly from the panel header.

![Member Switcher](screenshots/member-switcher.png)

### Member Overview

View total records, last record timestamp, record type count, and latest values at a glance.

![Member Overview](screenshots/member-overview.png)

### Record Tab

Browse the full record timeline with date range filtering, text search, and record type toggles. Click any record to expand it for editing or deletion.

![Record Tab](screenshots/record-tab.png)

### Settings Tab

Manage member info, record types (add/edit/delete), and export data as CSV.

![Settings Tab](screenshots/settings-tab.png)

### Add Record Dialog

Log a new record by selecting a type, setting the timestamp, entering a value, and optionally adding a note.

![Add Record Dialog](screenshots/add-record-dialog.png)

## Entities

For each record type per member, the integration creates 4 entities:

| Entity Type | Entity ID Pattern | Description |
|-------------|-------------------|-------------|
| **Sensor** | `sensor.<member>_<type>_record` | Last recorded value with timestamp and note attributes |
| **Number** | `number.<member>_<type>_value` | Set a value to log a new record |
| **Button** | `button.<member>_<type>_log` | Press to log a record with the current number value |
| **Text** | `text.<member>_<type>_note` | Set a note for the next record |

### Example Entity IDs

For a member "baby_emma" with record type "weight":
- `sensor.baby_emma_weight_record` - Shows last weight value
- `number.baby_emma_weight_value` - Set weight value
- `button.baby_emma_weight_log` - Log weight record
- `text.baby_emma_weight_note` - Set note for weight record

### Sensor Attributes

Each sensor entity exposes:
- `last_value` - The most recent recorded value
- `last_timestamp` - ISO timestamp of the last record
- `last_note` - Note from the last record (if any)
- `record_count` - Total number of records for this type

### Logging Records Without the Panel

You can log records purely through HA entities:

1. Set the value: `number.baby_emma_weight_value` = `3.5`
2. (Optional) Set a note: `text.baby_emma_weight_note` = `"After feeding"`
3. Press the button: `button.baby_emma_weight_log`

## Events & Automations

### Event: `ha_health_record_record_logged`

Fired every time a record is logged (from the panel or via entities).

| Field | Description |
|-------|-------------|
| `member_id` | Member identifier (e.g., `baby_emma`) |
| `member_name` | Member display name (e.g., `Baby Emma`) |
| `record_type` | Record type ID (e.g., `weight`) |
| `value` | Recorded value |
| `unit` | Unit of measurement |
| `note` | Optional note text |
| `timestamp` | ISO timestamp of the record |

### Automation Examples

**Send a notification when a record is logged:**

```yaml
automation:
  - alias: "Health Record Notification"
    trigger:
      - platform: event
        event_type: ha_health_record_record_logged
    action:
      - service: notify.mobile_app
        data:
          title: "Health Record"
          message: >
            {{ trigger.event.data.member_name }}:
            {{ trigger.event.data.record_type }} =
            {{ trigger.event.data.value }} {{ trigger.event.data.unit }}
```

**Track daily feeding count with a counter:**

```yaml
automation:
  - alias: "Count Daily Feedings"
    trigger:
      - platform: event
        event_type: ha_health_record_record_logged
        event_data:
          record_type: feeding
    action:
      - service: counter.increment
        target:
          entity_id: counter.daily_feedings
```

## Troubleshooting

### Sidebar shows wrong language

The sidebar panel title automatically detects your Home Assistant language setting. If the title appears in the wrong language, try:
1. Navigate to your profile settings and verify the language
2. Reload the browser page

### Record types not appearing

After adding or modifying record types in the Settings tab, the entities are created on the next integration reload. Go to **Settings** > **Devices & Services** > **Ha Health Record** > click the three-dot menu on the member > **Reload**.

### Where is data stored?

All health record data is stored locally in Home Assistant's `.storage` directory as JSON files, one per member (e.g., `.storage/ha_health_record_baby_emma`). Data persists across restarts and updates.

### Is there a record limit?

There is no hard limit on the number of records. The system uses efficient JSON storage with delayed saves for batched operations. Performance has been tested with thousands of records per member.

### How to export data?

Go to the sidebar panel > select a member > **Settings** tab > expand **Data Management** > click **Export CSV**. This downloads all records for the selected member as a CSV file.

### How to remove a member?

Go to **Settings** > **Devices & Services** > **Ha Health Record** > click the three-dot menu on the member's config entry > **Delete**. This removes the member, all their entities, and their stored data.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
