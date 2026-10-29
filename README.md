# WindChime – Weather-Inspired Music Generator

WindChime composes short pieces of music from the current weather in Swedish cities. It fetches a live forecast from SMHI (the Swedish Meteorological and Hydrological Institute) and uses a **genetic algorithm** to evolve a melody whose notes, tempo, rhythm and harmony follow temperature, wind, humidity, cloudiness and rain. The result is a MIDI file and, with FluidSynth installed, a WAV file you can play in the browser.

> Team project (Group 19) built in February–March 2025 ([original team repository with the full history](https://github.com/AronKG/create_music_ethic)). Updated in October 2026 with tests, CI and improved input handling.

## How it works

```
City ──► SMHI forecast API ──► weather features ──► genetic algorithm ──► MIDI ──► FluidSynth ──► WAV
        (frontend/scripts)    temperature, wind,    (GenerateMusic.py)   3 tracks   (optional)
                              humidity, cloudiness,
                              precipitation (mm/h)
```

### Weather → music

| Weather | Musical effect |
|---|---|
| Temperature | Target pitch for the melody and the harmony's base note; warmer weather also raises the tempo |
| Wind speed | Wider note range, longer melody, faster tempo, extra drum sounds above 5 m/s |
| Humidity | Major chord (< 50 %) or minor chord (≥ 50 %); extra notes when very humid |
| Cloudiness | Clear skies allow a wider note range |
| Precipitation | Extra percussion for light (> 1 mm/h) and heavy (> 3 mm/h) rain |

### Genetic algorithm

1. **Population:** 20 random melodies (notes from middle C upwards) with a weather-based tempo.
2. **Fitness:** rewards notes close to a temperature-based target pitch, notes from the target chord, starting and ending on the target, and tempos near 120 BPM; penalises large jumps (> 12 semitones).
3. **Selection:** the best half survives each generation.
4. **Crossover:** two parents are cut at a random point and joined; the tempo is averaged.
5. **Mutation:** 20 % of children get one random note changed and may change tempo slightly.
6. After 30 generations, the best melody is written as a MIDI file with three tracks (melody, percussion, harmony) at the evolved tempo.

## My contributions

- Implemented the first version of the **genetic algorithm** (population, crossover, mutation, selection)
- Improved the **fitness function** based on a music article (target pitch, chord tones, interval penalties)
- Connected the **SMHI weather API** to the web app and added more weather features
- Added **rhythm and harmony** generation based on the weather
- Added Kiruna as a city; README and setup instructions for macOS
- 2026: tests, CI, input validation and robustness improvements in this repository

## Tech stack

| Area | Technology |
|---|---|
| Backend | Python 3, Flask |
| Music | mido (MIDI), midi2audio + FluidSynth (WAV) |
| Weather | SMHI open data API (via a bundled copy of `smhi-pkg`) |
| Frontend | HTML, CSS, JavaScript |
| Tests / CI | pytest, GitHub Actions |

## Getting started

### 1. Install

```bash
cd frontend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Audio playback (optional)

Without FluidSynth the app still generates MIDI files. For WAV audio in the browser, install FluidSynth and the FluidR3_GM soundfont:

- **Ubuntu:** `sudo apt-get install fluidsynth fluid-soundfont-gm` and set `SOUNDFONT_PATH=/usr/share/sounds/sf2/FluidR3_GM.sf2`
- **macOS:** `brew install fluid-synth`
- **Windows:** `choco install fluidsynth`

On macOS and Windows, download the soundfont from https://member.keymusician.com/Member/FluidR3_GM/index.html and place `FluidR3_GM.sf2` in `frontend/soundfonts/` (the default location), or set `SOUNDFONT_PATH`.

### 3. Run

```bash
cp .env.example .env    # optional settings
python app.py           # http://localhost:5000
```

### Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `SOUNDFONT_PATH` | Path to the `.sf2` soundfont used for WAV conversion | `frontend/soundfonts/FluidR3_GM.sf2` |
| `FLASK_DEBUG` | Set to `1` to enable Flask debug mode during development | off |

## Tests

```bash
cd frontend
pip install -r requirements-dev.txt
pytest
```

- `tests/test_generate_music.py`: fitness, crossover, mutation, weather-to-music rules, note and tempo limits, and valid MIDI output for mild, stormy and hot weather
- `tests/test_app.py`: the Flask routes with sample weather data (no network needed): music generation, input validation, weather service errors and file access

GitHub Actions runs the tests on every push and pull request.

## Project structure

```
frontend/
├── app.py                 # Flask routes
├── GenerateMusic.py       # genetic algorithm and MIDI/WAV output
├── scripts/weather_data.py# city coordinates and SMHI forecast
├── smhi/                  # bundled smhi-pkg 1.0.19 (MIT, see smhi/LICENSE)
├── templates/, static/    # web page
└── tests/                 # pytest tests
```

## Third-party code

`frontend/smhi/` is a copy of [smhi-pkg](https://github.com/joysoftware/pypi_smhi) 1.0.19 by Tomas Hellström, MIT License (see `frontend/smhi/LICENSE`), with minor spelling edits.

## Team

- Aron Kesete
- Isac Gustafsson
- Parna Saeidpour
- Sami Noroozi
