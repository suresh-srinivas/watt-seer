import pandas as pd

def load_data(file_path):
    energy_data = pd.read_csv(file_path, delimiter='\t', parse_dates=['start_time', 'end_time'])
    energy_data['start_time'] = pd.to_datetime(energy_data['start_time'], utc=True).dt.tz_convert(None)
    energy_data['end_time'] = pd.to_datetime(energy_data['end_time'], utc=True).dt.tz_convert(None)
    return energy_data

def resample_energy_data(energy_data, frequency):
    # Assume 'consumption' is the column you want to sum
    # Ensure that only numeric columns or specific columns are resampled
    resampled_data = energy_data.resample(frequency, on='start_time').agg({
        'consumption': 'sum',  # Summing consumption
        'provided_cost': 'sum'  # Summing cost if applicable
        # You can add more columns to sum or aggregate differently
    })
    return resampled_data


