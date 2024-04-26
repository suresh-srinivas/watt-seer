# Energy Consumption Analysis

This repository contains scripts for analyzing energy consumption data on an hourly, daily, weekly, and monthly basis.

## Files Description

- `energy-use.py`: Main Python script that loads hourly energy data, performs data aggregation to daily, weekly, and monthly intervals, and generates corresponding plots.

## Requirements

- Python 3.x
- Pandas
- Matplotlib

To install the required Python libraries, you can use the following command:

```bash
pip install pandas matplotlib
```


## Usage
Run the script using Python from the command line:

```bash
python energy-use.py 
```
This will generate PNG images for the daily, weekly, and monthly energy consumption visualizations based on the provided data.

## Data Format
The energy data should be in a tab-delimited file with the following columns:

- start_time: The starting time of the measurement (includes date and time).
- end_time: The ending time of the measurement (includes date and time).
- consumption: The amount of energy consumed in kWh.
- provided_cost: The cost of energy consumed in USD.

The start_time and end_time fields should be formatted to include timezone information, which will be converted to UTC and localized to remove timezone awareness within the script.

## Output
The script outputs several PNG files:

- Daily_Energy_Consumption.png: Shows daily energy consumption.
- Weekly_Energy_Consumption.png: (Optional) For weekly energy consumption visualization.
- Monthly_Energy_Consumption.png: (Optional) For monthly energy consumption visualization.

Each plot provides a visual representation of energy consumption patterns, assisting in trend analysis and decision-making processes.

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your proposed changes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

