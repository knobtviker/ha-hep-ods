# HEP Elektra ODS Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/knobtviker/ha-hep-ods.svg)](https://github.com/knobtviker/ha-hep-ods/releases)
[![License](https://img.shields.io/github/license/knobtviker/ha-hep-ods.svg)](LICENSE)

Home Assistant integration for HEP Elektra ODS electricity accounts in Croatia. Monitor your electricity consumption, balance, pricing, and receive payment alerts directly in Home Assistant.

## Features

- 📊 **Real-time Meter Readings** - Monitor current electricity consumption for both tariffs
- 💰 **Account Balance** - Track your account balance and latest bills  
- 💵 **Current Pricing** - View real-time electricity prices (EUR/kWh) for VT/NT
- 📈 **Consumption History** - Historical consumption data by period
- ⚠️ **Payment Warnings** - Get notified about payment issues
- 🔄 **Automatic Updates** - Data refreshes periodically (configurable 1-24 hours)
- 📱 **Energy Dashboard** - Compatible with HA Energy Dashboard

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the 3 dots (⋮) in the top right
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/knobtviker/ha-hep-ods`
6. Select category: "Integration"
7. Click "Install"
8. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/hep` folder to your `config/custom_components/` directory
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for "HEP Elektra ODS"

## Configuration

### Initial Setup

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **HEP Elektra ODS**
4. Enter your credentials:
   - **Email/Username**: Your HEP account email or username
   - **Password**: Your HEP account password

### Configure Options

After installation, you can customize the integration:

1. Go to **Settings** → **Devices & Services** → **HEP Elektra ODS**
2. Click the **Configure** button (gear icon)
3. Adjust settings:
   - **Update interval**: Set how often data is fetched (1-24 hours, default: 24)

## Sensors

Each HEP account creates 8 sensors:

### Meter Readings (Energy Dashboard Compatible)
- `sensor.hep_{account}_tarifa_1_reading` - T1 meter reading (kWh)
- `sensor.hep_{account}_tarifa_2_reading` - T2 meter reading (kWh)

### Financial
- `sensor.hep_{account}_balance` - Account balance (EUR)

### Pricing
- `sensor.hep_{account}_price_vt` - High tariff price (EUR/kWh)
- `sensor.hep_{account}_price_nt` - Low tariff price (EUR/kWh)

### Consumption History
- `sensor.hep_{account}_last_period_t1` - Previous period T1 (kWh)
- `sensor.hep_{account}_last_period_t2` - Previous period T2 (kWh)

### Alerts
- `binary_sensor.hep_{account}_payment_warning` - Payment warning indicator
  - **State ON**: Active warnings dated within the previous, current, or next month
  - **State OFF**: No warnings or warnings outside the 3-month window
  - Older warnings remain visible in sensor attributes but don't trigger the alert state
  - This prevents false alarms from historical payment issues

## Energy Dashboard Setup

1. Go to **Settings** → **Dashboards** → **Energy**
2. Click **Add Consumption**
3. Select the T1 and/or T2 meter reading sensors
4. Configure pricing using the price sensors if desired

## OMM Services (Meter Reading Submission)

Submit your electricity meter readings directly to HEP OMM system from Home Assistant.

### Submit OMM Reading

Submit meter reading for your OMM device. The reading date is automatically set to today's date.

**Service**: `hep.submit_omm_reading`

**Parameters**:
- `omm_id`: Meter ID (10 digits) - Auto-filled from your account if configured
- `tarifa1`: Reading for Tariff 1 (integer > 0)
- `tarifa2`: Reading for Tariff 2 (integer > 0)

**Example**:
```yaml
service: hep.submit_omm_reading
data:
  omm_id: "0123456789"
  tarifa1: 26124
  tarifa2: 11854
```

**Usage via UI**:
1. Go to **Developer Tools** → **Services**
2. Select **HEP Elektra ODS: Submit OMM Reading**
3. Fill in the form (OMM ID will be pre-filled if available)
4. Click **Call Service**

### Force Submit OMM Reading

If normal submission fails (e.g., reading already exists), you can force submit:

**Service**: `hep.force_submit_omm_reading`

Use this when the normal submit fails and you need to override the existing reading.

## Manual Refresh

You can force an immediate data refresh at any time:

**Settings** → **Devices & Services** → **HEP Elektra ODS** → **⋮** → **Reload**

## Troubleshooting

### Authentication Errors
- Verify credentials at https://mojracun.hep.hr
- Ensure you're using your email address
- Check account is active

### No Data Showing
- Wait a few minutes after setup
- Check logs: **Settings** → **System** → **Logs**
- Try reloading the integration

## Support

- [Report Issues](https://github.com/knobtviker/ha-hep-ods/issues)
- [Feature Requests](https://github.com/knobtviker/ha-hep-ods/issues/new)

## Credits

Developed by Bojan Komljenovic

*HEP Elektra ODS is a trademark of HEP d.d. This integration is unofficial and not affiliated with HEP.*

## License

[MIT License](LICENSE)
