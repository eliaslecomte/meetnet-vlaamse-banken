# Meetnet Vlaamse Banken - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant integration for the [Meetnet Vlaamse Banken](https://meetnetvlaamsebanken.be/) (Flemish Banks Monitoring Network) API. This integration provides real-time weather and oceanographic data from monitoring stations along the Belgian coast.

## Features

- **Wind data**: Speed, direction, and gusts
- **Temperature**: Air and water temperature
- **Water levels**: Tidal and wave height measurements
- **Pressure**: Atmospheric pressure readings
- **Historical data**: All sensors support Home Assistant's long-term statistics for historical tracking

## Prerequisites

You need API credentials for the Meetnet Vlaamse Banken API. You can request access at [meetnetvlaamsebanken.be](https://meetnetvlaamsebanken.be/).

## Installation

### HACS (Recommended)

This integration is available in the default HACS store.

[![Open your Home Assistant instance and open this repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eliaslecomte&repository=meetnet-vlaamse-banken&category=integration)

Or manually:

1. Open HACS in your Home Assistant instance
2. Search for "Meetnet Vlaamse Banken"
3. Open it and click **Download**
4. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/meetnet_vlaamse_banken` folder from this repository
2. Copy it to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "Meetnet Vlaamse Banken"
4. Enter your API credentials (username and password)
5. Select the monitoring locations you want to track
6. Click **Submit**

## Available Sensors

The integration creates sensors based on the data available at your selected locations. Common sensors include:

| Parameter | Description | Unit |
|-----------|-------------|------|
| Wind Speed | Average wind speed | m/s |
| Wind Direction | Wind direction | degrees |
| Wind Gust | Maximum wind gust | m/s |
| Air Temperature | Ambient air temperature | °C |
| Water Temperature | Sea water temperature | °C |
| Air Pressure | Atmospheric pressure | hPa |
| Water Level | Tidal water level | m |
| Wave Height | Significant wave height | m |

## Updating Location Selection

After initial setup, you can modify your selected locations:

1. Go to **Settings** > **Devices & Services**
2. Find the Meetnet Vlaamse Banken integration
3. Click **Configure**
4. Select or deselect locations as needed
5. Click **Submit**

## Data Update Interval

The integration polls the API every 5 minutes by default. This balances data freshness with API load.

## Troubleshooting

### Authentication Errors

If you see authentication errors:
1. Verify your credentials are correct
2. Check if you can log in at [meetnetvlaamsebanken.be](https://meetnetvlaamsebanken.be/)
3. If your password changed, go to **Settings** > **Devices & Services** and follow the reauthentication prompt for Meetnet Vlaamse Banken to enter your updated credentials. If no prompt appears yet, reload the integration to trigger an authentication check.

### Missing Data

Some monitoring stations may not have all sensor types available. The integration only creates sensors for data that is actually available at each location.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially affiliated with Meetnet Vlaamse Banken. Use at your own risk.
