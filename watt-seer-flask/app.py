import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import data_fetcher

# Load the data
energy_data = data_fetcher.load_data('data/energy1.dat')

app = dash.Dash(__name__)

daily_data = data_fetcher.resample_energy_data(energy_data, 'D')
weekly_data = data_fetcher.resample_energy_data(energy_data, 'W')
monthly_data = data_fetcher.resample_energy_data(energy_data, 'M')

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

app.layout = html.Div([
    html.H1("Energy Data Dashboard"),
    dcc.Graph(figure=daily_figure),
    dcc.Graph(figure=weekly_figure),
    dcc.Graph(figure=monthly_figure)
])

if __name__ == '__main__':
    app.run_server(debug=True)


