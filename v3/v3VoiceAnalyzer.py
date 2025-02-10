import numpy as np
import librosa
import sounddevice as sd
import soundfile as sf
import threading
import datetime
import os
import speech_recognition as sr

class AudioRecorder:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []
        
    def start_recording(self):
        """Start recording audio"""
        self.recording = True
        self.audio_data = []
        
        def record():
            with sd.InputStream(samplerate=self.sample_rate, channels=1) as stream:
                while self.recording:
                    audio_chunk, _ = stream.read(self.sample_rate)
                    self.audio_data.extend(audio_chunk.flatten())
                    
        self.record_thread = threading.Thread(target=record)
        self.record_thread.start()
        
    def stop_recording(self):
        """Stop recording and save the audio file"""
        self.recording = False
        self.record_thread.join()
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        
        os.makedirs("recordings", exist_ok=True)
        filepath = os.path.join("recordings", filename)
        
        sf.write(filepath, np.array(self.audio_data), self.sample_rate)
        return filepath

class VoiceAnalyzer:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.recognizer = sr.Recognizer()
        self.filler_words = {
            'um', 'uh', 'ah', 'er', 'like', 'you know', 'sort of', 'kind of',
            'basically', 'literally', 'actually', 'so', 'well', 'i mean',
            'right', 'okay', 'hmm', 'mhm'
        }
        
    def transcribe_audio(self, audio_path):
        """Convert speech to text"""
        with sr.AudioFile(audio_path) as source:
            audio = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio)
                return text.lower()
            except sr.UnknownValueError:
                return "Speech recognition could not understand the audio"
            except sr.RequestError:
                return "Could not request results from speech recognition service"

    def analyze_filler_words(self, text):
        """Analyze the use of filler words in the text"""
        words = text.lower().split()
        total_words = len(words)
        filler_count = {}
        total_fillers = 0
        
        # Count individual filler words
        for word in words:
            if word in self.filler_words:
                filler_count[word] = filler_count.get(word, 0) + 1
                total_fillers += 1
        
        # Check for multi-word fillers
        text_lower = text.lower()
        for filler in self.filler_words:
            if ' ' in filler and filler in text_lower:
                count = text_lower.count(filler)
                filler_count[filler] = count
                total_fillers += count
        
        return {
            'total_words': total_words,
            'total_fillers': total_fillers,
            'filler_percentage': (total_fillers / total_words * 100) if total_words > 0 else 0,
            'filler_count': filler_count
        }
    
    def record_and_analyze(self):
        """Record audio and analyze voice characteristics"""
        print("Starting recording... Speak now!")
        self.recorder.start_recording()
        
        input("Press Enter to stop recording...")
        
        audio_path = self.recorder.stop_recording()
        print(f"Recording saved to: {audio_path}")
        
        # Transcribe speech
        transcribed_text = self.transcribe_audio(audio_path)
        
        # Analyze voice characteristics
        voice_analysis = self.analyze_voice(audio_path)
        
        # Analyze filler words
        filler_analysis = self.analyze_filler_words(transcribed_text)
        
        # Adjust confidence score based on filler word usage
        filler_penalty = min(filler_analysis['filler_percentage'] / 100, 0.3)  # Max 30% penalty
        adjusted_confidence = voice_analysis['confidence_score'] * (1 - filler_penalty)
        
        return {
            'voice_analysis': voice_analysis,
            'transcribed_text': transcribed_text,
            'filler_analysis': filler_analysis,
            'final_confidence_score': adjusted_confidence
        }, audio_path

    def analyze_voice(self, audio_path):
        """Analyze voice characteristics using librosa"""
        # Load audio file
        y, sr = librosa.load(audio_path)
        
        # Calculate various voice characteristics
        
        # 1. Pitch analysis
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_mean = np.mean(pitches[pitches > 0])
        pitch_std = np.std(pitches[pitches > 0])
        pitch_stability = 1.0 / (pitch_std + 1e-6)
        
        # 2. Volume/energy analysis
        rms = librosa.feature.rms(y=y)[0]
        energy_mean = np.mean(rms)
        energy_std = np.std(rms)
        energy_stability = 1.0 / (energy_std + 1e-6)
        
        # 3. Speaking rate
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        
        # 4. Voice clarity
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        clarity = 1.0 / (np.std(zcr) + 1e-6)
        
        # Calculate confidence score based on these metrics
        confidence_indicators = {
            'pitch_stability': min(pitch_stability / 100, 1.0),
            'energy_stability': min(energy_stability / 100, 1.0),
            'speech_power': min(energy_mean * 1000, 1.0),
            'voice_clarity': min(clarity / 100, 1.0),
            'speaking_pace': min(abs(tempo - 120) / 120, 1.0)
        }
        
        confidence_score = np.mean(list(confidence_indicators.values()))
        
        return {
            'confidence_score': confidence_score,
            'metrics': {
                'pitch_stability': pitch_stability,
                'volume_stability': energy_stability,
                'speaking_rate': tempo,
                'voice_clarity': clarity,
                'voice_power': energy_mean
            },
            'confidence_indicators': confidence_indicators
        }



# ### NEW CODE 
# import numpy as np
# import librosa
# import librosa.feature.rhythm as rhythm
# import sounddevice as sd
# import soundfile as sf
# import threading
# import datetime
# import os
# import speech_recognition as sr
# from scipy.signal import butter, filtfilt
# import noisereduce as nr

# class AudioProcessor:
#     def __init__(self):
#         self.sr = 44100  # Sample rate
        
#     def reduce_noise(self, audio_data, sr):
#         """Reduce background noise using spectral gating"""
#         # Use noisereduce to remove background noise
#         reduced_noise = nr.reduce_noise(
#             y=audio_data,
#             sr=sr,
#             prop_decrease=1.0,
#             stationary=True
#         )
#         return reduced_noise
    
#     def apply_bandpass_filter(self, audio_data, sr, lowcut=80, highcut=8000):
#         """Apply bandpass filter to focus on speech frequencies"""
#         nyquist = sr / 2
#         low = lowcut / nyquist
#         high = highcut / nyquist
#         order = 4
#         b, a = butter(order, [low, high], btype='band')
#         filtered_audio = filtfilt(b, a, audio_data)
#         return filtered_audio
    
#     def normalize_audio(self, audio_data):
#         """Normalize audio volume"""
#         max_amplitude = np.max(np.abs(audio_data))
#         if max_amplitude > 0:
#             normalized_audio = audio_data / max_amplitude
#             return normalized_audio
#         return audio_data
    
#     def trim_silence(self, audio_data, sr, threshold=20):
#         """Remove silence from beginning and end"""
#         trimmed_audio, _ = librosa.effects.trim(
#             audio_data, 
#             top_db=threshold,
#             frame_length=512,
#             hop_length=128
#         )
#         return trimmed_audio
    
#     def process_audio(self, audio_data, sr):
#         """Apply all audio processing steps"""
#         # 1. Reduce background noise
#         processed_audio = self.reduce_noise(audio_data, sr)
        
#         # 2. Apply bandpass filter for speech frequencies
#         processed_audio = self.apply_bandpass_filter(processed_audio, sr)
        
#         # 3. Normalize audio volume
#         processed_audio = self.normalize_audio(processed_audio)
        
#         # 4. Trim silence
#         processed_audio = self.trim_silence(processed_audio, sr)
        
#         return processed_audio

# class AudioRecorder:
#     def __init__(self, sample_rate=44100):
#         self.sample_rate = sample_rate
#         self.recording = False
#         self.audio_data = []
#         self.processor = AudioProcessor()
        
#     def start_recording(self):
#         """Start recording audio"""
#         self.recording = True
#         self.audio_data = []
        
#         def record():
#             with sd.InputStream(samplerate=self.sample_rate, channels=1) as stream:
#                 while self.recording:
#                     audio_chunk, _ = stream.read(self.sample_rate)
#                     self.audio_data.extend(audio_chunk.flatten())
                    
#         self.record_thread = threading.Thread(target=record)
#         self.record_thread.start()
        
#     def stop_recording(self):
#         """Stop recording and save the audio file"""
#         self.recording = False
#         self.record_thread.join()
        
#         # Process the recorded audio
#         processed_audio = self.processor.process_audio(
#             np.array(self.audio_data),
#             self.sample_rate
#         )
        
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
#         # Save both original and processed audio
#         os.makedirs("recordings", exist_ok=True)
        
#         # Save original audio
#         original_filepath = os.path.join("recordings", f"original_{timestamp}.wav")
#         sf.write(original_filepath, np.array(self.audio_data), self.sample_rate)
        
#         # Save processed audio
#         processed_filepath = os.path.join("recordings", f"processed_{timestamp}.wav")
#         sf.write(processed_filepath, processed_audio, self.sample_rate)
        
#         return processed_filepath, original_filepath

# class VoiceAnalyzer:
#     def __init__(self):
#         self.recorder = AudioRecorder()
#         self.recognizer = sr.Recognizer()
#         self.filler_words = {
#             'um', 'uh', 'ah', 'er', 'like', 'you know', 'sort of', 'kind of',
#             'basically', 'literally', 'actually', 'so', 'well', 'i mean',
#             'right', 'okay', 'hmm', 'mhm'
#         }
        
#     def transcribe_audio(self, audio_path):
#         """Convert speech to text"""
#         with sr.AudioFile(audio_path) as source:
#             audio = self.recognizer.record(source)
#             try:
#                 text = self.recognizer.recognize_google(audio)
#                 return text.lower()
#             except sr.UnknownValueError:
#                 return "Speech recognition could not understand the audio"
#             except sr.RequestError:
#                 return "Could not request results from speech recognition service"

#     def analyze_filler_words(self, text):
#         """Analyze the use of filler words in the text"""
#         words = text.lower().split()
#         total_words = len(words)
#         filler_count = {}
#         total_fillers = 0
        
#         # Count individual filler words
#         for word in words:
#             if word in self.filler_words:
#                 filler_count[word] = filler_count.get(word, 0) + 1
#                 total_fillers += 1
        
#         # Check for multi-word fillers
#         text_lower = text.lower()
#         for filler in self.filler_words:
#             if ' ' in filler and filler in text_lower:
#                 count = text_lower.count(filler)
#                 filler_count[filler] = count
#                 total_fillers += count
        
#         return {
#             'total_words': total_words,
#             'total_fillers': total_fillers,
#             'filler_percentage': (total_fillers / total_words * 100) if total_words > 0 else 0,
#             'filler_count': filler_count
#         }
    
#     def record_and_analyze(self):
#         """Record audio and analyze voice characteristics"""
#         print("Starting recording... Speak now!")
#         self.recorder.start_recording()
        
#         input("Press Enter to stop recording...")
        
#         processed_path, original_path = self.recorder.stop_recording()
#         print(f"Original recording saved to: {original_path}")
#         print(f"Processed recording saved to: {processed_path}")
        
#         # Transcribe speech using processed audio
#         transcribed_text = self.transcribe_audio(processed_path)
        
#         # Analyze voice characteristics
#         voice_analysis = self.analyze_voice(processed_path)
        
#         # Analyze filler words
#         filler_analysis = self.analyze_filler_words(transcribed_text)
        
#         # Adjust confidence score based on filler word usage
#         filler_penalty = min(filler_analysis['filler_percentage'] / 100, 0.3)
#         adjusted_confidence = voice_analysis['confidence_score'] * (1 - filler_penalty)
        
#         return {
#             'voice_analysis': voice_analysis,
#             'transcribed_text': transcribed_text,
#             'filler_analysis': filler_analysis,
#             'final_confidence_score': adjusted_confidence,
#             'original_audio': original_path,
#             'processed_audio': processed_path
#         }

#     def analyze_voice(self, audio_path):
#         """Analyze voice characteristics using librosa"""
#         # Load audio file
#         y, sr = librosa.load(audio_path)
        
#         # Calculate various voice characteristics
#         pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
#         pitch_mean = np.mean(pitches[pitches > 0])
#         pitch_std = np.std(pitches[pitches > 0])
#         pitch_stability = 1.0 / (pitch_std + 1e-6)
        
#         rms = librosa.feature.rms(y=y)[0]
#         energy_mean = np.mean(rms)
#         energy_std = np.std(rms)
#         energy_stability = 1.0 / (energy_std + 1e-6)
        
#         onset_env = librosa.onset.onset_strength(y=y, sr=sr)
#         tempo = rhythm.tempo(onset_envelope=onset_env, sr=sr)[0]  # Corrected line
        
#         zcr = librosa.feature.zero_crossing_rate(y)[0]
#         clarity = 1.0 / (np.std(zcr) + 1e-6)
        
#         confidence_indicators = {
#             'pitch_stability': min(pitch_stability / 100, 1.0),
#             'energy_stability': min(energy_stability / 100, 1.0),
#             'speech_power': min(energy_mean * 1000, 1.0),
#             'voice_clarity': min(clarity / 100, 1.0),
#             'speaking_pace': min(abs(tempo - 120) / 120, 1.0)
#         }
        
#         confidence_score = np.mean(list(confidence_indicators.values()))
        
#         return {
#             'confidence_score': confidence_score,
#             'metrics': {
#                 'pitch_stability': pitch_stability,
#                 'volume_stability': energy_stability,
#                 'speaking_rate': tempo,
#                 'voice_clarity': clarity,
#                 'voice_power': energy_mean
#             },
#             'confidence_indicators': confidence_indicators
#         }
    


# ### 