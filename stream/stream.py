import streamlit as st
import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
import time
from datetime import datetime
import os

# Create a directory for saving recordings if it doesn't exist
if not os.path.exists("recordings"):
    os.makedirs("recordings")

# Initialize session state variables
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = []
if 'sample_rate' not in st.session_state:
    st.session_state.sample_rate = 44100  # CD quality audio
if 'recordings' not in st.session_state:
    st.session_state.recordings = []

def record_audio():
    while st.session_state.recording:
        # Record audio in chunks
        audio_chunk = sd.rec(
            frames=1024,
            samplerate=st.session_state.sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()  # Wait until recording is finished
        st.session_state.audio_data.extend(audio_chunk)

def save_recording():
    if len(st.session_state.audio_data) > 0:
        # Convert to numpy array and scale to int16 range
        audio_data = np.array(st.session_state.audio_data)
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recordings/recording_{timestamp}.wav"
        
        # Save the WAV file
        wavfile.write(filename, st.session_state.sample_rate, audio_data)
        
        # Add to recordings list
        recording_info = {
            'filename': filename,
            'timestamp': timestamp,
            'duration': len(audio_data) / st.session_state.sample_rate
        }
        st.session_state.recordings.append(recording_info)
        
        # Clear the audio data
        st.session_state.audio_data = []
        return filename
    return None

def toggle_recording():
    st.session_state.recording = not st.session_state.recording
    if st.session_state.recording:
        # Start new recording
        st.session_state.audio_data = []
    else:
        # Stop and save recording
        filename = save_recording()
        if filename:
            st.success(f"Recording saved as {filename}")

# Title of the app
st.title("Audio Recording Application")

# Record button
if st.button("Record" if not st.session_state.recording else "Stop Recording"):
    toggle_recording()

# Display recording status
if st.session_state.recording:
    st.write("🔴 Recording in progress...")
    record_audio()
else:
    st.write("⚪ Recording stopped")

# Display recording history
if st.session_state.recordings:
    st.subheader("Recording History")
    for i, recording in enumerate(st.session_state.recordings, 1):
        st.write(f"Recording {i}:")
        st.write(f"Filename: {recording['filename']}")
        st.write(f"Timestamp: {recording['timestamp']}")
        st.write(f"Duration: {recording['duration']:.2f} seconds")
        
        # Add play button for the recording
        audio_file = open(recording['filename'], 'rb')
        st.audio(audio_file)
        st.write("---")