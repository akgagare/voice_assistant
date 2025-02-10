import streamlit as st
import numpy as np
import librosa
import sounddevice as sd
from scipy.stats import zscore
import scipy.io.wavfile as wavfile
import os
from datetime import datetime

class VoiceRatingAnalyzer:
    def __init__(self):
        self.sample_rate = 22050
        self.parameters = {
            'pitch': 0.0,
            'tone': 0.0,
            'frequency_variation': 0.0,
            'pauses': 0.0,
            'confidence': 0.0
        }
        
        # Create recordings directory if it doesn't exist
        self.recordings_dir = "recordings"
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)

    def record_audio(self, duration=5):
        """Record audio for specified duration"""
        print("Recording...")
        audio = sd.rec(int(duration * self.sample_rate),
                      samplerate=self.sample_rate,
                      channels=1)
        sd.wait()
        return audio.flatten()

    def save_wav(self, audio, filename=None):
        """Save audio as WAV file"""
        if filename is None:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
        
        # Full path for the file
        filepath = os.path.join(self.recordings_dir, filename)
        
        # Ensure audio is normalized and converted to the right format
        audio_normalized = audio / np.max(np.abs(audio))
        audio_int16 = (audio_normalized * 32767).astype(np.int16)
        
        # Save the WAV file
        wavfile.write(filepath, self.sample_rate, audio_int16)
        return filepath

    def analyze_pitch(self, audio):
        """Analyze pitch characteristics"""
        pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sample_rate)
        pitch_mean = np.mean(pitches[pitches > 0])
        pitch_std = np.std(pitches[pitches > 0])
        
        # Score based on pitch stability and range
        pitch_score = min(100, max(0, 100 - (pitch_std * 10)))
        return pitch_score

    def analyze_tone(self, audio):
        """Analyze tone quality"""
        stft = librosa.stft(audio)
        db = librosa.amplitude_to_db(abs(stft))
        
        # Calculate tone score based on spectral characteristics
        tone_score = min(100, max(0, np.mean(db) + 100))
        return tone_score

    def analyze_frequency_variation(self, audio):
        """Analyze frequency variation"""
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
        variation_score = min(100, max(0, 100 - (np.std(spectral_centroids) * 0.1)))
        return variation_score

    def analyze_pauses(self, audio):
        """Analyze speech pauses"""
        rms = librosa.feature.rms(y=audio)[0]
        silence_threshold = np.mean(rms) * 0.5
        pauses = np.sum(rms < silence_threshold) / len(rms)
        
        # Score based on appropriate pause ratio
        pause_score = min(100, max(0, 100 - abs(pauses - 0.2) * 200))
        return pause_score

    def analyze_confidence(self, audio):
        """Analyze speaking confidence"""
        rms = librosa.feature.rms(y=audio)[0]
        confidence_score = min(100, max(0, np.mean(rms) * 200 + 50))
        return confidence_score

    def analyze_voice(self, audio=None, duration=5):
        """Analyze voice and return ratings"""
        if audio is None:
            audio = self.record_audio(duration)
        
        # Normalize audio
        audio = audio / np.max(np.abs(audio))
        
        # Save the WAV file
        wav_path = self.save_wav(audio)
        
        # Analyze individual parameters
        self.parameters['pitch'] = self.analyze_pitch(audio)
        self.parameters['tone'] = self.analyze_tone(audio)
        self.parameters['frequency_variation'] = self.analyze_frequency_variation(audio)
        self.parameters['pauses'] = self.analyze_pauses(audio)
        self.parameters['confidence'] = self.analyze_confidence(audio)
        
        # Calculate overall score
        overall_score = np.mean(list(self.parameters.values()))
        
        return {
            'parameters': self.parameters,
            'overall_score': overall_score,
            'wav_path': wav_path
        }

    def get_feedback(self):
        """Generate feedback based on ratings"""
        feedback = []
        
        for param, score in self.parameters.items():
            if score >= 80:
                feedback.append(f"Excellent {param}: {score:.1f}/100")
            elif score >= 60:
                feedback.append(f"Good {param}: {score:.1f}/100")
            else:
                feedback.append(f"Could improve {param}: {score:.1f}/100")
                
        return feedback

# Streamlit app
st.title("Voice Recording and Analysis")

if st.button("Record (5 seconds)"):
    # Create analyzer instance
    analyzer = VoiceRatingAnalyzer()
    
    # Record and analyze voice
    with st.spinner("Recording..."):
        results = analyzer.analyze_voice()
    
    # Display results
    st.success(f"Recording saved as: {results['wav_path']}")
    
    st.subheader("Analysis Results")
    st.write(f"Overall Score: {results['overall_score']:.1f}/100")
    
    st.write("Individual Parameters:")
    for param, score in results['parameters'].items():
        st.write(f"{param.title()}: {score:.1f}/100")
    
    st.write("\nFeedback:")
    for feedback in analyzer.get_feedback():
        st.write(f"- {feedback}")
    
    # Play the recording
    with open(results['wav_path'], 'rb') as audio_file:
        st.audio(audio_file)