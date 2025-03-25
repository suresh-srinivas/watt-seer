import dash
from dash import html, dcc
import plotly.express as px
import data_fetcher
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from datetime import datetime, date, timedelta
import pytz
import pandas as pd
from dateutil.relativedelta import relativedelta
from dash.exceptions import PreventUpdate
import logging
import argparse
from functools import wraps
import os

# Define supported utilities
SUPPORTED_UTILITIES = {
    'portlandgeneral': 'Portland General',
    'pacificpower': 'Pacific Power'
}

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask server first
server = Flask(__name__, 
              template_folder='templates')  # Changed to relative path

# Set secret key for session management
server.secret_key = 'your-secret-key-here'  # Change this to a secure secret key in production

# Initialize Dash with the Flask server
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            logger.debug('User not in session, redirecting to login')
            return redirect(url_for('login'))
        logger.debug('User in session, proceeding to dashboard')
        return f(*args, **kwargs)
    return decorated_function

# Login route
@server.route('/login', methods=['GET', 'POST'])
def login():
    logger.debug('Login route accessed')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        utility = request.form.get('utility')
        
        logger.debug(f'Login attempt - Username: {username}, Utility: {utility}')
        
        try:
            # Try to fetch data with the provided credentials
            test_credentials = {
                'username': username,
                'password': password,
                'utility': utility
            }
            # Try to fetch current month data to validate credentials
            data_fetcher.get_current_month_data(test_credentials)
            
            # If successful, update the CREDENTIALS
            CREDENTIALS.update(test_credentials)
            
            # Store user info in session
            session['user'] = username
            session['utility'] = utility
            logger.debug('Login successful, redirecting to dashboard')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logger.debug(f'Login failed - {str(e)}')
            return render_template('login.html', error='Invalid credentials', utilities=SUPPORTED_UTILITIES)
    
    logger.debug('Rendering login template')
    return render_template('login.html', utilities=SUPPORTED_UTILITIES)

# Logout route
@server.route('/logout')
def logout():
    logger.debug('Logout route accessed')
    session.pop('user', None)
    session.pop('utility', None)
    return redirect(url_for('login'))

# Root route redirects to login
@server.route('/')
def index():
    logger.debug('Root route accessed, redirecting to login')
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# Dashboard route
@server.route('/dashboard')
@login_required
def dashboard():
    logger.debug('Dashboard route accessed')
    return app.index()

# Protect all Dash routes
@server.before_request
def protect_dash_routes():
    if request.path.startswith('/_dash') or request.path.startswith('/assets'):
        if 'user' not in session:
            logger.debug('Unauthorized access to Dash route, redirecting to login')
            return redirect(url_for('login'))

# Credentials configuration
USE_DEV_CREDENTIALS = False  # Set to False before committing to GitHub

# GitHub credentials (safe to commit)
GITHUB_CREDENTIALS = {
    'username': 'example@email.com',
    'password': 'ExamplePass',
    'utility': 'portlandgeneral'
}

# Development credentials (DO NOT COMMIT)
DEV_CREDENTIALS = GITHUB_CREDENTIALS

# Set active credentials
CREDENTIALS = DEV_CREDENTIALS if USE_DEV_CREDENTIALS else GITHUB_CREDENTIALS

# Initialize empty figures
current_month_figure = px.line(title='Current Month Energy Consumption')
yearly_figure = px.bar(title='Monthly Energy Consumption (Selected Year)')
quarterly_figure = px.bar(title='Quarterly Energy Consumption (Selected Year)')
yearly_total_figure = px.bar(title='Total Energy Consumption by Year')

# Get available years (current year and previous 4 years)
current_year = datetime.now().year
available_years = list(range(current_year - 4, current_year + 1))

# Available months
available_months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

app.layout = html.Div([
    html.Div([
        html.H1("Energy Data Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),
        html.Div([
            html.A('Logout', href='/logout', style={'float': 'right', 'marginRight': '20px', 'color': 'red'})
        ])
    ]),
    
    # Year and Month selectors
    html.Div([
        # Year selector
        html.Div([
            html.Label("Select Year:", style={'marginRight': '10px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='year-selector',
                options=[{'label': str(year), 'value': year} for year in available_years],
                value=current_year,
                style={'width': '200px', 'display': 'inline-block'}
            ),
        ], style={'display': 'inline-block', 'marginRight': '20px'}),
        
        # Month selector
        html.Div([
            html.Label("Select Month:", style={'marginRight': '10px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='month-selector',
                options=[{'label': month, 'value': month} for month in available_months],
                value=datetime.now().strftime('%B'),  # Current month name
                style={'width': '200px', 'display': 'inline-block'}
            ),
        ], style={'display': 'inline-block'}),
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    # Main Dashboard
    html.Div([
        # First row
        html.Div([
            html.Div([
                html.H3(id='daily-view-title', children="Current Month Energy Consumption", style={'textAlign': 'center'}),
                dcc.Graph(id='current-month-figure', figure=current_month_figure),
            ], style={'width': '50%', 'padding': '20px', 'display': 'inline-block'}),
            
            html.Div([
                html.H3("Quarterly Energy Consumption (Selected Year)", style={'textAlign': 'center'}),
                dcc.Graph(id='yearly-figure', figure=yearly_figure),
            ], style={'width': '50%', 'padding': '20px', 'display': 'inline-block'}),
        ]),
        
        # Second row
        html.Div([
            html.Div([
                html.H3("Monthly Energy Consumption (Selected Year)", style={'textAlign': 'center'}),
                dcc.Graph(id='quarterly-figure', figure=quarterly_figure),
            ], style={'width': '50%', 'padding': '20px', 'display': 'inline-block'}),
            
            html.Div([
                html.H3("Total Energy Consumption by Year", style={'textAlign': 'center'}),
                dcc.Graph(id='yearly-total-figure', figure=yearly_total_figure),
            ], style={'width': '50%', 'padding': '20px', 'display': 'inline-block'}),
        ]),
    ]),
    
    # Auto-update interval
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # in milliseconds (5 minutes)
        n_intervals=0
    )
])

@app.callback(
    [dash.Output('current-month-figure', 'figure'),
     dash.Output('yearly-figure', 'figure'),
     dash.Output('quarterly-figure', 'figure'),
     dash.Output('yearly-total-figure', 'figure'),
     dash.Output('daily-view-title', 'children')],
    [dash.Input('interval-component', 'n_intervals'),
     dash.Input('year-selector', 'value'),
     dash.Input('month-selector', 'value')]
)
def update_graphs(n, selected_year, selected_month):
    try:
        figures = []
        selected_year = int(selected_year)
        
        # 1. Get current month data
        logger.info("Fetching current month data")
        current_month_data = data_fetcher.get_current_month_data(CREDENTIALS)
        
        if current_month_data.empty:
            empty_figures = [
                px.line(title='No data available'),
                px.bar(title='No data available'),
                px.bar(title='No data available'),
                px.bar(title='No data available'),
                "No data available"
            ]
            return empty_figures
            
        # Log the data structure for debugging
        logger.debug(f"Data types of columns: {current_month_data.dtypes}")
        logger.debug(f"First few rows of start_time: {current_month_data['start_time'].head()}")
        
        # Parse datetime with explicit timezone handling
        current_month_data['start_time'] = pd.to_datetime(current_month_data['start_time'], utc=True)
        
        # Add common fields used across different views
        # Convert to UTC for consistent date handling
        current_month_data['date'] = current_month_data['start_time'].dt.date
        current_month_data['month'] = current_month_data['start_time'].dt.strftime('%B %Y')
        current_month_data['quarter'] = current_month_data['start_time'].dt.quarter.map(lambda x: f'Q{x}')
        
        # 1. Daily view for current month
        daily_totals = current_month_data.groupby(['date', 'account_name'])['consumption'].sum().reset_index()
        
        # Calculate daily totals
        daily_combined = daily_totals.groupby('date')['consumption'].sum().reset_index()
        daily_combined['account_name'] = 'Total'
        
        # Combine individual accounts with total
        daily_totals = pd.concat([daily_totals, daily_combined], ignore_index=True)
        daily_totals = daily_totals.sort_values(['date', 'account_name'])
        
        current_month_name = datetime.now().strftime('%B %Y')
        current_fig = px.line(
            daily_totals,
            x='date',
            y='consumption',
            color='account_name',
            title=f"Daily Energy Consumption for {CREDENTIALS['username']} ({current_month_name})",
            labels={
                'date': 'Date',
                'consumption': 'Energy Consumption (kWh)',
                'account_name': 'Account'
            }
        )
        
        current_fig.update_traces(
            mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=6)
        )
        
        # Set custom colors and styles
        for trace in current_fig.data:
            if trace.name == 'Total':
                trace.line.dash = 'dash'
                trace.line.color = 'green'
                trace.marker.color = 'green'
            elif '7277230355' in trace.name:
                trace.line.color = 'blue'
                trace.marker.color = 'blue'
            elif '0858033726' in trace.name:
                trace.line.color = 'red'
                trace.marker.color = 'red'
        
        current_fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Energy Consumption (kWh)",
            hovermode='x unified',
            showlegend=True,
            legend_title="Account",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        figures.append(current_fig)
        
        # 2. Get quarterly data
        logger.info("Fetching quarterly data")
        quarterly_data = data_fetcher.get_quarterly_data(CREDENTIALS)
        
        if not quarterly_data.empty:
            # Parse datetime with explicit timezone handling
            quarterly_data['start_time'] = pd.to_datetime(quarterly_data['start_time'], utc=True)
            quarterly_totals = quarterly_data.groupby(['quarter', 'account_name'])['consumption'].sum().reset_index()
            quarterly_combined = quarterly_totals.groupby('quarter')['consumption'].sum().reset_index()
            quarterly_combined['account_name'] = 'Total'
            quarterly_totals = pd.concat([quarterly_totals, quarterly_combined], ignore_index=True)
            
            quarterly_fig = px.bar(
                quarterly_totals,
                x='quarter',
                y='consumption',
                color='account_name',
                title=f'Quarterly Energy Consumption for {CREDENTIALS["username"]} ({datetime.now().year})',
                labels={
                    'quarter': 'Quarter',
                    'consumption': 'Total Energy Consumption (kWh)',
                    'account_name': 'Account'
                },
                barmode='group'
            )
            
            quarterly_fig.update_layout(
                xaxis_title="Quarter",
                yaxis_title="Total Energy Consumption (kWh)",
                hovermode='x unified',
                showlegend=True,
                legend_title="Account"
            )
        else:
            quarterly_fig = px.bar(title='No quarterly data available')
        
        figures.append(quarterly_fig)
        
        # 3. Get yearly data
        logger.info("Fetching yearly data")
        yearly_data = data_fetcher.get_current_year_data(CREDENTIALS)
        
        if not yearly_data.empty:
            # Parse datetime with explicit timezone handling
            yearly_data['start_time'] = pd.to_datetime(yearly_data['start_time'], utc=True)
            yearly_data['month'] = yearly_data['start_time'].dt.strftime('%B %Y')
            yearly_totals = yearly_data.groupby(['month', 'account_name'])['consumption'].sum().reset_index()
            yearly_combined = yearly_totals.groupby('month')['consumption'].sum().reset_index()
            yearly_combined['account_name'] = 'Total'
            yearly_totals = pd.concat([yearly_totals, yearly_combined], ignore_index=True)
            
            # Sort months chronologically
            yearly_totals['sort_date'] = pd.to_datetime(yearly_totals['month'], format='%B %Y')
            yearly_totals = yearly_totals.sort_values(['sort_date', 'account_name'])
            
            yearly_fig = px.bar(
                yearly_totals,
                x='month',
                y='consumption',
                color='account_name',
                title=f'Monthly Energy Consumption for {CREDENTIALS["username"]} ({datetime.now().year})',
                labels={
                    'month': 'Month',
                    'consumption': 'Total Energy Consumption (kWh)',
                    'account_name': 'Account'
                },
                barmode='group'
            )
            
            yearly_fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Total Energy Consumption (kWh)",
                hovermode='x unified',
                showlegend=True,
                legend_title="Account"
            )
        else:
            yearly_fig = px.bar(title='No yearly data available')
        
        figures.append(yearly_fig)
        
        # 4. Total consumption by account
        if not yearly_data.empty:
            total_by_account = yearly_data.groupby('account_name')['consumption'].sum().reset_index()
            total_combined = pd.DataFrame([{
                'account_name': 'Total',
                'consumption': total_by_account['consumption'].sum()
            }])
            total_by_account = pd.concat([total_by_account, total_combined], ignore_index=True)
            
            total_fig = px.bar(
                total_by_account,
                x='account_name',
                y='consumption',
                title=f'Total Energy Consumption by Account for {CREDENTIALS["username"]} ({datetime.now().year})',
                labels={
                    'account_name': 'Account',
                    'consumption': 'Total Energy Consumption (kWh)'
                }
            )
            
            total_fig.update_layout(
                xaxis_title="Account",
                yaxis_title="Total Energy Consumption (kWh)",
                hovermode='x unified',
                showlegend=False
            )
        else:
            total_fig = px.bar(title='No total consumption data available')
        
        figures.append(total_fig)
        
        daily_view_title = f"Daily Energy Consumption for {CREDENTIALS['username']} ({current_month_name})"
        return figures + [daily_view_title]
            
    except Exception as e:
        logger.error(f"Error updating graphs: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return [
            px.line(title=f'Error loading data: {str(e)}'),
            px.bar(title=f'Error loading data: {str(e)}'),
            px.bar(title=f'Error loading data: {str(e)}'),
            px.bar(title=f'Error loading data: {str(e)}'),
            "Error loading data"
        ]

@server.route('/energy/daily', methods=['POST'])
def get_daily_energy():
    data = request.get_json()
    if not data or 'credentials' not in data:
        return jsonify({'error': 'No credentials provided'}), 400
    
    try:
        df = data_fetcher.get_current_month_data(data['credentials'])
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@server.route('/energy/weekly', methods=['POST'])
def get_weekly_energy():
    data = request.get_json()
    if not data or 'credentials' not in data:
        return jsonify({'error': 'No credentials provided'}), 400
    
    try:
        df = data_fetcher.get_weekly_data(data['credentials'])
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@server.route('/energy/quarterly', methods=['POST'])
def get_quarterly_energy():
    data = request.get_json()
    if not data or 'credentials' not in data:
        return jsonify({'error': 'No credentials provided'}), 400
    
    try:
        df = data_fetcher.get_quarterly_data(data['credentials'])
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@server.route('/energy/yearly', methods=['POST'])
def get_yearly_energy():
    data = request.get_json()
    if not data or 'credentials' not in data:
        return jsonify({'error': 'No credentials provided'}), 400
    
    try:
        df = data_fetcher.get_current_year_data(data['credentials'])
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@server.route('/energy/range', methods=['POST'])
def get_energy_by_range():
    data = request.get_json()
    if not data or 'credentials' not in data or 'start_date' not in data or 'end_date' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        df = data_fetcher.get_data_by_date_range(start_date, end_date, data['credentials'])
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_quarter_dates(year):
    """Get start and end dates for each quarter of a given year"""
    quarters = []
    for quarter in range(1, 5):
        start_month = (quarter - 1) * 3 + 1
        end_month = quarter * 3
        start_date = datetime(year, start_month, 1, tzinfo=pytz.UTC)
        if end_month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=pytz.UTC) - relativedelta(days=1)
        else:
            end_date = datetime(year, end_month + 1, 1, tzinfo=pytz.UTC) - relativedelta(days=1)
        quarters.append((start_date, end_date))
    return quarters

def get_year_dates(year):
    """Get start and end dates for a given year"""
    start_date = datetime(year, 1, 1, tzinfo=pytz.UTC)
    end_date = datetime(year + 1, 1, 1, tzinfo=pytz.UTC) - relativedelta(days=1)
    return start_date, end_date

def get_quarterly_data(credentials):
    """Fetch quarterly data for the current year"""
    current_year = datetime.now(pytz.UTC).year
    all_quarterly_data = []
    
    for start_date, end_date in get_quarter_dates(current_year):
        try:
            quarter_data = data_fetcher.get_data_by_date_range(start_date, end_date, credentials)
            if not quarter_data.empty:
                # Add quarter label
                quarter_data['quarter'] = f"Q{(start_date.month-1)//3 + 1}"
                all_quarterly_data.append(quarter_data)
        except Exception as e:
            print(f"Error fetching data for quarter {start_date.month//3 + 1}: {e}")
    
    if all_quarterly_data:
        return pd.concat(all_quarterly_data, ignore_index=True)
    return pd.DataFrame()

def get_yearly_data(credentials):
    """Fetch yearly data for the current year"""
    current_year = datetime.now(pytz.UTC).year
    start_date, end_date = get_year_dates(current_year)
    
    try:
        return data_fetcher.get_data_by_date_range(start_date, end_date, credentials)
    except Exception as e:
        print(f"Error fetching yearly data: {e}")
        return pd.DataFrame()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8050)
    args = parser.parse_args()
    
    app.run(debug=True, port=args.port, use_reloader=False)


