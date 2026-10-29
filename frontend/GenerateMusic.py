import logging
import os
import random
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

logger = logging.getLogger(__name__)

# MIDI notes must be between 0 and 127; melodies start at middle C (60)
BASE_NOTE = 60
MAX_NOTE = 127
MIN_TEMPO = 60
MAX_TEMPO = 200

def fitness(melody_data, weather_data):
    #60 (Middle C) is our base
    melody, tempo = melody_data
    target = max(40, 60 + weather_data["temperature"]) 
    avg_note = sum(melody) / len(melody)
    base_fitness = 100 - abs(avg_note - target)*2
    tempo_penalty = abs(tempo - 120) / 2 

    bonus_start_end = 0
    if melody[0] == target:
        bonus_start_end += 50
    if melody[-1] == target:
        bonus_start_end += 50

    penalty_intervals = 0
    for i in range(1, len(melody)):
        interval = abs(melody[i] - melody[i - 1])
        if interval > 12:
            penalty_intervals += 2 * (interval - 12)

    chord = {target, target + 4, target + 7}
    chord_bonus = 0
    if len(melody) > 0:
        for note in melody:
            if note in chord:
                chord_bonus += 30  
            else:
                chord_bonus -= 60  
        chord_bonus /= len(melody)

    fitness_val = base_fitness + bonus_start_end - penalty_intervals + chord_bonus-tempo_penalty
    return fitness_val

def crossover(parent1, parent2):
    melody1, tempo1 = parent1
    melody2, tempo2 = parent2
    point = random.randint(1, len(melody1) - 1)
    new_tempo = (tempo1 + tempo2) // 2
    return melody1[:point] + melody2[point:],new_tempo

def mutate(melody_data, note_range):
    melody, tempo = melody_data 
    idx = random.randint(0, len(melody) - 1)
    melody[idx] = random.randint(BASE_NOTE, BASE_NOTE + note_range)

    if random.random() < 0.5:
        tempo += random.randint(-5, 5)
        tempo = max(MIN_TEMPO, min(MAX_TEMPO, tempo))
    
    return melody,tempo

def generate_harmony_based_on_weather(weather_data):

    humidity = weather_data["humidity"]
    base_note = 60 + (weather_data["temperature"] // 2)  
    chord_type = "major" if humidity < 50 else "minor"  
    harmony = []

    if chord_type == "major":
       
        harmony = [base_note, base_note + 4, base_note + 7]  
    elif chord_type == "minor":
       
        harmony = [base_note, base_note + 3, base_note + 7]

    if humidity > 75:
      
        harmony.extend([int(base_note + 10)])  

    return harmony

def generate_rhythm_based_on_weather(weather_data):
    wind_speed = weather_data["wind_speed"]
    temperature = weather_data["temperature"]
    humidity = weather_data["humidity"]
    # Precipitation amount in mm/h (0 when it is not raining)
    rain = weather_data.get("precipitation_mm", 0)
    base_rhythm = []
    
    if wind_speed > 5:
        base_rhythm = [36, 38, 42, 46, 48]  
    else:
        base_rhythm = [36, 38, 42,44]  

    if temperature > 20:
        base_rhythm += [50, 52]  
    
    if humidity > 70:
        base_rhythm += [40, 45, 47] 

    if rain > 3:  
        base_rhythm += [35, 43, 49]  
    elif rain > 1:  
        base_rhythm += [36, 38] 
    
    rhythm_pattern =  [int(note) for note in base_rhythm] 
    
    return rhythm_pattern


def melody_settings(weather_data):
    """Note range, melody length and start tempo derived from the weather."""
    note_range = 10 + int(weather_data["wind_speed"]*4+int(weather_data["humidity"])/8)
    note_range += int((100 - weather_data["cloudiness"]) / 10)
    # Keep every note inside the MIDI range (strong wind made notes above 127)
    note_range = min(note_range, MAX_NOTE - BASE_NOTE)
    melody_length = int(weather_data["wind_speed"])+20
    tempo = max(60, min(180, 100 + int(weather_data["wind_speed"]*8) + int(weather_data["humidity"]/3)))
    tempo += max(8, 12 + int(weather_data["temperature"] * 5))
    tempo = max(MIN_TEMPO, min(MAX_TEMPO, tempo))
    return note_range, melody_length, tempo


def evolve_melody(weather_data, generations=30, population_size=20):
    """Run the genetic algorithm and return the best (melody, tempo)."""
    note_range, melody_length, tempo = melody_settings(weather_data)


    population = [
        ([random.randint(BASE_NOTE, BASE_NOTE + note_range) for _ in range(melody_length)],tempo)
        for _ in range(population_size)
    ]
    
    best_melody = None
    best_fit = float('-inf')
    
    for gen in range(generations):
        scored_population = [(fitness(individual, weather_data),individual) for individual in population]
        scored_population.sort(reverse=True, key=lambda x: x[0])
        
        best_gen_fit, best_gen_melody = scored_population[0]
        if best_gen_fit > best_fit:
            best_fit = best_gen_fit
            best_melody = best_gen_melody
        
        logger.debug("Generation %d: best fitness = %.2f", gen + 1, best_gen_fit)
        
        survivors = [individual for score, individual in scored_population[:population_size // 2]]
        
        new_population = survivors.copy()
        while len(new_population) < population_size:
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            child = crossover(parent1, parent2)
            if random.random() < 0.2:
                child = mutate(child, note_range)
            new_population.append(child)
        
        population = new_population

    return best_melody


def build_midi(melody, tempo, weather_data):
    """Melody, percussion and harmony tracks as a MIDI file."""
    mid = MidiFile()

    track1 = MidiTrack()
    # Use the evolved tempo for playback
    track1.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo), time=0))
    track1.append(Message('program_change', program=2, time=0))  # Piano
    for note in melody:
        note = int(note)
        track1.append(Message('note_on', note=note, velocity=100, time=0))
        track1.append(Message('note_off', note=note, velocity=64, time=480))

    track2 = MidiTrack()
    track2.append(Message('program_change', program=9, time=0))  # Percussion
    rhythm = generate_rhythm_based_on_weather(weather_data)
    for note in rhythm:
        note = int(note)
        track2.append(Message('note_on', note=note, velocity=100, time=0))
        track2.append(Message('note_off', note=note, velocity=64, time=480))

    track3 = MidiTrack()
    track3.append(Message('program_change', program=0, time=0))  # Acoustic piano for harmony
    harmony = generate_harmony_based_on_weather(weather_data)
    for note in harmony:
        note = int(note)
        track3.append(Message('note_on', note=note, velocity=100, time=0))
        track3.append(Message('note_off', note=note, velocity=64, time=480))

    # Add tracks to the MIDI file
    mid.tracks.append(track1)
    mid.tracks.append(track2)
    mid.tracks.append(track3)
    return mid


def generate_music_genetic(weather_data, file_name, output_dir, soundfont_path=None, generations=30, population_size=20):
    """
    Generate music for the weather and save <file_name>.mid in output_dir.
    A .wav file is also created when FluidSynth and the soundfont are available.
    Returns the paths of the created files.
    """
    melody, tempo = evolve_melody(weather_data, generations, population_size)
    mid = build_midi(melody, tempo, weather_data)

    os.makedirs(output_dir, exist_ok=True)
    midi_path = os.path.join(output_dir, file_name + '.mid')
    mid.save(midi_path)
    files = {"midi": midi_path, "wav": None}

    # Convert MIDI to WAV
    if soundfont_path and os.path.exists(soundfont_path):
        try:
            from midi2audio import FluidSynth
            wav_path = os.path.join(output_dir, file_name + '.wav')
            FluidSynth(soundfont_path).midi_to_audio(midi_path, wav_path)
            if os.path.exists(wav_path):
                files["wav"] = wav_path
        except Exception:
            logger.exception("WAV conversion failed; returning MIDI only")
    else:
        logger.warning("Soundfont not found (%s); returning MIDI only", soundfont_path)
    return files
