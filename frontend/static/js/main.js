// Music player state
let audioContext = null;
let currentTrack = null;
let isPlaying = false;
let startTime = 0;
let currentTime = 0;
let duration = 180; // Default duration in seconds

// Enhanced music wave animation
function updateMusicWaves(isPlaying) {
    const waves = document.querySelectorAll('.wave');
    waves.forEach((wave, index) => {
        if (isPlaying) {
            wave.style.animationPlayState = 'running';
            wave.style.animationDuration = `${1 + (index * 0.2)}s`;
        } else {
            wave.style.animationPlayState = 'paused';
        }
    });
}

// Helper function to show/hide elements
function toggleElement(element, show) {
    if (show) {
        element.classList.remove('hidden');
    } else {
        element.classList.add('hidden');
    }
}

// Helper function to format time
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Helper function to format weather data
function formatWeatherData(data) {
    return `
        <div class="weather-data">
            <div class="weather-item">
                <span class="label">Temperature</span>
                <span class="value">${data.temperature}°C</span>
            </div>
            <div class="weather-item">
                <span class="label">Wind Speed</span>
                <span class="value">${data.windSpeed} m/s</span>
            </div>
            <div class="weather-item">
                <span class="label">Precipitation</span>
                <span class="value">${data.precipitation} mm</span>
            </div>
            <div class="weather-item">
                <span class="label">Sunshine</span>
                <span class="value">${data.sunshine} hours</span>
            </div>
        </div>
    `;
}

// Function to handle MIDI file download
function downloadMIDI(midiData, filename) {
    const blob = new Blob([midiData], { type: 'audio/midi' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename || 'weather-music.mid';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Function to update progress bar
function updateProgress() {
    if (!isPlaying) return;
    
    const progressBar = document.getElementById('progress');
    const currentTimeEl = document.getElementById('currentTime');
    const durationEl = document.getElementById('duration');
    
    currentTime = (Date.now() - startTime) / 1000;
    const progress = (currentTime / duration) * 100;
    
    progressBar.style.width = `${Math.min(progress, 100)}%`;
    currentTimeEl.textContent = formatTime(currentTime);
    durationEl.textContent = formatTime(duration);
    
    if (currentTime < duration) {
        requestAnimationFrame(updateProgress);
    } else {
        stopPlayback();
    }
}

// Function to start playback
function startPlayback() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    isPlaying = true;
    startTime = Date.now() - (currentTime * 1000);
    updateProgress();
    updateVisualization();
    updateMusicWaves(true);
}

// Function to stop playback
function stopPlayback() {
    isPlaying = false;
    updateMusicWaves(false);
    if (currentTime >= duration) {
        currentTime = 0;
        const progressBar = document.getElementById('progress');
        progressBar.style.width = '0%';
    }
}

// Function to update visualization
function updateVisualization() {
    if (!isPlaying) return;
    
    const visualizer = document.getElementById('visualizer');
    const bars = visualizer.children;
    
    // Create a smooth transition between random heights
    for (let bar of bars) {
        const currentHeight = parseFloat(bar.style.height) || 0;
        const targetHeight = Math.random() * 100;
        const newHeight = currentHeight + (targetHeight - currentHeight) * 0.1;
        bar.style.height = `${newHeight}%`;
    }
    
    requestAnimationFrame(updateVisualization);
}

// Initialize player controls
document.addEventListener('DOMContentLoaded', () => {
    const playBtn = document.getElementById('playBtn');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const progressBar = document.querySelector('.progress-bar');
    
    if (playBtn) {
        playBtn.addEventListener('click', () => {
            if (isPlaying) {
                stopPlayback();
                playBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="5 3 19 12 5 21 5 3"/>
                    </svg>
                `;
            } else {
                startPlayback();
                playBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="6" y="4" width="4" height="16"/>
                        <rect x="14" y="4" width="4" height="16"/>
                    </svg>
                `;
            }
        });
    }
    
    if (progressBar) {
        progressBar.addEventListener('click', (e) => {
            const rect = progressBar.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const percentage = x / rect.width;
            currentTime = percentage * duration;
            startTime = Date.now() - (currentTime * 1000);
            const progress = document.getElementById('progress');
            progress.style.width = `${percentage * 100}%`;
        });
    }
    
    // Initialize visualization bars
    const visualizer = document.getElementById('visualizer');
    if (visualizer) {
        // Remove existing bars if any
        visualizer.innerHTML = '';
        // Create new bars
        for (let i = 0; i < 50; i++) {
            const bar = document.createElement('div');
            bar.className = 'bar';
            bar.style.height = '0%';
            visualizer.appendChild(bar);
        }
    }
}); 