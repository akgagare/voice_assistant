import numpy as np
import librosa
import sounddevice as sd
from scipy.stats import zscore
from typing import Dict, List, Optional, Tuple, Union

class VoiceRatingAnalyzer:
    """
    A class for analyzing voice recordings and providing detailed feedback on various parameters.
    
    Parameters:
        sample_rate (int): The sampling rate for audio recording (default: 22050 Hz)
        pitch_weight (float): Weight for pitch scoring (default: 1.0)
        tone_weight (float): Weight for tone scoring (default: 1.0)
        variation_weight (float): Weight for frequency variation scoring (default: 0.8)
        pause_weight (float): Weight for pause analysis scoring (default: 0.7)
        confidence_weight (float): Weight for confidence scoring (default: 1.0)
    """
    
    def __init__(
        self,
        sample_rate: int = 22050,
        pitch_weight: float = 1.0,
        tone_weight: float = 1.0,
        variation_weight: float = 0.8,
        pause_weight: float = 0.7,
        confidence_weight: float = 1.0
    ):
        self.sample_rate = sample_rate
        self.weights = {
            'pitch': pitch_weight,
            'tone': tone_weight,
            'frequency_variation': variation_weight,
            'pauses': pause_weight,
            'confidence': confidence_weight
        }
        self.parameters = {
            'pitch': 0.0,
            'tone': 0.0,
            'frequency_variation': 0.0,
            'pauses': 0.0,
            'confidence': 0.0
        }
        self._last_audio = None
        
    def record_audio(self, duration: float = 5) -> np.ndarray:
        """
        Record audio for the specified duration.
        
        Args:
            duration (float): Recording duration in seconds
            
        Returns:
            np.ndarray: Recorded audio data
        """
        print(f"Recording for {duration} seconds...")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1
        )
        sd.wait()
        print("Recording complete!")
        return audio.flatten()
    
    def analyze_pitch(self, audio: np.ndarray) -> float:
        """
        Analyze pitch characteristics of the audio.
        
        Args:
            audio (np.ndarray): Audio data
            
        Returns:
            float: Pitch score (0-100)
        """
        pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sample_rate)
        pitch_data = pitches[pitches > 0]
        
        if len(pitch_data) == 0:
            return 0.0
            
        pitch_mean = np.mean(pitch_data)
        pitch_std = np.std(pitch_data)
        
        # Score based on pitch stability and range
        stability_score = 100 - min(100, (pitch_std / pitch_mean) * 100)
        range_score = 100 - min(100, abs(pitch_mean - 200) / 2)
        
        return np.mean([stability_score, range_score])
    
    def analyze_tone(self, audio: np.ndarray) -> float:
        """
        Analyze tone quality using spectral characteristics.
        
        Args:
            audio (np.ndarray): Audio data
            
        Returns:
            float: Tone score (0-100)
        """
        stft = librosa.stft(audio)
        db = librosa.amplitude_to_db(abs(stft))
        
        # Analyze harmonic content
        harmonic, percussive = librosa.decompose.hpss(stft)
        harmonic_ratio = np.sum(abs(harmonic)) / (np.sum(abs(percussive)) + 1e-6)
        
        # Calculate tone score based on spectral characteristics and harmonics
        spectral_score = min(100, max(0, np.mean(db) + 100))
        harmonic_score = min(100, harmonic_ratio * 50)
        
        return np.mean([spectral_score, harmonic_score])
    
    def analyze_frequency_variation(self, audio: np.ndarray) -> float:
        """
        Analyze frequency variation and speaking dynamics.
        
        Args:
            audio (np.ndarray): Audio data
            
        Returns:
            float: Frequency variation score (0-100)
        """
        # Analyze spectral contrast
        contrast = librosa.feature.spectral_contrast(y=audio, sr=self.sample_rate)
        contrast_score = min(100, np.mean(contrast) * 20 + 50)
        
        # Analyze spectral centroid variation
        centroids = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
        centroid_var = np.std(centroids)
        variation_score = min(100, max(0, 100 - (centroid_var * 0.1)))
        
        return np.mean([contrast_score, variation_score])
    
    def analyze_pauses(self, audio: np.ndarray) -> float:
        """
        Analyze speech pauses and rhythm.
        
        Args:
            audio (np.ndarray): Audio data
            
        Returns:
            float: Pause score (0-100)
        """
        # Detect silence using root mean square energy
        rms = librosa.feature.rms(y=audio)[0]
        silence_threshold = np.mean(rms) * 0.5
        
        # Calculate pause ratio
        pauses = np.sum(rms < silence_threshold) / len(rms)
        
        # Analyze pause distribution
        pause_segments = np.where(rms < silence_threshold)[0]
        if len(pause_segments) > 1:
            pause_spacing = np.diff(pause_segments)
            spacing_score = min(100, max(0, 100 - np.std(pause_spacing) * 0.1))
        else:
            spacing_score = 50
        
        # Score based on appropriate pause ratio and distribution
        ratio_score = min(100, max(0, 100 - abs(pauses - 0.2) * 200))
        
        return np.mean([ratio_score, spacing_score])
    
    def analyze_confidence(self, audio: np.ndarray) -> float:
        """
        Analyze speaking confidence based on various metrics.
        
        Args:
            audio (np.ndarray): Audio data
            
        Returns:
            float: Confidence score (0-100)
        """
        # Analyze amplitude dynamics
        rms = librosa.feature.rms(y=audio)[0]
        amplitude_score = min(100, max(0, np.mean(rms) * 200 + 50))
        
        # Analyze speaking rate
        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=self.sample_rate)[0]
        tempo_score = min(100, max(0, 100 - abs(tempo - 120) * 0.5))
        
        return np.mean([amplitude_score, tempo_score])
    
    def analyze_voice(
        self,
        audio: Optional[np.ndarray] = None,
        duration: float = 5
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """
        Analyze voice and return detailed ratings.
        
        Args:
            audio (Optional[np.ndarray]): Pre-recorded audio data
            duration (float): Recording duration if no audio provided
            
        Returns:
            Dict containing parameters scores and overall score
        """
        if audio is None:
            audio = self.record_audio(duration)
        
        # Store audio for potential reanalysis
        self._last_audio = audio
        
        # Normalize audio
        audio = audio / (np.max(np.abs(audio)) + 1e-6)
        
        # Analyze individual parameters
        self.parameters['pitch'] = self.analyze_pitch(audio)
        self.parameters['tone'] = self.analyze_tone(audio)
        self.parameters['frequency_variation'] = self.analyze_frequency_variation(audio)
        self.parameters['pauses'] = self.analyze_pauses(audio)
        self.parameters['confidence'] = self.analyze_confidence(audio)
        
        # Calculate weighted overall score
        weighted_scores = [
            score * self.weights[param]
            for param, score in self.parameters.items()
        ]
        overall_score = np.sum(weighted_scores) / np.sum(list(self.weights.values()))
        
        return {
            'parameters': self.parameters,
            'overall_score': overall_score
        }
    
    def get_feedback(self) -> List[str]:
        """
        Generate detailed feedback based on the analysis results.
        
        Returns:
            List[str]: List of feedback statements
        """
        feedback = []
        
        # Detailed feedback for each parameter
        feedback_thresholds = {
            'pitch': {
                90: "Excellent pitch control with good variation",
                80: "Very good pitch control",
                70: "Good pitch control with room for improvement",
                60: "Acceptable pitch control, consider working on stability",
                0: "Focus on maintaining consistent pitch and appropriate variation"
            },
            'tone': {
                90: "Outstanding vocal tone with excellent resonance",
                80: "Very good tone quality",
                70: "Good tone with some areas for improvement",
                60: "Acceptable tone quality, consider voice exercises",
                0: "Work on improving vocal resonance and tone quality"
            },
            'frequency_variation': {
                90: "Excellent dynamic range and expression",
                80: "Very good speaking dynamics",
                70: "Good variation in speech",
                60: "Acceptable variation, could be more dynamic",
                0: "Try to add more variety to your speaking style"
            },
            'pauses': {
                90: "Excellent use of pauses and pacing",
                80: "Very good rhythm and timing",
                70: "Good use of pauses",
                60: "Acceptable pacing, could improve pause distribution",
                0: "Work on incorporating more natural pauses"
            },
            'confidence': {
                90: "Extremely confident delivery",
                80: "Very confident speaking style",
                70: "Good confidence level",
                60: "Acceptable confidence, room for improvement",
                0: "Focus on building speaking confidence"
            }
        }
        
        for param, score in self.parameters.items():
            for threshold, message in feedback_thresholds[param].items():
                if score >= threshold:
                    feedback.append(f"{message} ({score:.1f}/100)")
                    break
        
        return feedback

    def save_audio(self, filename: str) -> bool:
        """
        Save the last recorded/analyzed audio to a file.
        
        Args:
            filename (str): Output filename (should end with .wav)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self._last_audio is None:
            return False
        
        try:
            librosa.output.write_wav(
                filename,
                self._last_audio,
                self.sample_rate
            )
            return True
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False