# Ha Health Record

A Home Assistant custom component for tracking health records of family members.

## Features

- **Quick Add**: Quickly log activities and growth records with one tap
- **Member Management**: Track multiple family members with individual profiles
- **Activity Tracking**: Log daily activities like feeding, diaper changes, sleep, etc.
- **Growth Tracking**: Record growth metrics like height, weight, head circumference
- **Record History**: View and filter records by date range and member
- **Search**: Full-text search across all records
- **Dark/Light Theme Support**: UI adapts to Home Assistant's theme settings
- **Multi-language**: Supports English, Traditional Chinese (zh-Hant), and Simplified Chinese (zh-Hans)

## Screenshots

The panel features:
- Top bar with sidebar toggle (follows HA theme)
- Member selection card
- Search bar
- Time filter with date range picker
- Quick action buttons for activities and growth records

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/WOOWTECH/ha_health_record` with category "Integration"
5. Install "Ha Health Record"
6. Restart Home Assistant

### Manual Installation

1. Download or clone this repository
2. Copy the `ha_health_record` folder to your `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Health Record"
4. Follow the setup wizard to add family members

## Usage

### Adding Members

1. Go to the Health Record panel
2. Click the "Member" tab
3. Click "+ Add Member"
4. Enter name and optional notes

### Logging Activities

1. Select a member from the dropdown
2. Click on an activity button (e.g., Feeding, Diaper)
3. Enter the amount and optional note
4. Click "Save"

### Recording Growth

1. Select a member from the dropdown
2. Click on a growth button (e.g., Height, Weight)
3. Enter the value
4. Click "Save"

### Viewing Records

1. Click the "Record" tab
2. Use the date filter to select a time range
3. Use the search bar to find specific records
4. Click on a record to expand details or edit

## API

The component exposes WebSocket APIs for integration with automations:

- `ha_health_record/get_members` - Get all members
- `ha_health_record/get_records` - Get records in date range
- `ha_health_record/log_activity` - Log an activity
- `ha_health_record/update_growth` - Record growth data
- `ha_health_record/add_member` - Add a new member
- `ha_health_record/update_member` - Update member info
- `ha_health_record/delete_member` - Delete a member

## Events

The component fires events that can be used in automations:

- `ha_health_record_activity_logged` - When an activity is logged
- `ha_health_record_growth_updated` - When growth data is recorded

## Version History

### 1.4.1
- Redesigned UI with top bar and sidebar toggle
- Added member selection card (like Finance Record)
- Added search bar on its own row
- Added time filter row with date range picker
- Changed growth buttons to blue (primary theme color)
- Added notes field to member edit/add dialog
- Fixed top bar to properly follow dark/light theme

### 1.4.0
- Initial public release

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
