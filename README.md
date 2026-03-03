# Ha Health Record

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-41BDF5.svg)](https://www.home-assistant.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/oaoomg/ha_health_record)](https://github.com/WOOWTECH/ha_health_record/releases)

**English** | [繁體中文](README_zh-TW.md)

A Home Assistant custom integration for tracking family members' health records. Manage any custom record types through a dedicated sidebar panel with full timeline, filtering, and inline editing.

![Health Record Panel](screenshots/record-tab.png)

## Features

- **Multi-member management** - Track health records for multiple family members independently
- **Flexible record types** - Built-in types (feeding, sleep, weight, height) plus unlimited custom types with configurable units and default values
- **Dedicated sidebar panel** - Full-featured UI with date filtering, search, type toggles, inline editing, and record timeline
- **Home Assistant entities** - Each record type creates sensor, number, button, and text entities for native HA integration
- **Event-driven automations** - Fires `ha_health_record_record_logged` events for use in automations
- **CSV export** - Export all records for a member as CSV
- **Local-only** - All data stored locally in Home Assistant, no cloud dependencies

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click the three-dot menu in the top right corner
3. Select **Custom repositories**
4. Enter repository URL: `https://github.com/WOOWTECH/ha_health_record`
5. Select category: **Integration**
6. Click **Add**, then find "Ha Health Record" in the HACS integration list and click **Download**
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/WOOWTECH/ha_health_record/releases)
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

The integration will automatically create a sidebar panel entry.

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

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
