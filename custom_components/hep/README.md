# HEP Elektra Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant integration for HEP Elektra ODS electricity accounts in Croatia. Monitor your electricity consumption, balance, pricing, and receive payment alerts.

## Features

- 📊 **Real-time Meter Readings** - Monitor current electricity consumption for both tariffs
- 💰 **Account Balance** - Track your account balance and latest bills
- 💵 **Current Pricing** - View real-time electricity prices (EUR/kWh) for VT/NT
- 📈 **Consumption History** - Historical consumption data by period
- ⚠️ **Payment Warnings** - Get notified about payment issues
- 🔄 **Automatic Updates** - Data refreshes every 24 hours
- 📱 **Energy Dashboard** - Compatible with HA Energy Dashboard

## Installation

### Option 1: Manual Installation

1. Copy the `custom_components/hep` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "HEP Elektra ODS" and select it
5. Enter your HEP Elektra ODS account credentials (email and password)

### Option 2: HACS (Coming Soon)

This integration will be available through HACS in the future.

## Configuration

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **HEP Elektra ODS**
4. Enter your credentials:
   - **Email/Username**: Your HEP Elektra ODS account email or username
   - **Password**: Your HEP Elektra ODS account password

## Sensors Created

For each HEP Elektra ODS account, the integration creates the following sensors:

### Meter Readings
- `sensor.hep_{account}_tarifa_1_reading` - Current T1 meter reading (kWh)
- `sensor.hep_{account}_tarifa_2_reading` - Current T2 meter reading (kWh)

### Balance & Billing
- `sensor.hep_{account}_balance` - Account balance (EUR)

### Pricing
- `sensor.hep_{account}_price_vt` - High tariff price (EUR/kWh)
- `sensor.hep_{account}_price_nt` - Low tariff price (EUR/kWh)

### Consumption History
- `sensor.hep_{account}_last_period_t1` - Previous billing period T1 (kWh)
- `sensor.hep_{account}_last_period_t2` - Previous billing period T2 (kWh)

### Alerts
- `binary_sensor.hep_{account}_payment_warning` - Payment warning indicator

## Energy Dashboard Integration

The meter reading sensors are fully compatible with Home Assistant's Energy Dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Click **Add Consumption**
3. Select `sensor.hep_{account}_tarifa_1_reading` and/or `sensor.hep_{account}_tarifa_2_reading`
4. Configure pricing if desired

## Manual Data Refresh

While the integration automatically updates every 24 hours, you can force a refresh:

1. Go to **Settings** → **Devices & Services**
2. Find **HEP Elektra**
3. Click the **⋮** menu → **Reload**

## Troubleshooting

### Authentication Errors

If you receive authentication errors:
- Verify your credentials at https://mojracun.hep.hr
- Ensure you're using your email address (not customer ID)
- Check if your account is active

### No Data Showing

- Wait a few minutes after adding the integration
- Check **Settings** → **System** → **Logs** for error messages
- Try reloading the integration

### Sensors Not Appearing

- Verify your HEP Elektra ODS account has active electricity service
- Check that you have at least one active contract
- Restart Home Assistant

## Privacy & Security

- Your credentials are stored securely in Home Assistant's encrypted storage
- Data is fetched directly from HEP Elektra ODS servers (no third-party services)
- No data is collected or transmitted outside your Home Assistant instance

##Support

For issues, questions, or feature requests, please visit the [GitHub Issues](https://github.com/knobtviker/ha-hep-ods/issues) page.

## Credits

HEP Elektra ODS is a trademark of HEP d.d. This integration is not officially affiliated with or endorsed by HEP Elektra ODS.

## License

This project is licensed under the MIT License.
