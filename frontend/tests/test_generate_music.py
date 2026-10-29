import random

import pytest
from mido import MidiFile, tempo2bpm

import GenerateMusic as gm

MILD = {"temperature": 8, "wind_speed": 3.0, "humidity": 70, "cloudiness": 40, "precipitation_mm": 0.0}
STORM = {"temperature": 2, "wind_speed": 25.0, "humidity": 100, "cloudiness": 0, "precipitation_mm": 5.0}
HEAT = {"temperature": 35, "wind_speed": 10.0, "humidity": 90, "cloudiness": 0, "precipitation_mm": 0.0}


def test_strong_wind_keeps_notes_inside_midi_range():
    note_range, _, _ = gm.melody_settings(STORM)
    assert gm.BASE_NOTE + note_range <= gm.MAX_NOTE


def test_tempo_stays_between_limits():
    for weather in (MILD, STORM, HEAT):
        _, _, tempo = gm.melody_settings(weather)
        assert gm.MIN_TEMPO <= tempo <= gm.MAX_TEMPO


def test_fitness_prefers_notes_close_to_the_target_chord():
    target = 60 + MILD["temperature"]
    on_chord = ([target, target + 4, target + 7] * 7, 120)
    far_away = ([120] * 21, 120)
    assert gm.fitness(on_chord, MILD) > gm.fitness(far_away, MILD)


def test_crossover_keeps_length_and_averages_tempo():
    random.seed(1)
    child, tempo = gm.crossover(([60] * 20, 100), ([70] * 20, 140))
    assert len(child) == 20
    assert tempo == 120
    assert set(child) <= {60, 70}


def test_mutation_stays_in_range():
    random.seed(2)
    for _ in range(200):
        melody, tempo = gm.mutate(([60] * 20, 120), note_range=10)
        assert all(60 <= note <= 70 for note in melody)
        assert gm.MIN_TEMPO <= tempo <= gm.MAX_TEMPO


def test_rain_changes_the_rhythm():
    dry = gm.generate_rhythm_based_on_weather({**MILD, "precipitation_mm": 0.0})
    heavy = gm.generate_rhythm_based_on_weather({**MILD, "precipitation_mm": 5.0})
    light = gm.generate_rhythm_based_on_weather({**MILD, "precipitation_mm": 2.0})
    assert [35, 43, 49] == heavy[-3:]
    assert [36, 38] == light[-2:]
    assert len(dry) < len(light) < len(heavy)


def test_humidity_switches_between_major_and_minor_harmony():
    major = gm.generate_harmony_based_on_weather({**MILD, "humidity": 40})
    minor = gm.generate_harmony_based_on_weather({**MILD, "humidity": 60})
    assert major[1] - major[0] == 4
    assert minor[1] - minor[0] == 3


def test_evolution_improves_on_a_random_start():
    random.seed(3)
    note_range, length, tempo = gm.melody_settings(MILD)
    start = [([random.randint(60, 60 + note_range) for _ in range(length)], tempo) for _ in range(20)]
    best_start = max(gm.fitness(m, MILD) for m in start)

    random.seed(3)
    best = gm.evolve_melody(MILD, generations=30, population_size=20)
    assert gm.fitness(best, MILD) >= best_start


@pytest.mark.parametrize("weather", [MILD, STORM, HEAT])
def test_generates_a_valid_midi_file(tmp_path, weather):
    random.seed(4)
    files = gm.generate_music_genetic(weather, "song", str(tmp_path), soundfont_path=None, generations=5)

    assert files["wav"] is None  # no soundfont in the test environment
    midi = MidiFile(files["midi"])
    assert len(midi.tracks) == 3
    tempo_messages = [m for m in midi.tracks[0] if m.type == "set_tempo"]
    assert len(tempo_messages) == 1
    assert gm.MIN_TEMPO <= round(tempo2bpm(tempo_messages[0].tempo)) <= gm.MAX_TEMPO
    notes = [m.note for track in midi.tracks for m in track if m.type == "note_on"]
    assert notes and all(0 <= n <= 127 for n in notes)
