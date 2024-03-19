import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify
import time
from threading import Thread

app = Flask(__name__)

# Global variable to store the fetched data
global_data = {
    'datum': '',
    'uhrzeit': '',
    'pegel': '',
    'grafik': '',
    'water_level_status': ''
}

# Function to fetch Hochwasser data from the website
def get_hochwasser_data():
    url = 'https://www.stadt-koeln.de/interne-dienste/hochwasser/pegel_ws.php'

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting relevant data from the HTML
        datum = soup.find('datum').text
        uhrzeit = soup.find('uhrzeit').text
        pegel = soup.find('pegel').text
        grafik = soup.find('grafik').text

        # Converting month names to numerical format in the date
        months = {
            'Januar': '01',
            'Februar': '02',
            'März': '03',
            'April': '04',
            'Mai': '05',
            'Juni': '06',
            'Juli': '07',
            'August': '08',
            'September': '09',
            'Oktober': '10',
            'November': '11',
            'Dezember': '12'
        }
        for month in months:
            if month in datum:
                datum = datum.replace(month, months[month])

        # Determining the water level status based on the fetched data
        water_level_status = 'Not Available to Work'
        if float(pegel.replace(',', '.')) <= 1.2:
            water_level_status = 'Available to Work'

        # Updating the global data dictionary
        global global_data
        global_data = {
            'datum': datum,
            'uhrzeit': uhrzeit,
            'pegel': pegel,
            'grafik': grafik,
            'water_level_status': water_level_status
        }
    except requests.RequestException as e:
        print('Error:', e)

# Function to continuously update the data in the background
def update_data_loop():
    while True:
        get_hochwasser_data()
        time.sleep(5)  # Update every 5 seconds

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html', data=global_data)

# Route to fetch the data via AJAX
@app.route('/get_data')
def get_data():
    return jsonify(global_data)

if __name__ == '__main__':
    # Start a new thread to update data in the background
    update_thread = Thread(target=update_data_loop)
    update_thread.daemon = True
    update_thread.start()

    app.run(debug=True)
