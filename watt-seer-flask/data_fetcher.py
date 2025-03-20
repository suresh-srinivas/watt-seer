import pandas as pd
from datetime import datetime, timedelta
import pytz
import subprocess
import tempfile
import os
import logging
import json
from io import StringIO

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_opower_command(credentials, start_date=None, end_date=None):
    """Run the opower command line tool and return the data as a DataFrame"""
    try:
        # Construct the command
        cmd = [
            'python', '-m', 'opower',
            '--utility', credentials['utility'],
            '--username', credentials['username'],
            '--password', credentials['password']
        ]
        
        # Add date range if provided
        if start_date:
            cmd.extend(['--start_date', start_date.strftime('%Y%m%d')])
        if end_date:
            cmd.extend(['--end_date', end_date.strftime('%Y%m%d')])
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stderr:
            logger.error(f"Command stderr: {result.stderr}")
        
        if result.returncode != 0:
            logger.error(f"Command failed with return code {result.returncode}")
            raise Exception(f"Command failed: {result.stderr}")
        
        # Parse the output
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            current_account = None
            all_data = []
            header = None
            data_lines = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('Getting historical data: account='):
                    # If we have data from previous account, process it
                    if header and data_lines:
                        df = process_data_lines(header, data_lines, current_account)
                        if not df.empty:
                            all_data.append(df)
                    
                    # Extract account info
                    current_account = extract_account_info(line)
                    header = None
                    data_lines = []
                elif line.startswith('start_time'):
                    header = line
                elif '\t' in line and not line.startswith('Getting') and not line.startswith('Current'):
                    data_lines.append(line)
            
            # Process the last account's data
            if header and data_lines:
                df = process_data_lines(header, data_lines, current_account)
                if not df.empty:
                    all_data.append(df)
            
            # Combine all data
            if all_data:
                return pd.concat(all_data, ignore_index=True)
            return pd.DataFrame()
            
        else:
            logger.error("No data received from command")
            raise Exception("No data received from command")
            
    except Exception as e:
        logger.error(f"Error in run_opower_command: {str(e)}")
        raise

def get_current_month_data(credentials):
    """Get energy consumption data from the 1st of current month until today"""
    try:
        # Get today's date
        end_date = datetime.now(pytz.UTC)
        # Get first day of the current month
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        logger.debug(f"Fetching current month data from {start_date} to {end_date}")
        return run_opower_command(credentials, start_date, end_date)
    except Exception as e:
        logger.error(f"Error in get_current_month_data: {str(e)}")
        raise

def get_weekly_data(credentials):
    """Get energy consumption data for the last week"""
    try:
        end_date = datetime.now(pytz.UTC)
        start_date = end_date - timedelta(days=7)
        logger.debug(f"Fetching weekly data from {start_date} to {end_date}")
        return run_opower_command(credentials, start_date, end_date)
    except Exception as e:
        logger.error(f"Error in get_weekly_data: {str(e)}")
        raise

def get_data_by_date_range(start_date, end_date, credentials):
    """Get energy consumption data for a specific date range"""
    try:
        logger.debug(f"Fetching data from {start_date} to {end_date}")
        
        # Run command without account specification
        cmd = [
            'python', '-m', 'opower',
            '--utility', credentials['utility'],
            '--username', credentials['username'],
            '--password', credentials['password'],
            '--start_date', start_date.strftime('%Y%m%d'),
            '--end_date', end_date.strftime('%Y%m%d')
        ]
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stderr:
            logger.error(f"Command stderr: {result.stderr}")
        
        if result.returncode != 0:
            logger.error(f"Command failed with return code {result.returncode}")
            raise Exception(f"Command failed: {result.stderr}")
        
        # Process the output
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            current_account = None
            all_data = []
            header = None
            data_lines = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('Getting historical data: account='):
                    # If we have data from previous account, process it
                    if header and data_lines:
                        df = process_data_lines(header, data_lines, current_account)
                        if not df.empty:
                            all_data.append(df)
                    
                    # Extract account info
                    current_account = extract_account_info(line)
                    header = None
                    data_lines = []
                elif line.startswith('start_time'):
                    header = line
                elif '\t' in line and not line.startswith('Getting') and not line.startswith('Current'):
                    data_lines.append(line)
            
            # Process the last account's data
            if header and data_lines:
                df = process_data_lines(header, data_lines, current_account)
                if not df.empty:
                    all_data.append(df)
            
            # Combine all data
            if all_data:
                return pd.concat(all_data, ignore_index=True)
            return pd.DataFrame()
            
        else:
            logger.error("No data received from command")
            raise Exception("No data received from command")
            
    except Exception as e:
        logger.error(f"Error in get_data_by_date_range: {str(e)}")
        raise

def extract_account_info(line):
    """Extract account information from the opower output header line"""
    try:
        # Example line: Getting historical data: account= Account(customer=Customer(uuid='61a1b970-1463-11ee-8d0d-020017032af5'), uuid='6a9a198c-9cc2-11ee-ac6e-020017032af5', utility_account_id='7277230355', id='7277230355', ...)
        account_info = {}
        
        # Extract utility_account_id
        if 'utility_account_id=' in line:
            account_info['utility_account_id'] = line.split("utility_account_id='")[1].split("'")[0]
        
        # Extract customer UUID
        if "Customer(uuid='" in line:
            account_info['customer_uuid'] = line.split("Customer(uuid='")[1].split("'")[0]
        
        # Extract account UUID
        if "uuid='" in line:
            account_info['account_uuid'] = line.split("uuid='")[1].split("'")[0]
        
        return account_info
    except Exception as e:
        logger.error(f"Error extracting account info: {str(e)}")
        return None

def process_data_lines(header, data_lines, account_info):
    """Process data lines for a single account"""
    try:
        if not header or len(data_lines) == 0 or not account_info:
            return pd.DataFrame()
        
        data_str = header + '\n' + '\n'.join(data_lines)
        df = pd.read_csv(
            StringIO(data_str), 
            delimiter='\t',
            parse_dates=['start_time', 'end_time']
        )
        
        if not df.empty:
            # Add account information
            df['account_id'] = account_info['utility_account_id']
            df['customer_uuid'] = account_info['customer_uuid']
            df['account_uuid'] = account_info['account_uuid']
            
            # Add a friendly account name
            df['account_name'] = f"Account {account_info['utility_account_id']}"
        
        return df
    except Exception as e:
        logger.error(f"Error processing data lines: {str(e)}")
        return pd.DataFrame()

def load_data(file_path):
    """Load data from a CSV file (kept for backward compatibility)"""
    energy_data = pd.read_csv(file_path, delimiter='\t', parse_dates=['start_time', 'end_time'])
    energy_data['start_time'] = pd.to_datetime(energy_data['start_time'], utc=True).dt.tz_convert(None)
    energy_data['end_time'] = pd.to_datetime(energy_data['end_time'], utc=True).dt.tz_convert(None)
    return energy_data

def resample_energy_data(energy_data, frequency):
    """Resample energy data to a specified frequency"""
    resampled_data = energy_data.resample(frequency, on='start_time').agg({
        'consumption': 'sum',
        'provided_cost': 'sum' if 'provided_cost' in energy_data.columns else None
    })
    return resampled_data

def get_current_year_data(credentials):
    """Get energy consumption data for the current year"""
    try:
        # Get current year's start and today's date
        current_year = datetime.now(pytz.UTC).year
        start_date = datetime(current_year, 1, 1, tzinfo=pytz.UTC)
        end_date = datetime.now(pytz.UTC)
        logger.debug(f"Fetching current year data from {start_date} to {end_date}")
        return run_opower_command(credentials, start_date, end_date)
    except Exception as e:
        logger.error(f"Error in get_current_year_data: {str(e)}")
        raise

def get_quarterly_data(credentials):
    """Get energy consumption data for each quarter of the current year"""
    try:
        # Get current year
        current_year = datetime.now(pytz.UTC).year
        all_quarterly_data = []
        
        # Define quarters
        quarters = [
            (datetime(current_year, 1, 1, tzinfo=pytz.UTC), datetime(current_year, 3, 31, tzinfo=pytz.UTC)),
            (datetime(current_year, 4, 1, tzinfo=pytz.UTC), datetime(current_year, 6, 30, tzinfo=pytz.UTC)),
            (datetime(current_year, 7, 1, tzinfo=pytz.UTC), datetime(current_year, 9, 30, tzinfo=pytz.UTC)),
            (datetime(current_year, 10, 1, tzinfo=pytz.UTC), datetime(current_year, 12, 31, tzinfo=pytz.UTC))
        ]
        
        # Fetch data for each quarter
        for i, (start_date, end_date) in enumerate(quarters, 1):
            # Only fetch data for quarters that have already started
            if start_date > datetime.now(pytz.UTC):
                continue
                
            try:
                quarter_data = run_opower_command(credentials, start_date, end_date)
                if not quarter_data.empty:
                    quarter_data['quarter'] = f'Q{i}'
                    all_quarterly_data.append(quarter_data)
            except Exception as e:
                logger.error(f"Error fetching data for Q{i}: {str(e)}")
        
        # Combine all quarterly data
        if all_quarterly_data:
            return pd.concat(all_quarterly_data, ignore_index=True)
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Error in get_quarterly_data: {str(e)}")
        raise


