
from flask import Flask, render_template, request, jsonify
import data_fetcher

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    utility_name = request.form.get('utility_name', 'PortlandGeneral')
    data = data_fetcher.get_data(utility_name)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
