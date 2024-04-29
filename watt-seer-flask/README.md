
# Energy Data Dashboard

This dashboard visualizes daily, weekly, and monthly energy consumption using Python, Dash, and Plotly.

## Installation

Before running the dashboard, ensure you have the necessary packages installed:

```bash
pip install dash pandas plotly
```

## Usage

To run the dashboard, execute the script. The application will start on your local server, typically accessible via `http://127.0.0.1:8050/` in your web browser.

## Application Structure

- `data_fetcher.py`: This module contains functions to load and process the energy data.
- `app.py`: This script initializes the Dash application and defines the layout and visualizations.

## Features

- **Daily Energy Consumption**: Line graph showing the total energy consumption per day.
- **Weekly Energy Consumption**: Line graph showing the total energy consumption per week.
- **Monthly Energy Consumption**: Line graph showing the total energy consumption per month.

## Development

Add additional features or data sources to the dashboard by modifying `data_fetcher.py` and `app.py` as needed.

## Contributors

Feel free to contribute to this project by submitting issues or pull requests.

## License

This project is open-sourced under the MIT license.
