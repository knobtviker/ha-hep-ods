# HEP Elektra ODS

Monitor your HEP Elektra ODS electricity account directly in Home Assistant.

## Features

- 📊 **Real-time meter readings** for both tariffs (T1/T2)
- 💰 **Account balance** tracking
- 💵 **Current electricity prices** (EUR/kWh)
- 📈 **Consumption history**
- ⚠️ **Payment warnings**
- 📱 **Energy Dashboard** compatible

## Installation

### HACS

1. Open HACS
2. Go to "Integrations"
3. Click the 3 dots in the top right
4. Select "Custom repositories"
5. Add `https://github.com/knobtviker/ha-hep-ods` as an Integration
6. Click "Install"
7. Restart Home Assistant

### Manual

Copy the `custom_components/hep` folder to your `config/custom_components/` directory and restart Home Assistant.

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **HEP Elektra ODS**
4. Enter your credentials from https://mojracun.hep.hr

## What You Get

### For Each Account
- Current meter readings (T1 & T2)
- Account balance
- Electricity prices (VT/NT)
- Last period consumption
- Payment warning alerts

All sensors are grouped under one device per account with rich attributes.

## Support

Having issues? [Open an issue](https://github.com/knobtviker/ha-hep-ods/issues)

---

*HEP Elektra ODS is a trademark of HEP d.d. This integration is unofficial.*
