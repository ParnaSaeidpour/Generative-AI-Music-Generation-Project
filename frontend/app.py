import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory, url_for

from GenerateMusic import generate_music_genetic
from scripts.weather_data import get_weather_data_by_city

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, 'static', 'generated')
SOUNDFONT_PATH = os.getenv('SOUNDFONT_PATH', os.path.join(BASE_DIR, 'soundfonts', 'FluidR3_GM.sf2'))

app = Flask(__name__)

# Supported cities and the ASCII names used for generated files
CITIES = {
    "Stockholm": "stockholm",
    "Gothenburg": "gothenburg",
    "Malmö": "malmo",
    "Uppsala": "uppsala",
    "Jönköping": "jonkoping",
    "Kiruna": "kiruna",
}


def get_weather_data(city):
    data = get_weather_data_by_city(city)
    logger.info("Got weather data for %s", city)
    return {
        'temperature': data['temperature'],
        'wind_speed': data['wind_speed'],
        'rain': data['precipitation'] > 0,
        'precipitation_mm': data['precipitation_mm'],
        'cloudiness': data['cloudiness'],
        'humidity': data['humidity']
    }


def error(message, status):
    return jsonify({'status': 'error', 'message': message}), status


@app.route('/')
def index():
    return render_template('index.html', cities=list(CITIES))


@app.route('/generate', methods=['POST'])
def generate_music():
    city = request.form.get('city')
    if not city:
        return error('City is required', 400)
    if city not in CITIES:
        return error('Unknown city', 400)

    # The file name only uses the known city name, never raw user input
    filename = CITIES[city] + '_' + datetime.now().strftime('%Y%m%d%H')

    try:
        weather_data = get_weather_data(city)
    except Exception:
        logger.exception("Weather lookup failed for %s", city)
        return error('Weather data is not available right now. Please try again later.', 502)

    try:
        files = generate_music_genetic(weather_data, filename, GENERATED_DIR, SOUNDFONT_PATH)
    except Exception:
        logger.exception("Music generation failed for %s", city)
        return error('Music could not be generated.', 500)

    return jsonify({
        'status': 'success',
        'message': f'Generated music for {city} (Temperature: {weather_data["temperature"]}°C, Wind: {weather_data["wind_speed"]} m/s, Rain: {"Yes" if weather_data["rain"] else "No"})',
        'weather': weather_data,
        'midi_url': url_for('static', filename='generated/' + filename + '.mid'),
        'wav_url': url_for('static', filename='generated/' + filename + '.wav') if files['wav'] else None
    })


@app.route('/play/<filename>')
def play_audio(filename):
    # send_from_directory refuses paths outside GENERATED_DIR
    return send_from_directory(
        GENERATED_DIR, filename,
        mimetype='audio/wav' if filename.endswith('.wav') else 'audio/midi'
    )


@app.route('/weather/<city>')
def get_weather(city):
    if city not in CITIES:
        return error('Unknown city', 404)
    try:
        return jsonify({'status': 'success', 'data': get_weather_data(city)})
    except Exception:
        logger.exception("Weather lookup failed for %s", city)
        return error('Weather data is not available right now.', 502)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    # Debug mode only when explicitly enabled (never in production)
    app.run(debug=os.getenv('FLASK_DEBUG') == '1')
