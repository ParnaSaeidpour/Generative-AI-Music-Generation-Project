from flask import Flask, render_template, request, jsonify, send_file, url_for
from dotenv import load_dotenv
import os
from datetime import datetime
import sys
from scripts.weather_data import get_weather_data_by_city

# Add the Simplegeneticalgorithm directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Simplegeneticalgorithm'))
from GenerateMusic import generate_music_genetic

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Create static/generated directory if it doesn't exist
GENERATED_DIR = os.path.join(os.path.dirname(__file__), 'static', 'generated')
os.makedirs(GENERATED_DIR, exist_ok=True)

# List of available cities (can be expanded later)
CITIES = [
    "Stockholm",
    "Gothenburg",
    "Malmö",
    "Uppsala",
    "Jönköping",
    "Kiruna"
]

# Simulated weather data (will be replaced with actual API calls)
def get_weather_data(city):
    data = get_weather_data_by_city(city)

    print(f"Got weather data for {city}: {data}")
    return {
        'temperature': data['temperature'],
        'wind_speed': data['wind_speed'],
        'rain': data['precipitation'] > 0,
        'cloudiness': data['cloudiness'],
        'humidity': data['humidity']   
    }

@app.route('/')
def index():
    return render_template('index.html', cities=CITIES)

@app.route('/generate', methods=['POST'])
def generate_music():
    city = request.form.get('city')
    
    filename = city + '_' + datetime.now().strftime('%Y%m%d%H')

    #If file already exists, return the existing file
    # if os.path.exists(os.path.join(GENERATED_DIR, filename + '.mid')):
    #     return jsonify({
    #         'status': 'success',
    #         'message': 'Generated music for ' + city,
    #         'midi_url': url_for('static', filename='generated/' + filename + '.mid'),
    #         'wav_url': url_for('static', filename='generated/' + filename + '.wav')
    #     })

    
    if not city:
        return jsonify({
            'status': 'error',
            'message': 'City is required'
        }), 400
    
    try:
        # Get weather data
        weather_data = get_weather_data(city)
        
        # Generate music
        generate_music_genetic(weather_data, filename)
        
        return jsonify({
            'status': 'success',
            'message': f'Generated music for {city} (Temperature: {weather_data["temperature"]}°C, Wind: {weather_data["wind_speed"]} m/s, Rain: {"Yes" if weather_data["rain"] else "No"})',
            'weather': weather_data,
            'midi_url': url_for('static', filename='generated/' + filename + '.mid'),
            'wav_url': url_for('static', filename='generated/' + filename + '.wav')
        })
    except Exception as e:
        print(f"Error generating music: {str(e)}")  # Debug logging
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/play/<filename>')
def play_audio(filename):
    try:
        return send_file(
            os.path.join(GENERATED_DIR, filename),
            mimetype='audio/wav' if filename.endswith('.wav') else 'audio/midi'
        )
    except Exception as e:
        return str(e), 404

@app.route('/weather/<city>')
def get_weather(city):
    try:
        weather_data = get_weather_data(city)
        return jsonify({
            'status': 'success',
            'data': weather_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/download/<city>')
def download_midi(city):
    # This will be implemented when the backend is ready
    # For now, return a dummy response
    return jsonify({
        'status': 'error',
        'message': 'MIDI download functionality will be implemented soon'
    }), 501

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True) 