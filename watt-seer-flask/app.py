import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import data_fetcher
from flask import Flask, jsonify, request

# Load the data
energy_data = data_fetcher.load_data('data/energy1.dat')

app = dash.Dash(__name__)
server = app.server  # Get the Flask server instance


daily_data = data_fetcher.resample_energy_data(energy_data, 'D')
weekly_data = data_fetcher.resample_energy_data(energy_data, 'W')
monthly_data = data_fetcher.resample_energy_data(energy_data, 'ME')
quarterly_data = data_fetcher.resample_energy_data(energy_data, 'QE')
yearly_data = data_fetcher.resample_energy_data(energy_data, 'YE')

daily_figure = px.line(daily_data, x=daily_data.index, y='consumption', title='Daily Energy Consumption', 
                       labels={
                           'date': 'Date',
                           'consumption': 'Energy Consumption (kWh)'
                       })
weekly_figure = px.line(weekly_data, x=weekly_data.index, y='consumption', title='Weekly Energy Consumption',
                       labels={
                           'date': 'Date',
                           'consumption': 'Energy Consumption (kWh)'
                       })
monthly_figure = px.line(monthly_data, x=monthly_data.index, y='consumption', title='Monthly Energy Consumption',
                       labels={
                           'date': 'Date',
                           'consumption': 'Energy Consumption (kWh)'
                       })
quarterly_figure = px.line(quarterly_data, x=quarterly_data.index, y='consumption', title='Quarterly Energy Consumption',
                       labels={
                           'date': 'Date',
                           'consumption': 'Energy Consumption (kWh)'
                       })
yearly_figure = px.line(yearly_data, x=yearly_data.index, y='consumption', title='Yearly Energy Consumption',
                       labels={
                           'date': 'Date',
                           'consumption': 'Energy Consumption (kWh)'
                       })
app.layout = html.Div([
    html.H1("Energy Data Dashboard"),
    dcc.Graph(figure=daily_figure),
    dcc.Graph(figure=weekly_figure),
    dcc.Graph(figure=monthly_figure),
	dcc.Graph(figure=quarterly_figure),
    dcc.Graph(figure=yearly_figure)

])

# Endpoint to get daily energy consumption
@server.route('/energy/daily', methods=['GET'])
def get_daily_energy():
    try:
        # Assume get_daily_data() is a function in data_fetcher that returns daily energy data
        data = data_fetcher.get_daily_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to get energy data by date range
@server.route('/energy/range', methods=['POST'])
def get_energy_by_range():
    try:
        # Expecting JSON data with 'start_date' and 'end_date'
        request_data = request.get_json()
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        if not start_date or not end_date:
            return jsonify({"error": "Please provide start_date and end_date"}), 400
        
        # Assume get_data_by_date_range() is a function in data_fetcher that accepts start and end dates
        data = data_fetcher.get_data_by_date_range(start_date, end_date)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run_server(debug=True)


