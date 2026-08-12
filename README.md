# Weather Music Generator - WindChime

Welcome to WindChime, the music generator that creates music based on the weather in certain Swedish cities using a genetic algorithm.

## Setup Instructions
1. cd to the frontend folder
```bash
cd frontend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Additional Setup for Audio Playback
1. macOS: 
```bash 
brew install fluid-synth 
```

Download the soundfile from https://member.keymusician.com/Member/FluidR3_GM/index.html

```
unzip ~/Downloads/FluidR3_GM.zip -d ~/Downloads/FluidR3_GM
mv ~/Downloads/FluidR3_GM/FluidR3_GM.sf2 ./soundfonts/FluidR3_GM.sf2
```


2. Windows: (Requires Chocolatey)
```bash
choco install fluidsynth
```

Download the soundfile from https://member.keymusician.com/Member/FluidR3_GM/index.html and move it to the soundfonts folder, found in the frontend folder. If no soundfonts folder exists, create one.

3. ubuntu:
```bash
sudo apt-get install fluidsynth
sudo apt-get install fluid-soundfont-gm

```





4. Run the development server:
```bash
python app.py
```


The application will be available at `http://localhost:5000`



## Team

- Aron Kesete
- Isac Gustafsson
- Parna Saeidpour
- Sami Noroozi