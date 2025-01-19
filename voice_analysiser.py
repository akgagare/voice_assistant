import numpy as np
import librosa
import sounddevice as sd
from scipy.stats import zscore

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
        
    def record_audio(self, duration=5):
        """Record audio for specified duration"""
        print("Recording...")
        audio = sd.rec(int(duration * self.sample_rate), 
                      samplerate=self.sample_rate, 
                      channels=1)
        sd.wait()
        return audio.flatten()
    
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
        # Detect silence using root mean square energy
        rms = librosa.feature.rms(y=audio)[0]
        silence_threshold = np.mean(rms) * 0.5
        pauses = np.sum(rms < silence_threshold) / len(rms)
        
        # Score based on appropriate pause ratio
        pause_score = min(100, max(0, 100 - abs(pauses - 0.2) * 200))
        return pause_score
    
    def analyze_confidence(self, audio):
        """Analyze speaking confidence"""
        # Use amplitude variation and speech rate as confidence indicators
        rms = librosa.feature.rms(y=audio)[0]
        confidence_score = min(100, max(0, np.mean(rms) * 200 + 50))
        return confidence_score
    
    def analyze_voice(self, audio=None, duration=5):
        """Analyze voice and return ratings"""
        if audio is None:
            audio = self.record_audio(duration)
            
        # Normalize audio
        audio = audio / np.max(np.abs(audio))
        
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
            'overall_score': overall_score
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