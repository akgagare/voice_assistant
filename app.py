import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from voice_analysiser import VoiceRatingAnalyzer
import time

# Initialize the analyzer
analyzer = VoiceRatingAnalyzer()

# Initialize session state for recordings
if 'recordings' not in st.session_state:
    st.session_state.recordings = []

st.title("Voice Recording and Analysis")

def record_audio(duration=5, sample_rate=44100):
    """Record audio for a specified duration"""
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.float32
    )
    st.info("Recording...")
    sd.wait()  # Wait until the recording is finished
    st.success("Recording finished!")
    return recording

if st.button("Record (5 seconds)"):
    # Record audio
    audio_data = record_audio()
    
    # Save the recording temporarily
    wavfile.write("temp.wav", 44100, audio_data)
    
    # Analyze the voice
    results = analyzer.analyze_voice()
    
    # Display results
    st.subheader("Analysis Results")
    st.write(f"Overall Score: {results['overall_score']:.1f}/100")
    
    st.write("Individual Parameters:")
    for param, score in results['parameters'].items():
        st.write(f"{param.title()}: {score:.1f}/100")
    
    st.write("\nFeedback:")
    for feedback in analyzer.get_feedback():
        st.write(f"- {feedback}")
    
    # Play the recording
    st.audio("temp.wav")